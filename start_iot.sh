# start iot handler

certdir="$HOME/p/awsdev/awsiot/certs"

ENDPOINT="a3vkf37pujp1kg.iot.us-east-1.amazonaws.com"
#ROOTCERT="$certdir/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem"
ROOTCERT="$certdir/rootcert.pem"
MYCERT="$certdir/8dc9019edf-certificate.pem.crt"
PRIVATEKEY="$certdir/8dc9019edf-private.pem.key"

python my_test_sub.py -e $ENDPOINT -r $ROOTCERT -c $MYCERT -k $PRIVATEKEY --mode subscribe
