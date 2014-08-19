import datetime
import fcntl
import getopt
import logging
import os
import re
import shutil
import sys
import time

import boto.s3.connection
import boto.sqs.connection
import boto.sqs.message

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''

logger = logging.getLogger(__name__)


def usage():
  """Prints the command-line usage to STDOUT
  
  """
  print 'Usage: ' + sys.argv[0] + ' [OPTION]'
  print '\nMandatory option:'
  print '  -l,  --log=log_prefix     log "prefix" or directory name (e.g. ad_response).'
  sys.exit(1)

def timeout(func, args=(), kwargs={}, timeout_duration=10, default=None):
  """This function will spawn a thread and run the given function
  using the args, kwargs and return the given default value if the
  timeout_duration is exceeded.
  
  """ 
  import threading
  class InterruptableThread(threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
      self.result = default
    
    def run(self):
      self.result = func(*args, **kwargs)
  
  it = InterruptableThread()
  it.start()
  it.join(timeout_duration)
  if it.isAlive():
    raise Exception('Process unresponsive')
  else:
    return it.result

def file_copy_retry(source_filename, destination_filename, max_retries):
  """Copy a file, sleep for progressively longer if failure
  
  """
  curr_retries = 0
  while curr_retries < max_retries:
    try:
      timeout(shutil.copyfile, (source_filename, destination_filename,), timeout_duration=600)
    except:
      if curr_retries > max_retries:
        raise
      else:
        logger.info('Unexpected error:' + str(sys.exc_info()))
        logger.info('File transfer error:' + source_filename)
        logger.info('Sleeping for ' + str(curr_retries) + ' seconds')
        curr_retries = curr_retries + 1
        time.sleep(curr_retries)
    else:
      current_size = os.path.getsize(destination_filename)
      return current_size

def file_delete_retry(delete_filename, max_retries):
  """Delete a file, sleep for progressively longer if failure
  
  """
  curr_retries = 0
  good_delete = False
  while not good_delete and curr_retries < max_retries:
    try:
      timeout(os.remove, (delete_filename,), timeout_duration=600)
    except:
      if curr_retries > max_retries:
        raise
      else:
        logger.info('Unexpected error:' + str(sys.exc_info()))
        logger.info('File delete error:' + source_filename)
        logger.info('Sleeping for ' + str(curr_retries) + ' seconds')
        curr_retries = curr_retries + 1
        time.sleep(curr_retries)
    else:
      good_delete = True

def recursive_dir(directory_name):
  """Builds a list of files from a given directory
  
  """
  file_list = []
  for root, dirs, files in os.walk(directory_name):
    for file in files:
      file_list.append([root, file, os.path.join(root, file)])
  return file_list

def process_directory(directory_name, s3_output_bucket, remote_dir, tmp_dir, skip_ext_check):
  """Copies *.log.gz files recursively from local directory to S3
  
  """
  processed_file_list = []
  file_list = recursive_dir(directory_name)
  exclude = ['ad_response', 'adcel-attributed-request']
  file_list = filter(lambda f: not any(s in f for s in exclude), file_list)
  for dir, file, fullfile in file_list:
    logger.debug('File found: ' + file)
    file_noextension, file_extension = os.path.splitext(file)
    file_md5 = file + '.md5'
    file_md5_complete = os.path.join(dir, file_md5)
    file_tmp = os.path.join(tmp_dir, file)
    if (skip_ext_check or file_extension == '.gz' or file_extension == '.log') and os.path.exists(file_md5_complete):
      logger.info('Event file found: ' + fullfile)
      logger.info('Copy file to local: ' + fullfile + ' --> ' + file_tmp)
      file_copy_retry(fullfile, file_tmp, 10)
      s3_filename = remote_dir + file
      logger.info('Transfering file to S3: ' + s3_filename)
      key = s3_output_bucket.new_key(s3_filename)
      key.set_contents_from_filename(file_tmp)
      logger.info('Deleting file local: ' + fullfile)
      logger.info('Deleting MD5 file local: ' + file_md5_complete)
      logger.info('Deleting file tmp: ' + file_tmp)
      file_delete_retry(fullfile, 10)
      file_delete_retry(file_md5_complete, 10)
      file_delete_retry(file_tmp, 10)
      processed_file_list.append(s3_filename)
  return processed_file_list

def main():
  try:
    getopt_opts, getopt_args = getopt.getopt(sys.argv[1:], 'lops:', ['log=', 'out=', 'path=', 'skip-ext-check'])
  except:
    usage()
  
  log_prefix = ''
  log_output = ''
  log_local = '/wal/logarchive.stg'
  skip_ext_check = False
  for o, a in getopt_opts:
    if o in ('-l', '--log'):
      log_prefix = a
    elif o in ('-o', '--out'):
      log_output = a
    elif o in ('-p', '--path'):
      log_local = a
    elif o in ('-s', '--skip-ext-check'):
      skip_ext_check = True
    else:
      usage()
  
  # Lyle's version used /tmp
  tmp_dir = '/var/tmp'
  
  # Lyle's version used logging.DEBUG
  logger.basicConfig(filename=tmp_dir+'/file_packer.' + log_prefix + '.log', level=logging.INFO)
  
  if re.search('^(|.*[/ ].*)$', log_prefix):
    logger.info('"%s" contains invalid characters', log_prefix)
    sys.exit(3)
  
  # only run one instance of the packer at a time
  try:
    fp = open('{0}/file_packer.{1}.lock'.format(tmp_dir, log_prefix), 'w')
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    logger.info('Process lock acquired')
  except IOError:
    logger.info('Process currently locked')
    sys.exit(3)
  
  # Eric's version used str(time.time())
  """Lyle did this because the other packer is running on multiple machines
  simultaneously and Adam requested this to have cron jobs that start at the
  same time populate the same path in S3"""
  current_id = str(int(round(time.time(), -1)))
  datestring = datetime.date.today().isoformat()
  
  # Lyle's version version had a trailing slash
  local = os.path.join(log_local, log_prefix)
  
  if not os.path.exists(local):
    logger.info('"%s" does not exist', local)
    sys.exit(3)
  
  remote_bucket = 'data.vrvm.com'
  remote_dir = 'temp/{0}/ds={1}/{2}/'.format(log_output, datestring, current_id)
  
  queue_message = '|'.join([remote_bucket, remote_dir, datestring, current_id, log_prefix])
  queue_name = 'file_packer_prod'
  
  sqs_conn = boto.sqs.connection.SQSConnection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
  s3_conn = boto.s3.connection.S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
  s3_output_bucket = s3_conn.get_bucket(remote_bucket)
  
  processed_file_list = process_directory(local, s3_output_bucket, remote_dir, tmp_dir, skip_ext_check)
  
  if len(processed_file_list) == 0:
    logger.info('No message to queue: ')
  else:
    queue = sqs_conn.create_queue(queue_name)
    m = boto.sqs.message.Message()
    m.set_body(queue_message)
    status = queue.write(m)
    logger.info('Wrote message to queue: ' + queue_name + '\t' + queue_message)

if __name__ == '__main__':
  main()

