#!/bin/bash

#VER=`readlink -f ${BASH_SOURCE[0]} | sed -e 's/.*releases\///' -e 's/\/.*//'`
#S3_CODE="s3://verve-opsdata/code/etl/$VER"
S3_CODE=$1
S3_LIB="s3://verve-opsdata/lib"

basedir='~/verve'
download=$basedir/download

# from etl/deploy/store_vault.sh
pass='oBrq5KqYgWTX9m3d'
file='verve_config.tgz.enc'
s3dest=$S3_LIB

mkdir -p $download
hadoop fs -copyToLocal $s3dest$file $download
openssl enc -in $download/$file -pass pass:$pass -d -aes-256-cbc | tar -xz -C ~
cp ~/.ssh/id_rsa.verve ~/.ssh/id_rsa

util=$basedir/code/s3/util/python
mkdir -p $util
hadoop fs -copyToLocal $S3_CODE/util/python/* $util
export PYTHONPATH=$util
echo "export PYTHONPATH=$PYTHONPATH" >> ~/.bashrc

hadoop fs -copyToLocal $S3_LIB/boto-2.5.2.tar.gz $download/boto-2.5.2.tar.gz
tar -xzf boto-2.5.2.tar.gz
cd boto-2.5.2
sudo python setup.py install

