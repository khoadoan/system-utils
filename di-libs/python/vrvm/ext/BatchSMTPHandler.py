#!/usr/bin/env python

import logging
import logging.handlers
import os


class BatchSMTPHandler(logging.handlers.SMTPHandler):
  msgs = []
  maxLogLevel = logging.NOTSET;
  
  def __init__(self, toaddrs, subject, **kwargs):
    if 'mailhost' not in kwargs:
      mailhost = 'localhost'
    if 'fromaddr' not in kwargs:
      fromaddr = os.getlogin()
    logging.handlers.SMTPHandler.__init__(self, mailhost, fromaddr, toaddrs, subject)

  def emit(self, rec):
    self.msgs.append(rec.__str__());
    # adjust the log level for the final message
    if self.maxLogLevel < rec.levelno:
      self.maxLogLevel = rec.levelno;

  def send(self):
    if len(self.msgs) > 0:
      # generate a 'final' record
      rec = logging.makeLogRecord({'msg':'\n'.join(self.msgs), 'levelno':self.maxLogLevel})
      logging.handlers.SMTPHandler.emit(self, rec);
      self.msgs = []

  def close(self):
    self.send()


if __name__ == '__main__':
  mh = BatchSMTPHandler(['marc@vervemobile.com'], 'test message')
  mlog = logging.getLogger('mail')
  mlog.setLevel(logging.WARNING)
  mlog.addHandler(mh);
  mlog.error('something went VERY wrong')
  mlog.warning('something went KINDA wrong')
  mlog.critical('shit hit the fan')

