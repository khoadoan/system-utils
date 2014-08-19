#!/usr/bin/env python
#
# utility classes for sending graphite metrics
#

import os
import socket
import time


class GraphitePrefix:
  proj = 'di'
  app = None
  host = os.uname()[1].split('.')[0]
  
  def __init__(self, app, task, **kwargs):
    self.app = app
    self.task = task
    if 'proj' in kwargs:
      self.proj = kwargs['proj']
    if 'host' in kwargs:
      self.host = kwargs['host']
  
  def __str__(self):
    return '%s.%s.%s.%s' % (self.proj, self.app, self.host, self.task)


class GraphiteClient:
  host = 'localhost'
  port = 2003
  conn = None
  prefix = None
  
  def __init__(self, prefix, **kwargs):
    self.setPrefix(prefix)
    if 'host' in kwargs:
      self.host = kwargs['host']
    if 'port' in kwargs:
      self.port = kwargs['port']
  
  def __del__(self):
    if self.conn != None:
      self.conn.close()
  
  def send(self, name, value, ts = int(time.time())):
    self.open()
    self.conn.sendall('%s.%s %lf %ld\n' % (self.prefix, name, value, ts))
  
  def open(self):
    if self.conn == None:
      self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.conn.connect((self.host, self.port))
  
  def setPrefix(self, prefix):
    self.prefix = prefix
  
  def __str__(self):
    return '%s.%s' % (self.host, self.port)


if __name__ == '__main__':
  gp = GraphitePrefix('demo', 'job0')
  print GraphiteClient(gp)
  print GraphiteClient(gp, port = 20003)
  print GraphiteClient(gp, host = 'dev0')
  gc = GraphiteClient(gp)
  gc.send('metric0', 10)
  gc.setPrefix(GraphitePrefix('demo', 'job1', proj = 'adcel'))
  gc.send('metric0', 10)

