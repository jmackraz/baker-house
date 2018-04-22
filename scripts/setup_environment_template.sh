# source this file to set up private values in the environment
# DO NOT CHECK THIS FILE INTO SOURCE CONTROL

# TEMPLATE: Fill in your personal values.

# determines which AWS credentials will be used by AWS CLI and boto3 library scripts
export AWS_PROFILE="default"

# AWS IoT Thing name
export BAKERHOUSE_IOT_THING="NOT_SET"
# AWS IoT Thing type
export BAKERHOUSE_IOT_THING_TYPE="${BAKERHOUSE_IOT_THING}_type"
# AWS IoT Thing ARN
export BAKERHOUSE_IOT_THING_ARN="NOT_SET"

# AWS IoT Certificates

certdir=$PWD/certs

# Path to root certificate file
export BAKERHOUSE_ROOTCERT_FILE="$certdir/rootcert.pem"
# Path to my x.509 cert for aws iot
export BAKERHOUSE_MYCERT_FILE="$certdir/certificate.pem.crt"
# Path to my private key file"
export BAKERHOUSE_PRIVATEKEY_FILE="$certdir/private.pem.key"

# AWS IoT endpoint
export BAKERHOUSE_ENDPOINT="NOT_SET"

# ARN of Lambda
export BAKERHOUSE_LAMBDA="NOT_SET"
