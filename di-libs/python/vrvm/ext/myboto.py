#!/usr/bin/env python

import ConfigParser
import logging
import os
import time

import boto
import boto.sqs.message
from boto.emr.step import JarStep
from boto.emr.bootstrap_action import BootstrapAction
from boto.emr.instance_group import InstanceGroup

from vrvm import xlog

HOME_DIR = os.path.expanduser('~')
DEFAULT_CRED_FILE = os.path.join(HOME_DIR, '.boto')

logging.getLogger('boto').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# visibility timeout set absurdly high (12h) to ensure that slow-running
# parallel processes do not consume messages more than once.
def consume_queue(queue_name):
  conn = boto.connect_sqs()
  q = conn.get_queue(queue_name)
  m = q.read(visibility_timeout=3600*12)
  while m is not None:
    yield m
    q.delete_message(m)
    logger.info('Message deleted')
    m = q.read()


def get_credentials(cred_file=DEFAULT_CRED_FILE):
  config = ConfigParser.ConfigParser()
  config.read(cred_file)
  aws_access_key_id = config.get('Credentials', 'aws_access_key_id')
  aws_secret_access_key = config.get('Credentials', 'aws_secret_access_key')
  return (aws_access_key_id, aws_secret_access_key)


def get_s3_conn(cred_file=DEFAULT_CRED_FILE):
  aws_access_key_id, aws_secret_access_key = get_credentials(cred_file)
  return boto.connect_s3(aws_access_key_id, aws_secret_access_key)


class Error(Exception):
  pass


class IncompleteDataError(Error):
  pass


class sqs:
  def __init__(self):
    self.conn = boto.connect_sqs()
  
  def write_message(self, queue_name, body):
    q = self.conn.create_queue(queue_name)
    m = boto.sqs.message.Message()
    m.set_body(body)
    status = q.write(m)
    logger.info("Wrote message to queue %s: %s", queue_name, body)
  
  def create_hourly_jobflow_manual(self, script, queue_name_out, queue_name_in, current_folder_name, log_prefix, pig_args):
    """writes to queue being read by an EMR consumer (circumvent EMR add step).
    
    """
    # TODO: standardize message packing/unpacking
    pig_command_args = ['/home/hadoop/bin/pig']
    for varname in pig_args.keys():
      pig_command_args.append('-p')
      pig_command_args.append(varname + '=' + pig_args[varname])
    pig_command_args.append(script)
    pig_command = '|'.join(pig_command_args)
    
    queue_message = '\t'.join([pig_command, queue_name_out, current_folder_name + '|' + log_prefix])
    self.write_message(queue_name_in, queue_message)


