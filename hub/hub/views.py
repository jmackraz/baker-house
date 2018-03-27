""" Cornice services.
"""
from cornice import Service


hello = Service(name='hello', path='/', description="Simplest app")

_VALUE = {'Hello': 'World'}


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return _VALUE

@hello.put()
def put_info(request):
    """messing around"""
    try:
        # json_body is JSON-decoded variant of the request body
        _VALUE = request.json_body
    except ValueError:
        return False
    return True


devices = Service(name='devices', path='/devices', description="Discovery")

@devices.get()
def get_devices(request):
    return {'devices': ['receiver', 'tv']}

receiver = Service(name='receiver', path='/receiver', description="The one and only receiver")

@receiver.get()
def get_receiver(request):
    return {'name': 'family room receiver',
            'model': 'Integra blah blah',
            'control': {'input': 'directv', 'volume': 40}
            }

receiver_ctl = Service(name='receiver_ctl', path='/receiver/control', description="The one and only receiver")

@receiver_ctl.get()
def get_receiver_ctl(request):
    return {'input': 'directv', 'volume': 40}

@receiver_ctl.put()
def put_receiver_ctl(request):
    """control recevier"""
    control_delta = request.json_body
    try:
        # json_body is JSON-decoded variant of the request body
        control_delta = request.json_body
    except ValueError:
        return False
    return control_delta

