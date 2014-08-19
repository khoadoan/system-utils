#!/usr/bin/env python

import inspect
import logging
import logging.handlers
import os
import re
from socket import gethostname
import sys

LOG_FMT = '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s'
DI_DLIST = ['datainfrastructure@vervemobile.com']
PROD_USER = 'etlprod'

logger = logging.getLogger(__name__)


class Error(Exception):
  pass


class DirectoryStructureError(Error):
  pass


def _add_smtp_handler(logger_in, level=logging.ERROR):
  # TODO: make into args?
  smtp_to = _get_default_dlist()
  smtp_from = _get_smtp_sender()
  
  subject = ' '.join(sys.argv)
  # NOTE: SMTPHandler doesn't support Reply-To header; could subclass
  h = logging.handlers.SMTPHandler('localhost', smtp_from, smtp_to, subject)
  h.setLevel(level)
  formatter = logging.Formatter(LOG_FMT)
  h.setFormatter(formatter)
  logger_in.addHandler(h)


def deprecated(msg='deprecated'):
  """Log uses of old code."""
  s = inspect.stack()
  module = s[1][1]
  caller = s[1][3]
  logger.warning('%s: %s in %s', msg, caller, module)


def _get_default_dlist():
  user = _get_user()
  if user == PROD_USER:
    notify = DI_DLIST
  else:
    # assume development; no need to notify everyone
    notify = ['{user}@vervemobile.com'.format(user=user)]
  return notify


def _get_smtp_sender():
  host = gethostname()
  smtp_sender = '{user}@{host}'.format(user=_get_user(), host=host)
  return smtp_sender


def _get_user():
  return os.environ['USER']


# callers must live under .*/releases/$TIMESTAMP/.*
def get_version():
  """Identify release version to sync with S3."""
  frame = inspect.stack()[1]
  sourcefile = os.path.realpath(inspect.getsourcefile(frame[0]))
  logger.debug(sourcefile)
  try:
    ver = re.search('releases/(\d+)/', sourcefile).group(1)
  except AttributeError:
    raise DirectoryStructureError(sourcefile)
  return ver


# TODO: default argument for debug_level (trickier than it seems)
def setup_logging(debug_level):
  """Boilerplate logging wrapper, intended for use as a decorator."""
  def wrap(f):
    def wrapped_f():
      logging.basicConfig(level=debug_level, format=LOG_FMT)
      _add_smtp_handler(logger)
      logger.info('init')
      try:
        f()
      except Exception:
        logger.critical('bad news ...', exc_info=True)
        sys.exit(1)
      else:
        logger.info('finish')
    return wrapped_f
  return wrap

