#!/usr/bin/env python

import ConfigParser
import logging
import os
import sys

from vrvm.ext.bunch import Bunch

logger = logging.getLogger(__name__)


def derive_filename():
  #import pdb; pdb.set_trace()
  p = os.path.realpath(sys.argv[0])
  p = os.path.basename(p)
  f = os.path.splitext(p)[0]
  filename = '{0}/{1}.cfg'.format(sys.path[0], f)
  logger.debug('Inferred configuration file: %s', filename)
  return filename


def get_cfg(filename=None, section='DEFAULT'):
  if filename == None:
    filename = derive_filename()
    logger.debug('derived filename: %s', filename)
  filename = os.path.expanduser(filename)  # not sure if this is necessary for config.read(), but doesn't hurt
  config = ConfigParser.SafeConfigParser()
  config.optionxform = str # default behavior converts option names to lowercase
  config.read(filename)
  logger.info('Read %s section from configuration file %s', section, filename)
  d = dict(config.items(section))
  return Bunch(**d)

