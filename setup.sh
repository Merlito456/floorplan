#!/bin/bash
# Install Python 3.11
apt-get update
apt-get install -y python3.11 python3.11-distutils python3.11-dev
update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install requirements
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt