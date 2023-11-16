#!/bin/bash
wget https://github.com/andrevinicius201/soap-serverless/archive/main.zip
unzip main.zip
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel
wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
sudo tar xzf Python-3.9.16.tgz
cd Python-3.9.16
sudo ./configure --enable-optimizations
sudo make altinstall
cd ..
cd soap-serverless-main/
sam build
sam deploy --no-confirm-changeset
