#!/bin/bash
set -e

S3_BASE="s3://verve-opsdata"
S3_LIB="$S3_BASE/lib"

base="/home/hadoop/verve"

downloads="$base/downloads"
mkdir -p $downloads

s3_py_base="$S3_LIB/python"


cd $downloads

# boto
# TODO: update version
d="boto-2.5.2"
f="$d.tar.gz"
hadoop fs -copyToLocal $s3_py_base/$f $f
tar -xzf $f
cd $d
sudo python setup.py install
cd ..

# argparse
d="argparse-1.2.1"
f="$d.tar.gz"
hadoop fs -copyToLocal $s3_py_base/$f $f
tar -xzf $f
cd $d
sudo python setup.py install
cd ..

# MySQLdb
# sudo apt-get install libmysqlclient-dev
arch=`dpkg --print-architecture`
f=libmysqlclient-dev_5.1.66-0+squeeze1_$arch.deb
hadoop fs -copyToLocal $s3_py_base/$f $f
sudo dpkg -i $f
d="MySQL-python-1.2.3"
f="$d.tar.gz"
hadoop fs -copyToLocal $s3_py_base/$f $f
tar -xzf $f
cd $d
sudo python setup.py install
cd ..

