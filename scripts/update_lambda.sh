# update lambda function on server
#!/bin/bash

DIR="$(dirname $0)"
python_file="$DIR/../src/new_house_lambda.py"
#python_file="$DIR/../src/house_lambda.py"
zip_file="/tmp/tmp_lambda.zip"
lambda_name=$BAKERHOUSE_LAMBDA

# BUG! "--no-dry-run" does not work!
dry_run=""
#dry_run="--dry-run"

echo publishing $python_file

# -j means "junk (omit) the path
zip -j $zip_file $python_file

#aws lambda update-function-code --function-name $lambda_name --zip-file  fileb://$zip_file --no-publish $dry_run
cmd="aws lambda update-function-code --function-name $lambda_name --zip-file  fileb://$zip_file --no-publish $dry_run"
echo CMD: $cmd
$cmd

