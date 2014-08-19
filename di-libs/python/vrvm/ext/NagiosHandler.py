#!/usr/bin/env python

import logging
import logging.handlers
import os
import time


class NagiosHandler(logging.Handler):
  # default the hostname
  host = 'localhost'
  svcHost = os.uname()[1]
  svc = None
    
  def __init__(self, svc, **kwargs):
    if 'level' in kwargs:
      logging.Handler.__init__(self, kwargs['level'])
    else:
      logging.Handler.__init__(self, logging.WARNING)
    if 'host' in kwargs:
      self.host = kwargs['host']
    if 'svcHost' in kwargs:
      self.svcHost = kwargs['svcHost']
    self.svc = svc
  
  # PROCESS_SERVICE_CHECK_RESULT;<host_name>;<svc_description>;<return_code>;<plugin_output>
  def emit(self, rec):
    logging.getLogger('root').debug('emitting %s' % rec)
    rc = 3
    if rec.levelno == logging.INFO:
      rc = 0
    elif rec.levelno == logging.WARNING:
      rc = 1
    elif rec.levelno == logging.ERROR or rec.levelno == logging.CRITICAL:
      rc = 2
    os.system('echo "%s;%s;%d;%s" | /usr/sbin/send_nsca -H %s -d ";" >/dev/null 2>&1' % (self.svcHost, self.svc, rc, rec.msg, self.host))


if __name__ == '__main__':
  log = logging.getLogger('root')
  log.setLevel(logging.INFO)
  log.addHandler(logging.StreamHandler())
  log.addHandler(NagiosHandler('dummy-test'))
  log.info('test message to console')
  log.warning('test warning message to console/nagios')
  log.error('test error message to console/nagios')
  log = logging.getLogger('nagios')
  log.setLevel(logging.INFO)
  log.addHandler(NagiosHandler('demo-test', level = logging.INFO))
  log.info('everything ok')
  log.warning('everything not ok')
  log.error('everything broken')

