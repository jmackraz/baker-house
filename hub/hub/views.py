""" Cornice services.
"""
import logging
import datetime

import colander

from cornice import Service
from cornice.resource import resource
from cornice.validators import colander_body_validator

from cornice.validators import extract_cstruct

log = logging.getLogger(__name__)

hello = Service(name='hello', path='/', description="Simplest app")

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
            'control': {'input': 'directv', 'volume': 40}
            }


_CONTROL={'input': 'directv', 'volume': 40}

# don't blow out the volume
VOLUME_LEVEL_CAP=50

# ZZZ: use this in a last-modified response header,
# so iot can selectively update the device shadow
#
_last_modify_time = datetime.utc()
def _update_last_modify_time():
    global _last_modify_time
    _last_modify_time = datetime.utc()


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

@resource(accept="text/json", path='/receiver/control', schema=ControlSchema(), validators=(colander_body_validator,) )
class ReceiverControl:
    def __init__(self, request, context = None):
        #log.debug("ReceiverControl init()")
        self.request = request

    def get(self):
        log.debug("get_receiver_ctl")
        return _CONTROL

    def put(self):
        """control recevier"""
        log.debug("put_receiver_ctl")

        knobs = self.request.validated
        _update_receiver(knobs)

        return _CONTROL

