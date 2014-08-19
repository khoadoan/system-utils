#!/usr/bin/env python

import logging
import shlex
import subprocess

logger = logging.getLogger(__name__)


def _sh_call(cmd):
  return subprocess.call(cmd, shell=True)


def file_exists(filename):
  cmd = 'hadoop fs -test -e ' + filename
  return not _sh_call(cmd)


def copy_from_s3(f_in, f_out, f_log='/dev/null'):
  logger.warning('deprecated')
  distcp(f_in, f_out, f_log)


def distcp(f_in, f_out, f_log='/dev/null'):
  # TODO: utilize s3distcp
  cmd = 'hadoop distcp {0} {1} > {2} 2>&1'.format(f_in, f_out, f_log)
  _sh_call(cmd)


def remove(path):
  if file_exists(path):
    cmd = 'hadoop fs -rmr ' + path
    _sh_call(cmd)


def copy_to_local(src, dst):
  cmd = 'hadoop dfs -copyToLocal {0} {1}'.format(src, dst)
  args = shlex.split(cmd)
  return subprocess.call(args)


def cp(src, dst):
  cmd = 'hadoop dfs -cp {0} {1}'.format(src, dst)
  args = shlex.split(cmd)
  return subprocess.call(args)


def lsr(path):
  cmd = 'hadoop fs -lsr ' + path
  args = shlex.split(cmd)
  proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  if proc.returncode:
    raise Exception('error executing {0}: {1}'.format(cmd, err))
  files = out.rstrip('\n').split('\n')
  #TODO: further parsing of output:
  #['-rw-r--r--', '2', 'hadoop', 'supergroup', '22196652', '2014-02-26', '16:16', '/home/jeff/avro-schema-segregated/request/pre/2014-02-25/adcel-attributed-request_2014-02-25_00-13_app003-adcel.log']
  #>>> foreach line in files, line_array = line.split()
  #file_size = int(line_array[4])
  #file_name = line_array[7]
  return files

