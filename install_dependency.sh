#!/bin/bash
pip2 install virtualenv
virtualenv env
source ./env/Scripts/activate
pip install -r requirements.txt