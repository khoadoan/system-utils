#!/usr/bin/env python

import logging

from vrvm.ext import myMySQLdb

DEFAULT_CFG_GROUP = 'clientvlsm'

logger = logging.getLogger(__name__)


# TODO: refactor into vlsm_db class
def _fix_conn(db):
  # necessary because of invalid characters in segments.name
  db.force_utf8()


def connect(**kwargs):
  db = vlsm_db(**kwargs)
  _fix_conn(db)
  return db


def mycnf_connect(read_default_group=DEFAULT_CFG_GROUP, **kwargs):
  db = vlsm_db(read_default_file='~/.my.cnf', read_default_group=read_default_group, **kwargs)
  _fix_conn(db)
  return db


class vlsm_db(myMySQLdb.myConnection):
  pass

