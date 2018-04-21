#!/usr/bin/env python
""" Cornice services.
"""
import logging
from datetime import datetime
import locale

import colander
from cornice import Service
from cornice.resource import resource
from cornice.validators import colander_body_validator
from cornice.service import get_services
from cornice_swagger import CorniceSwagger
from waitress import serve

import eiscp

log = logging.getLogger(__name__)
# inherit root
#log.setLevel(logging.INFO)

# Pyramid WSGI app initialization

from pyramid.config import Configurator

def create_wsgi_app(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.include('cornice_swagger')
    config.scan("house_hub")
    return config.make_wsgi_app()



devices = Service(name='devices', path='/devices', description="Discovery")
@devices.get()
def get_devices(request):
    """discovery stub. not used."""
    log.info("get_devices")
    return {'devices': ['receiver', 'tv']}

receiver = Service(name='receiver', path='/receiver', description="The one and only receiver")
@receiver.get()
def get_receiver(request):
    """stub. could use eiscp discovery, if I ever control more than one receiver"""
    log.info("get_receiver")
    return {'name': 'family room receiver',
            'model': 'Integra blah blah',
            }


# Base class and mock for an AV device remote control

class MockControlSchema(colander.MappingSchema):
    knob1 = colander.SchemaNode(colander.Int(), name="knob1", missing=colander.drop)
    knob2 = colander.SchemaNode(colander.Int(), name="knob2",  missing=colander.drop)


@resource(accept="text/json", path='/receiver/mock-control', schema=MockControlSchema(), validators=(colander_body_validator,), description="mock controls" )
class RemoteControl:
    _CONTROL={}

    # override me
    def update(self, knobs ):
        """mock implementation of the interface to some AV-like device"""
        log.info("mock update of remote device")

    # override me
    def refresh(self):
        """update local copy of device control settings, from hardware"""
        log.info("mock refresh (no-op)")


    def _update_last_modify_time(self):
        datestring = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self._CONTROL['hub-last-modify'] = datestring

    def _last_modify_time():
        return self._CONTROL['hub-last-modify']

    def __init__(self, request, context = None):
        #log.debug("ReceiverControl init()")
        self.request = request

    def get(self):
        """REST method: get receiver state"""
        log.debug("get")
        self.refresh()                          # get fresh read from device
        return self._CONTROL

    def put(self):
        """REST method: control receiver"""
        log.debug("put")

        knobs = self.request.validated
        self.update(knobs)                  # affect the device

        return self._CONTROL


# Onkyo/Integra remote control
# so iot can selectively update the device shadow


class ReceiverControlSchema(colander.MappingSchema):
    """definition of REST control payload"""
    input_node = colander.SchemaNode(colander.String(), name="input", missing=colander.drop)
    volume = colander.SchemaNode(colander.Int(), missing=colander.drop)

@resource(accept="text/json", path='/receiver/control', schema=ReceiverControlSchema(), validators=(colander_body_validator,), description="audio controls" )
class OnkyoRemoteControl:

    _CONTROL=None

    # don't blow out my speakers
    VOLUME_LEVEL_CAP=65

    def __init__(self, request, context = None):
        log.debug("OnkyoRemoteControl __init__")

        self.request = request

        # discover receiver(s), use first found
        # (can use model number, id string, etc.)
        # ZZZ: cache IP address to save discovery delay

        timeout=1
        receivers = eiscp.eISCP.discover(timeout=timeout)
        if receivers:
            self.receiver =  receivers[0]
        else:
            log.warn("no receivers found. timeout was:", timeout)
            self.receiver = None

        # initialize with fake values
        if not self._CONTROL:
            log.debug("initialize _CONTROL")
            self._CONTROL={'input': 'none', 'volume': 0}

        # get current values from hardware
        self.refresh()


    def get(self):
        """REST method: get receiver state"""
        log.debug("GET")
        self.refresh()                          # get fresh read from device
        return self._CONTROL

    def put(self):
        """REST method: control receiver"""
        log.debug("PUT")

        # clean up input payload, according to schema
        knobs = self.request.validated

        if self.receiver is None:
            log.warn("put: no receiver found")
            return

        if 'input' in knobs:
            log.info("stub set receiver input to: %s", knobs['input'])
            response = self.receiver.command('input-selector', [knobs['input']], zone='main')
            self._update_from_response(response)

        if 'volume' in knobs:
            capped_level = min(knobs['volume'], self.VOLUME_LEVEL_CAP)
            log.info("stub set receiver volume to: %s (capped, requested: %s)", capped_level, knobs['volume'])
            response = self.receiver.command('input-selector', [capped_level], zone='main')
            self._update_from_response(response)
        return self._CONTROL


    def refresh(self):
        """update local copy of device control settings, from hardware"""

        if self.receiver is None:
            log.warn("refresh: no receiver found")
            return

        #log.debug("onkyo refresh, receiver:", self.receiver.info['model-name'] )
        log.info("onkyo refresh, receiver:", self.receiver.info )

        # query for current values and remember them
        response = self.receiver.command('input-selector', ['query'], zone='main')
        self._update_from_response(response)

        response = self.receiver.command('master-volume', ['query'], zone='main')
        self._update_from_response(response)

    def _update_last_modify_time(self):
        datestring = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        self._CONTROL['hub-last-modify'] = datestring

    def _last_modify_time():
        return self._CONTROL['hub-last-modify']

    def _update_from_response(self, response):
        """record values found in loosely-coupled responses from receiver"""
        log.debug("_update_from_response: %s", response)

        # eiscp response from receiver is not quite a dict, eg: ('input-selector', ('video2', 'cbl', 'sat')) 
        # convert it to dict using neat trick
        it = iter(response)
        msg = dict(zip(it,it))

        log.debug("_update msg: %s", msg)

        if 'input-selector' in msg:
            log.debug("current _CONTROL: %s", self._CONTROL)
            #if self._CONTROL['input'] != msg['input-selector']:
            if self._CONTROL['input'] != "fizzbin":
                log.debug("msg: %s", msg)
                log.info("recording input as: %s", str(msg['input-selector']))
                self._CONTROL['input'] = msg['input-selector']
                self._update_last_modify_time()

        if 'master-volume' in msg:
            if self._CONTROL['volume'] != msg['master-volume']:
                log.info("recording volume as: %s", msg['master-volume'])
                self._CONTROL['volume'] = msg['master-volume']
                self._update_last_modify_time()


# Create a service to serve our OpenAPI spec
swagger = Service(name='OpenAPI',
                  path='/__api__',
                  description="OpenAPI documentation")


@swagger.get()
def openAPI_spec(request):
    doc = CorniceSwagger(get_services())
    doc.summary_docstrings = True
    my_spec = doc.generate('MyAPI', '1.0.0')
    return my_spec

# run this baby
if __name__ == "__main__":
    # execute only if run as a script
    #
    logging.getLogger('waitress').setLevel(logging.DEBUG)
    serve(create_wsgi_app(None), listen='*:6543')
