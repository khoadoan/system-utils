#!/usr/bin/env python

import errno
import logging
import os

import lockfile
from lockfile.pidlockfile import PIDLockFile

logger = logging.getLogger(__name__)


def _ensure_path_exists(path):
  try:
    os.makedirs(path)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise


# TODO: support decorator constructor with default arguments
#def lock(filename, suppress_error=False, timeout=1):
def lock(filename):
  suppress_error = False
  timeout = 1
  """Boilerplate locking wrapper, intended for use as a decorator.
  
  suppress_error can be set for scripts where locking errors are
  expected (e.g., frequently running SQS consumers).
  
  replaces default timeout wait (infinite) with a minimal default
  of one (zero doesn't work).
  
  """
  filename = os.path.expanduser(filename)
  def wrap(f):
    def wrapped_f():
      _ensure_path_exists(os.path.dirname(filename))
      lock = PIDLockFile(filename, timeout=timeout)
      try:
        lock.acquire()
      except lockfile.LockTimeout:
        if suppress_error:
          logger.info('Unable to acquire lock: %s', filename)
          # could continue, but probably safer to quit?
          os._exit(os.EX_OK)  # sys.exit raises an exception
        else:
          raise
      else:
        logger.info('Acquired lock: %s', filename)
        f()
        lock.release()
        logger.info('Released lock: %s', filename)
    return wrapped_f
  return wrap


# duplicating code above because I'm too busy to figure out how
# to set up decorators with default arguments.
def softlock(filename):
  suppress_error = True
  timeout = 1
  """Boilerplate locking wrapper, intended for use as a decorator.
  
  suppress_error can be set for scripts where locking errors are
  expected (e.g., frequently running SQS consumers).
  
  replaces default timeout wait (infinite) with a minimal default
  of one (zero doesn't work).
  
  """
  filename = os.path.expanduser(filename)
  def wrap(f):
    def wrapped_f():
      _ensure_path_exists(os.path.dirname(filename))
      lock = PIDLockFile(filename, timeout=timeout)
      try:
        lock.acquire()
      except lockfile.LockTimeout:
        if suppress_error:
          logger.info('Unable to acquire lock: %s', filename)
          # could continue, but probably safer to quit?
          os._exit(os.EX_OK)  # sys.exit raises an exception
        else:
          raise
      else:
        logger.info('Acquired lock: %s', filename)
        f()
        lock.release()
        logger.info('Released lock: %s', filename)
    return wrapped_f
  return wrap

