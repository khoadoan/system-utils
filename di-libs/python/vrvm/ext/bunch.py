#!/usr/bin/env python

import logging

logger = logging.getLogger(__name__)


# http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
# helper class to allow dot access instead of dict access
class Bunch:
  def __init__(self, **kwds):
    self.__dict__.update(kwds)