class emr:
  BOOTSTRAP_GANGLIA = BootstrapAction('Install ganglia',
    's3://elasticmapreduce/bootstrap-actions/install-ganglia',
    None)
  BOOTSTRAP_PIG = BootstrapAction('Install Pig',
    's3://us-east-1.elasticmapreduce/libs/pig/pig-script',
    ['--base-path', 's3://us-east-1.elasticmapreduce/libs/pig/', '--install-pig', '--pig-versions', '0.11.1.1'])
  BOOTSTRAP_DEBUG = BootstrapAction('AWS requested, see DI-115',
    's3://lab-emr/customer/enablehttpdebugging.bash',
    None)
  SCRIPT_RUNNER_JAR = 's3://us-east-1.elasticmapreduce/libs/script-runner/script-runner.jar'
  
  @classmethod
  def get_ig(cls, num_instances, role, type, market, name, bidprice=None):
    return InstanceGroup(num_instances, role, type, market, name, bidprice)
  
  @classmethod
  def get_old_bootstrap_actions(cls):
    xlog.deprecated('hard-coded di-apps references')
    s3_codebase = 's3://verve-opsdata/code/di-apps/{0}/di-libs'.format(xlog.get_version())
    bootstrap_sh = BootstrapAction('Install custom shell env',
      '{0}/bootstrap/bootstrap_shell_env.sh'.format(s3_codebase),
      None)
    bootstrap_py = BootstrapAction('Install custom python env',
      '{0}/bootstrap/bootstrap_python_env.sh'.format(s3_codebase),
      ['{0}/python'.format(s3_codebase)])
    return [cls.BOOTSTRAP_GANGLIA, cls.BOOTSTRAP_PIG, bootstrap_sh, bootstrap_py]
  
  @classmethod
  def step_copy(cls, src, dest):
    # local jar more current than s3 jar, per AWS support ticket 109569051
    #jar = 's3://us-east-1.elasticmapreduce/libs/s3distcp/1.latest/s3distcp.jar',
    jar = '/home/hadoop/lib/emr-s3distcp-1.0.jar'
    return cls.step_exec('copy S3 to HDFS',
      ['--src', src, '--dest', dest],
      jar=jar)
  
  @classmethod
  def step_disable_termination_notification(cls):
    return cls.step_exec('disable termination notification', [
      's3://verve-opsdata/home/jeff/test/bootstrap-termination-notification-companion.sh'])
    #return cls.step_exec('disable termination notification', [
    #  '/bin/rm -f',
    #  '/mnt/var/lib/instance-controller/public/shutdown-actions/emr-termination.py'])
  
  @classmethod
  def step_exec(cls, step_name, step_args, jar=SCRIPT_RUNNER_JAR, action_on_failure='TERMINATE_JOB_FLOW'):
    return JarStep(
      name=step_name,
      jar=jar,
      action_on_failure=action_on_failure,
      step_args=step_args)
  
  @classmethod
  def step_hdfs_del(cls, filename):
    return cls.step_exec('delete from HDFS', [
      '/home/hadoop/bin/hadoop',
      'fs', '-rmr', filename])
  
  @classmethod
  def step_write_queue(cls, queue, msg):
    xlog.deprecated('hard-coded di-apps references')
    s3_codebase = 's3://verve-opsdata/code/di-apps/{0}/di-libs'.format(xlog.get_version())
    return cls.step_exec('send message to queue', [
      '{0}/python/vrvm/emr_send_msg.py'.format(s3_codebase),
      queue, msg])
  
  def __init__(self):
    self.conn = boto.connect_emr()
  
  def run_jobflow(self,
    log_uri='s3://verve-opsdata-aws/emr-logs',
    ec2_keyname='verve-shared',
    ami_version='2.4.3',
    hadoop_version='1.0.3',
    visible_to_all_users=True,
    **kwargs):
    jobflow_id = self.conn.run_jobflow(
      log_uri=log_uri,
      ec2_keyname=ec2_keyname,
      ami_version=ami_version,
      hadoop_version=hadoop_version,
      visible_to_all_users=visible_to_all_users,
      **kwargs)
    logger.info('Started jobflow %s.', jobflow_id)
    return jobflow_id


class ses:
  def __init__(self):
    self.conn = boto.connect_ses()
  
  def send_html_email(self, source, to_addresses, subject, body):
    # body param required due to older version of boto
    self.conn.send_email(
    source=source,
    to_addresses=to_addresses,
    subject=subject,
    format='html',
    html_body=body,
    body=None)


