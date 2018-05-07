# source this file to set up private values in the environment
# DO NOT CHECK THIS FILE INTO SOURCE CONTROL

# TEMPLATE: Set personal values for your configuration

# ### DEVELOPMENT-TIME VARIABLES ### #

# AWS and ASK profiles
# profile to be used by AWS CLI, boto3 library scripts
export AWS_PROFILE="default"
# profile to be used by ASK CLI
export ASK_DEFAULT_PROFILE="default"   

# ### RUN-TIME VARIABLES ### #

# AWS IoT Thing name.
# Your choice.
export BAKERHOUSE_IOT_THING="BakerHouseThing1"

# AWS IoT endpoint.
# This is REQUIRED for the IoT client to connect to AWS IoT
#
# You can get this value from the AWS IoT console, in the
# "Interact" page of your Thing configuration.
#
# You can also run scripts/configure_aws_iot.py
# to emit the value and paste it here.
export BAKERHOUSE_ENDPOINT="NOT SET"

# endpoints for profiles, if you have more than one.
# leave BAKERHOUSE_ENDPOINT set to "NOT SET" or it will be used
#
export BAKERHOUSE_ENDPOINT_default="NOT SET YET"
export BAKERHOUSE_ENDPOINT_other-profile="NOT SET YET"

# AWS IoT Certificates
# Each created thing has its own certs subdirectory
#
# OK to leave these as they are.
#
certdir=$PWD/certs/"$AWS_PROFILE"/"$BAKERHOUSE_IOT_THING"
# Path to root certificate file
export BAKERHOUSE_ROOTCERT_FILE="$certdir/rootcert.pem"
# Path to my x.509 cert for aws iot
export BAKERHOUSE_MYCERT_FILE="$certdir/certificate.pem.crt"
# Path to my private key file"
export BAKERHOUSE_PRIVATEKEY_FILE="$certdir/private.pem.key"
# Path to my public key file"
export BAKERHOUSE_PUBLICKEY_FILE="$certdir/public.pem.key"

# ### CONFIG-TIME VARIABLES ### #

# OK to leave these as they are
export BAKERHOUSE_IOT_THING_TYPE="${BAKERHOUSE_IOT_THING}_type"
export BAKERHOUSE_IOT_THING_POLICY="${BAKERHOUSE_IOT_THING}_policy"
