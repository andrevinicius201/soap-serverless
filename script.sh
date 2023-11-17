#!/bin/bash
echo Please enter the REST API endpoint. Optionally, you can leave it blank and set it later in the xslt-transformer lambda function
read endpoint

if [ -z "$endpoint" ]; then
  echo "No endpoint was set at this moment"
else
  echo The solution will be able to invoke this REST endpoint: $endpoint
fi
git clone https://github.com/andrevinicius201/soap-serverless.git
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel
wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
sudo tar xzf Python-3.9.16.tgz
cd Python-3.9.16
sudo ./configure --enable-optimizations
sudo make altinstall
cd ..
cd soap-serverless/
sam build
sam deploy --no-confirm-changeset
if [ -z "$endpoint" ]; then
  echo "Setup is complete"
else
    env_vars_key_value_upsert=(
    "endpoint" $endpoint
    )
    existing_env_vars=$(aws lambda get-function-configuration \
        --function-name funcao-mavi \
        --query 'Environment.Variables' \
        --output json)
    updated_env_vars="$existing_env_vars"
    for ((i = 0; i < ${#env_vars_key_value_upsert[@]}; i+=2)); do
    updated_env_vars=$(echo "$updated_env_vars" \
        | jq --arg key "${env_vars_key_value_upsert[$i]}" --arg value "${env_vars_key_value_upsert[$i + 1]}" \
        '.[$key] = $value')
    done
    aws lambda update-function-configuration \
        --function-name funcao-mavi \
        --environment "{\"Variables\": $updated_env_vars}"
fi

ACC_ID=$(aws sts get-caller-identity | jq -r '.Account')
aws s3 cp ./xslt s3://soap-transformer-$ACC_ID/xslt --recursive
