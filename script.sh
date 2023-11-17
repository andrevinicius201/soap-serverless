#!/bin/bash
echo Please enter the REST API endpoint. Optionally, you can leave it blank and set it later in the xslt-transformer lambda function
read varname

if [ -z "$varname" ]; then
  echo "No endpoint was set at this moment"
else
  echo The solution will be able to invoke this REST endpoint: $varname
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
sam build && sam deploy
if [ -z "$varname" ]; then
  echo "Setup is complete"
else
    aws lambda update-function-configuration \
        --function-name  xslt-transformer \
        --environment Variables={KEY1=$varname} \
        > output.txt
  echo Setup complete
fi
