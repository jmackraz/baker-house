# start iot handler
#


DIR="$(dirname $0)"
python $DIR/../src/house_iot.py -e $BAKERHOUSE_ENDPOINT -r $BAKERHOUSE_ROOTCERT_FILE -c $BAKERHOUSE_MYCERT_FILE -k $BAKERHOUSE_PRIVATEKEY_FILE --mode subscribe
