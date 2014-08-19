#!/bin/bash
set -e

# global vars
DEFAULT_S3_LIB="s3://verve-opsdata/lib"
DEFAULT_BOTO_VERSION="boto-2.5.2"
DOWNLOADS="$HOME/verve/downloads"
PYTHONPATH="$HOME/verve/code/lib/python"


# cmd line args
PYTHON_S3_SRC=$1
S3_LIB=${2:-$DEFAULT_S3_LIB}
BOTO_VERSION=${3:-$DEFAULT_BOTO_VERSION}


# code
mkdir -p $DOWNLOADS
cd $DOWNLOADS
hadoop fs -copyToLocal $S3_LIB/${BOTO_VERSION}.tar.gz ${BOTO_VERSION}.tar.gz
tar -xvzf ${BOTO_VERSION}.tar.gz
cd ${BOTO_VERSION}
sudo python setup.py install

mkdir -p $PYTHONPATH
hadoop fs -copyToLocal $PYTHON_S3_SRC/* $PYTHONPATH
echo "export PYTHONPATH=$PYTHONPATH" >> ~/.bashrc
source ~/.bashrc

# TODO: remove external dependency
sudo apt-get install python-pip
sudo pip install argparse

