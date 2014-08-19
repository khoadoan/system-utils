#!/usr/bin/env python

import logging

from vrvm.ext import myMySQLdb

DEFAULT_CFG_GROUP = 'clientwarehouse'

logger = logging.getLogger(__name__)


def connect(**kwargs):
  return vlsm_db(**kwargs)


def mycnf_connect(read_default_group=DEFAULT_CFG_GROUP, **kwargs):
  return vlsm_db(read_default_file='~/.my.cnf', read_default_group=read_default_group, **kwargs)


class wh(myMySQLdb.myConnection):
  pass

