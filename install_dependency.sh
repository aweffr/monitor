#!/bin/bash
dir=/usr/local/huami/python2.7
pip2 install virtualenv
virtualenv ${dir}/env
${dir}/env/bin/pip install -r requirements.txt