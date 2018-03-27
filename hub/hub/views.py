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

log = logging.getLogger(__name__)

hello = Service(name='hello', path='/hello', description="Simplest app")

@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return  {'message': 'Baker Home REST API'}

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
            'control': _CONTROL
            }

    
_CONTROL={'input': 'directv', 'volume': 40, 'last-modify': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}


# ZZZ: use this in a last-modified response header,
# so iot can selectively update the device shadow
#
def _update_last_modify_time():
    datestring = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    _CONTROL['last-modify'] = datestring

def _last_modify_time():
    return _CONTROL['last-modify']


# don't blow out the volume
VOLUME_LEVEL_CAP=50

def _update_receiver( knobs ):
    """adjust the receiver by remote control"""
    if 'input' in knobs:
        log.info("set receiver input to: %s", knobs['input'])

    if 'volume' in knobs:
        capped_level = min(knobs['volume'], VOLUME_LEVEL_CAP)
        log.info("set receiver volume to: %s (capped, requested: %s)", capped_level, knobs['volume'])
        knobs['volume'] = capped_level

    global _CONTROL

    if len(knobs) > 0:
        _update_last_modify_time()
        _CONTROL.update(knobs)


class ControlSchema(colander.MappingSchema):
    input_node = colander.SchemaNode(colander.String(), name="input", missing=colander.drop)
    volume = colander.SchemaNode(colander.Int(), missing=colander.drop)

@resource(accept="text/json", path='/receiver/control', schema=ControlSchema(), validators=(colander_body_validator,), description="audio controls" )
class ReceiverControl:
    def __init__(self, request, context = None):
        #log.debug("ReceiverControl init()")
        self.request = request

    def get(self):
        """get receiver state"""
        log.debug("get_receiver_ctl")
        log.debug("_last_modify_time: %s", _last_modify_time())
        return _CONTROL

    def put(self):
        """control receiver"""
        log.debug("put_receiver_ctl")

        knobs = self.request.validated
        _update_receiver(knobs)

        log.debug("_last_modify_time: %s", _last_modify_time())
        return _CONTROL


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
