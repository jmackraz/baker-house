# update lambda function on server
#!/bin/bash

python_file="house-lambda.py"
zip_file="lambda.zip"
lambda_name="arn:aws:lambda:us-east-1:223828777169:function:onkyo-test"
lambda_name=$BAKERHOUSE_LAMBDA
dry_run="--no-dry-run"

echo publishing $python_file

zip $zip_file $python_file

aws lambda update-function-code --function-name $lambda_name --zip-file  fileb://$zip_file --no-publish $dry_run

