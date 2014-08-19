#!/usr/bin/env python

import logging

from vrvm.ext import myMySQLdb

DEFAULT_CFG_GROUP = 'clientinfobrightRW'

logger = logging.getLogger(__name__)


def connect(**kwargs):
  return infobright(**kwargs)


def mycnf_connect(read_default_group=DEFAULT_CFG_GROUP, **kwargs):
  return infobright(read_default_file='~/.my.cnf', read_default_group=read_default_group, **kwargs)


class infobright(myMySQLdb.myConnection):
  def set_autocommit(self, b):
    # TODO: use conn.autocommit()?
    cursor = self.cursor()
    cursor.execute('set autocommit=%i' % b)
  
  def truncate(self, table_name):
    """The free version of infobright does not support the truncate command.
    
    """
    sql = self.get_create_stmt(table_name)
    self.drop(table_name)
    self.xquery(sql)

