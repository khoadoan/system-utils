#!/bin/bash

S3_BASE="s3://verve-opsdata"
S3_LIB="$S3_BASE/lib"

cd /home/hadoop
hadoop fs -copyToLocal $S3_LIB/pig-0.11.1.tar.gz pig-0.11.1.tar.gz
tar zxf pig-0.11.1.tar.gz
mv pig-0.11.1 pig
# TODO: linking would be more consistent with what AWS is doing
#ln -s /home/hadoop/pig-0.11.1/bin/pig bin/pig

