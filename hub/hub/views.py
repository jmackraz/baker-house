""" Cornice services.
"""
import logging

from cornice import Service
from cornice.resource import resource

log = logging.getLogger(__name__)


log.debug("service starting")

hello = Service(name='hello', path='/', description="Simplest app")

_VALUE = {'Hello': 'World'}


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return _VALUE

@hello.put()
def put_info(request):
    """messing around"""
    global _VALUE
    try:
        # json_body is JSON-decoded variant of the request body
        log.debug("_VALUE before %s", _VALUE)
        _VALUE = request.json_body
    except ValueError:
        return False
    return True


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

#receiver_ctl = Service(name='receiver_ctl', path='/receiver/control', description="The one and only receiver")

_CONTROL={'input': 'directv', 'volume': 40}

@resource(path='/receiver/control')
class ReceiverControl:
    def __init__(self, request, context = None):
        log.debug("ReceiverControl init()")
        self.request = request

    def __acl__(self):
        return [(Allow, Everyone, 'everything')]

    def get(self):
        log.debug("get_receiver_ctl")
        return _CONTROL

    def put(self):
        """control recevier"""
        log.debug("put_receiver_ctl")
        global _CONTROL
        control_delta = self.request.json_body
        _CONTROL.update(control_delta)
        return _CONTROL

