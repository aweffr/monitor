#!/bin/bash
pip2 install virtualenv
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt