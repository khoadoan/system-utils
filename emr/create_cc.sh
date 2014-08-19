#!/bin/bash

DEPLOY_TIMESTAMP=$(readlink -fn /opt/verve/di-utils/current | awk -F "/" '{print $NF}')
S3_CODEBASE="s3://verve-opsdata/code/di-utils/${DEPLOY_TIMESTAMP}/di-libs/bootstrap"
CORE_INSTANCES=10

elastic-mapreduce --create --name "Caching Cluster" --alive \
  --visible-to-all-users \
  --set-termination-protection true \
  --log-uri "s3://verve-opsdata-aws/emr-logs" \
  --instance-group master --instance-type m1.large --instance-count 1 \
  --instance-group core --instance-type m3.xlarge --instance-count $CORE_INSTANCES \
  --ami-version 2.4.6 \
  --hadoop-version 1.0.3 \
  --pig-interactive --pig-versions 0.11.1.1 \
  --bootstrap-action "$S3_CODEBASE/bootstrap_shell_env.sh" \
  --bootstrap-name "Verve EMR Base Configuration" \
  --bootstrap-action "$S3_CODEBASE/bootstrap_cc.sh" \
  --bootstrap-name "CC-Specific Options" \
  --bootstrap-action "s3://elasticmapreduce/bootstrap-actions/configure-daemons" \
  --bootstrap-name "Configure Daemons" \
  --arg "--datanode-heap-size=384" \
  --arg "--tasktracker-heap-size=384" \
  --bootstrap-action "s3://elasticmapreduce/bootstrap-actions/configure-hadoop" \
  --bootstrap-name "Configure Hadoop" \
  --args "-h,dfs.replication=2,-m,mapred.jobtracker.taskScheduler=org.apache.hadoop.mapred.FairScheduler,-m,mapred.tasktracker.map.tasks.maximum=8,-m,mapred.tasktracker.reduce.tasks.maximum=3,-m,mapred.map.tasks.speculative.execution=false,-m,mapred.reduce.tasks.speculative.execution=false"
