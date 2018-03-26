#!/bin/bash
# start hub REST server
#

interface="192.168.1.135:8000"
wsgi_app="sample:api"
gunicorn --log-level debug -b $interface $wsgi_app

