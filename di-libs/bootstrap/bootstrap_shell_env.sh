#!/bin/bash
set -e

S3_LIB="s3://verve-opsdata/lib"
LOCAL_BASE="$HOME/verve"
DOWNLOADS="$LOCAL_BASE/downloads"

# see etl/deploy/store_vault.sh
pass="oBrq5KqYgWTX9m3d"
file="verve_config.tgz.enc"

mkdir -p $DOWNLOADS

hadoop fs -copyToLocal $S3_LIB/$file $DOWNLOADS
openssl enc -in $DOWNLOADS/$file -pass pass:$pass -d -aes-256-cbc | tar -xz -C ~
cp ~/.ssh/id_rsa.verve ~/.ssh/id_rsa

echo -e "\nalias ls='ls --color'" >> .bash_profile
git config --global color.ui true

# TODO: might be better to migrate these to the functions that need them
mkdir -p $LOCAL_BASE/log
mkdir -p /mnt/var/log/verve

