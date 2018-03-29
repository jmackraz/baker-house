# test using swagger
#
from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

http_client = RequestsClient()
http_client.set_basic_auth(
    'localhost:6543',
    'username', 'password'
)

client = SwaggerClient.from_url(
    'http://localhost:6543/__api__',
    http_client=http_client,
    config={'use_models': False}
)

print(dir(client.receiver.get_receiver()))

receiver = client.receiver.get_receiver().result()
print(receiver)
#print(receiver.model)
