#!/usr/bin/env python

import logging
import os
import signal
import socket
import subprocess
import time

import MySQLdb

logger = logging.getLogger(__name__)


def get_open_port():
  s = socket.socket()
  s.bind(('',0))
  port = s.getsockname()[1]
  s.close()
  return port


class mysql_connect:
  def __init__(self, mysql_group, tunnel_host):
    local_port = get_open_port()
    # TODO: get host/remote_port from .my.cnf file
    #host = 'vpc-stg-app-verveads-0.cpqtuzct7fyu.us-east-1.rds.amazonaws.com'
    host = 'vpc-prod-app-verveads-db-0.cpqtuzct7fyu.us-east-1.rds.amazonaws.com'
    remote_port = 3306
    # using & instead of -f flag to support automatic termination
    cmd = 'ssh -L {0}:{1}:{2} {3} -N &'.format(local_port, host, remote_port, tunnel_host)
    self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    # allow tunnel to instantiate (req'd because of not using -f)
    time.sleep(3)
    # need to use 127.0.0.1 instead of localhost to force TCP connection
    try:
      self.db = MySQLdb.connect(read_default_file='~/.my.cnf', read_default_group=mysql_group, host='127.0.0.1', port=local_port, charset='utf8')
    except MySQLdb.OperationalError:
      os.killpg(self.p.pid, signal.SIGTERM)
      raise
  
  def __enter__(self):
    return self.db
  
  def __exit__(self, type, value, traceback):
    # TODO: make sure self.p exists
    os.killpg(self.p.pid, signal.SIGTERM)

