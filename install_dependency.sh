#!/bin/bash
dir=/usr/local/huami/python2.7
pip2 install virtualenv
virtualenv ${dir}/env
source ${dir}/env/bin/activate
pip install -r requirements.txt