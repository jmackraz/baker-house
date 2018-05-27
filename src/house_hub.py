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


class ReceiverControlSchema(colander.MappingSchema):
    """definition of REST control payload"""
    input_node = colander.SchemaNode(colander.String(), name="input", missing=colander.drop)
    volume = colander.SchemaNode(colander.Int(), missing=colander.drop)

_CONTROL=None
_RECEIVER_IP=None

@resource(accept="text/json", path='/receiver/control', schema=ReceiverControlSchema(), validators=(colander_body_validator,), description="audio controls" )
class OnkyoRemoteControl:

    input_aliases = (
        ('directv', 'sat'),
        ('sonos', 'cd'),
        ('fire tv', 'strm-box')
    )

    def selection_alias(self, val):
        for alias_pair in self.input_aliases:
            if val == alias_pair[0]:
                return alias_pair[1]
        return val

    def response_alias(self, val):
        for alias_pair in self.input_aliases:
            if alias_pair[1] in val:
                return alias_pair[0]
        return val



    # don't blow out my speakers
    VOLUME_LEVEL_CAP=65

    def __init__(self, request, context = None):
        log.debug("OnkyoRemoteControl __init__")

        self.request = request

        # discover receiver(s), use first found
        # (can use model number, id string, etc.)
        # ZZZ: cache IP address to save discovery delay

        global _RECEIVER_IP

        if _RECEIVER_IP:
            log.debug("check cached IP")
            receiver = eiscp.eISCP(_RECEIVER_IP)

            if receiver is None or receiver.info is None or 'unknown' in receiver.info:
                # re-discover
                log.debug("cached IP didn't work, re-discover")
                _RECEIVER_IP = None

        if not _RECEIVER_IP:
            log.debug("discover receiver")
            timeout=1
            receivers = eiscp.eISCP.discover(timeout=timeout)
            if receivers:
                _RECEIVER_IP = receivers[0].host
                log.debug("receiver discovered at: %s", _RECEIVER_IP)
            else:
                log.warn("no receivers found. timeout was: %s", timeout)

        # initialize with fake values
        global _CONTROL
        if not _CONTROL:
            log.debug("initialize _CONTROL")
            _CONTROL={'input': 'none', 'volume': 0}
            # get current values from hardware
            self.refresh()


    def get(self):
        """REST method: get receiver state"""
        log.debug("GET")
        self.refresh()                          # read fresh state from hardware
        return _CONTROL

    def put(self):
        """REST method: control receiver"""
        log.info("PUT")

        # clean up input payload, according to schema
        knobs = self.request.validated


        with eiscp.eISCP(_RECEIVER_IP) as receiver:

            # times out if not on
            if 'volume' in knobs:
                if self.is_power_on(receiver):
                    capped_level = min(knobs['volume'], self.VOLUME_LEVEL_CAP)
                    log.info("set receiver volume to: %s (capped, requested: %s)", capped_level, knobs['volume'])
                    response = receiver.command('master-volume', [str(capped_level)], zone='main')
                    self._update_from_response(response)
                else:
                    log.info("receiver not powered on, volume setting ignored")

            # does not time out; powers up
            if 'input' in knobs:
                log.info("set receiver input to: %s", knobs['input'])

                # low-tech aliasing
                knobs['input'] = self.selection_alias(knobs['input'])

                #if knobs['input'] == 'sonos':
                #    knobs['input'] = 'cd'
                #elif knobs['input'] == "directv":
                #    knobs['input'] = "sat"

                response = receiver.command('input-selector', [knobs['input']], zone='main')
                self._update_from_response(response)

        return _CONTROL

    def is_power_on(self, receiver):
        response = receiver.command('system-power', ['query'], zone='main')
        return response[0] == 'system-power' and response[1] == 'on'


    def refresh(self):
        """update local copy of device control settings, from hardware"""

        with eiscp.eISCP(_RECEIVER_IP) as receiver:
            log.debug("onkyo refresh, receiver: %s", receiver.info )

            # query for current values and remember them
            response = receiver.command('input-selector', ['query'], zone='main')
            self._update_from_response(response)

            response = receiver.command('master-volume', ['query'], zone='main')
            self._update_from_response(response)

    def _update_last_modify_time(self):
        datestring = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        _CONTROL['hub-last-modify'] = datestring

    def _last_modify_time():
        return _CONTROL['hub-last-modify']

    def _update_from_response(self, response):
        """record values found in loosely-coupled responses from receiver"""
        log.debug("_update_from_response: %s", response)

        # eiscp response from receiver is not quite a dict, eg: ('input-selector', ('video2', 'cbl', 'sat')) 
        # convert it to dict using neat trick
        it = iter(response)
        msg = dict(zip(it,it))

        if 'input-selector' in msg:
            log.debug("current _CONTROL: %s", _CONTROL)
            input_source = self.response_alias(msg['input-selector'])


            if _CONTROL['input'] != input_source:
                log.debug("msg: %s", msg)
                log.info("remembering input as: %s", str(input_source))
                _CONTROL['input'] = input_source
                self._update_last_modify_time()

        if 'master-volume' in msg:
            if _CONTROL['volume'] != msg['master-volume']:
                log.info("remembering volume as: %s", msg['master-volume'])
                _CONTROL['volume'] = msg['master-volume']
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
    logging.getLogger('waitress').setLevel(logging.INFO)
    serve(create_wsgi_app(None), listen='*:6543')
