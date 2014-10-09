#!/bin/sh

BASEDIR=${1:-"Missing basedir"}

echo "Downloading Spark to ${BASEDIR}"
wget -nv -P ${BASEDIR} http://d3kbcqa49mib13.cloudfront.net/spark-1.0.2-bin-hadoop1.tgz

echo "Unpacking ${BASEDIR}/spark-1.0.2-bin-hadoop1.tgz"
tar zxf ${BASEDIR}/spark-1.0.2-bin-hadoop1.tgz -C "${BASEDIR}"

#echo "Downloading setup code"
#cd ${BASEDIR}
#git clone git@github.com:khoadoan/system-utils
#cd system-utils/hadoop-utils

echo "Install Sparks on Slaves"
nohup ./dist-exec.sh "mkdir -p ${BASEDIR} && wget -nv -P ${BASEDIR} http://d3kbcqa49mib13.cloudfront.net/spark-1.0.2-bin-hadoop1.tgz && tar zxf ${BASEDIR}/spark-1.0.2-bin-hadoop1.tgz -C ${BASEDIR}" 2>&1 &

echo "Adding slaves"
./ip-list.sh > ${BASEDIR}/spark-1.0.2-bin-hadoop1/conf/slaves

export SPARK_SSH_OPTS="-i ${HOME}/.ssh/verve-shared.pem"

