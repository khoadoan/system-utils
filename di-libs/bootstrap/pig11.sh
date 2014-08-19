#!/bin/bash
set -e

S3_BASE="s3://verve-opsdata"
S3_LIB="$S3_BASE/lib"

base="/home/hadoop/verve"

downloads="$base/downloads"
mkdir -p $downloads

software="$base/software"
mkdir -p $software


f="pig-0.11.1"
fz="pig-0.11.1.tar.gz"
hadoop fs -copyToLocal $S3_LIB/$fz $downloads
tar -xzf $downloads/$fz -C $software
echo "export PATH=$software/$f/bin:\$PATH" >> ~/.bashrc

