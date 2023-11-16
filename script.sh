#!/bin/bash
git clone https://github.com/aws-samples/serverless-samples.git
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel
wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
sudo tar xzf Python-3.9.16.tgz
cd Python-3.9.16
sudo ./configure --enable-optimizations
sudo make altinstall
cd ..
# cd serverless-samples/
# sam build && sam deploy
# y