class s3:
  # TODO: consider caching bucket objects
  def __init__(self, cred_file=DEFAULT_CRED_FILE):
    cred_file = os.path.expanduser(cred_file)
    aws_access_key_id, aws_secret_access_key = get_credentials(cred_file)
    self.conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
  
  def uri2parts(self, s3_uri):
    s = s3_uri.partition('//')[2]
    (s3_bucket, _unused, s3_filename) = s.partition('/')
    return (s3_bucket, s3_filename)
  
  def put_retry(self, s3_uri, local_filename, max_retries=3, policy=None):
    (s3_bucket, s3_filename) = self.uri2parts(s3_uri)
    return self._put_retry(s3_bucket, s3_filename, local_filename, max_retries, policy)
  
  def _put_retry(self, s3_bucket, s3_filename, local_filename, max_retries=3, policy=None):
    """put a file to s3, sleep for progressively longer if failure"""
    b = self.conn.get_bucket(s3_bucket)
    retries = 0
    while retries < max_retries:
      try:
        s3_key = b.new_key(s3_filename)
        s3_key.set_contents_from_filename(local_filename, policy=policy)
      except:
        logger.info('File transfer error: ' + s3_filename, exc_info=True)
        retries = retries + 1
        if retries == max_retries:
          raise
        time.sleep(retries)
      else:
        logger.info('Archived %s to %s/%s', local_filename, s3_bucket, s3_filename)
        return os.path.getsize(local_filename)
  
  def put_public_read_retry(self, s3_bucket, s3_filename, local_filename, max_retries=3):
    """put a file to s3, sleep for progressively longer if failure"""
    return self._put_retry(s3_bucket, s3_filename, local_filename, max_retries, 'public-read')
  
  def copy_retry(self, s3_bucket, s3_filename, local_filename, max_retries=3):
    """grab a file from s3, sleep for progressively longer if failure"""
    logger.debug('copying %s to %s', s3_filename, local_filename)
    b = self.conn.get_bucket(s3_bucket)
    retries = 0
    while retries < max_retries:
      try:
        s3_key = b.get_key(s3_filename)
        s3_key.get_contents_to_filename(local_filename)
      except:
        logger.info('File transfer error: ' + s3_filename, exc_info=True)
        retries = retries + 1
        if retries == max_retries:
          raise
        time.sleep(retries)
      else:
        return os.path.getsize(local_filename)
  
  def get_filenames(self, bucket, directory, delimiter=''):
    """get a list of filenames inside of a bucker/directory"""
    b = self.conn.get_bucket(bucket)
    rs = b.list(directory, delimiter)
    return [key.name for key in rs if '$folder$' not in key.name]
  
  def get_filenames_success(self, bucket, directory):
    # make sure "_SUCCESS" exists, remove it from the output
    filenames = self.get_filenames(bucket, directory)
    success_file = directory + '/_SUCCESS'
    try:
      filenames.remove(success_file)
    except ValueError:
      logger.error('_SUCCESS file not found: %s/%s', bucket, directory)
      raise IncompleteDataError()
    return filenames
  
  def get_uris(self, uri_prefix, delimiter=''):
    (bucket, prefix) = self.uri2parts(uri_prefix)
    fragments = self.get_filenames(bucket, prefix, delimiter)
    uris = ['s3://{0}/{1}'.format(bucket, f) for f in fragments]
    return uris
  
  def sync_up(self, bucket, remote_path, local_path):
    """Upload if not already on S3"""
    # TODO: make sync_down; both can probably use generic sync code
    b = self.conn.get_bucket(bucket)
    remote_ls = b.list(remote_path)
    remote_ls = [f.name for f in remote_ls]
    local_ls = os.listdir(local_path)
    for local_file in local_ls:
      remote_file = remote_path + local_file
      if remote_file not in remote_ls:
        logger.info('Transferring file to S3: %s', remote_file)
        key = b.new_key(remote_file)
        key.set_contents_from_filename(os.path.join(local_path, local_file))
  
  def exists(self, uri):
    (bucket, prefix) = self.uri2parts(uri)
    b = self.conn.get_bucket(bucket)
    rs = b.list(prefix)
    return any(True for _ in rs)
  
  def validate_resources(self, required=[], forbidden=[]):
    for f in required:
      if not self.exists(f):
        raise Exception('Required resource not found: {0}'.format(f))
    for f in forbidden:
      if self.exists(f):
        raise Exception('Forbidden resource found: {0}'.format(f))

