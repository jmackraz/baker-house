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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Pyramid WSGI app initialization

from pyramid.config import Configurator

def create_wsgi_app(**settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.include('cornice_swagger')
    config.scan("house_hub")
    return config.make_wsgi_app()



devices = Service(name='devices', path='/devices', description="Discovery")
@devices.get()
def get_devices(request):
    log.debug("get_devices")
    return {'devices': ['receiver', 'tv']}

receiver = Service(name='receiver', path='/receiver', description="The one and only receiver")
@receiver.get()
def get_receiver(request):
    log.debug("get_receiver")
    return {'name': 'family room receiver',
            'model': 'Integra blah blah',
            }



# Base class and mock for an AV device remote control

class MockControlSchema(colander.MappingSchema):
    knob1 = colander.SchemaNode(colander.Int(), name="knob1", missing=colander.drop)
    knob2 = colander.SchemaNode(colander.Int(), name="knob2",  missing=colander.drop)


@resource(accept="text/json", path='/receiver/mock-control', schema=MockControlSchema(), validators=(colander_body_validator,), description="mock controls" )
class RemoteControl:
    _CONTROL={'sucks': True}

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
        self._CONTROL['last-modify'] = datestring

    def _last_modify_time():
        return self._CONTROL['last-modify']

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
    input_node = colander.SchemaNode(colander.String(), name="input", missing=colander.drop)
    volume = colander.SchemaNode(colander.Int(), missing=colander.drop)

@resource(accept="text/json", path='/receiver/control', schema=ReceiverControlSchema(), validators=(colander_body_validator,), description="audio controls" )
class OnkyoRemoteControl(RemoteControl):
    # don't blow out the volume
    VOLUME_LEVEL_CAP=50

    def __init__(self, request, context = None):
        super().__init__(request,context)

    # override 
    def refresh(self):
        """update local copy of device control settings, from hardware"""
        log.info("onkyo refresh (stubbed)")
        fresh_values = {'input': 'directv', 'volume': 59}    # stub
        changes_made = False
        for knob in ['input', 'volume']:
            if knob in fresh_values and fresh_values[knob] != RemoteControl._CONTROL.get(knob):
                changes_made = True

        if changes_made:
            RemoteControl._CONTROL={'input': 'directv', 'volume': 59}
            self._update_last_modify_time()

    # override 
    def update(self, knobs ):
        """control an onkyo/integra AV receive"""
        log.info("update of onkyo/integra receiver")
        if 'input' in knobs:
            log.info("stub set receiver input to: %s", knobs['input'])

        if 'volume' in knobs:
            capped_level = min(knobs['volume'], self.VOLUME_LEVEL_CAP)
            log.info("stub set receiver volume to: %s (capped, requested: %s)", capped_level, knobs['volume'])
            knobs['volume'] = capped_level

        # update our copy
        if len(knobs) > 0:
            self._CONTROL.update(knobs)
            self._update_last_modify_time()     # merge dn the validated changes



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
    serve(create_wsgi_app(), listen='*:6543')
