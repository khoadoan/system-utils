#!/usr/bin/env python

import csv
import logging
import os

import MySQLdb
from MySQLdb import connections

logger = logging.getLogger(__name__)


def connect(**kwargs):
  return myConnection(**kwargs)


def mycnf_connect(read_default_group, **kwargs):
  db = myConnection(read_default_file='~/.my.cnf', read_default_group=read_default_group, **kwargs)
  logger.info('Connected to DB: %s', read_default_group)
  return db


#class myConnection(MySQLdb.connections.Connection):
class myConnection(connections.Connection):
  def load(self, file_name, table_name, field_separator='\t', line_separator=os.linesep):
    """Load file into the database.
    
    """
    stmt = """load data local infile '{0}' into table {1} fields terminated by '{2}' optionally enclosed by '\"' lines terminated by '{3}'""".format(file_name, table_name, field_separator, line_separator)
    self.xquery(stmt)
  
  def reload(self, file_name, table_name, field_separator='\t', line_separator=os.linesep):
    """Truncate table, then load file into the database.
    
    """
    self.truncate(table_name)
    self.load(file_name, table_name, field_separator, line_separator)
  
  def cquery(self, sql, params=tuple()):
    cursor = self.xquery(sql, params)
    self.commit()
    return cursor
  
  # can't use query because MySQLdb already defines
  def xquery(self, sql, params=tuple(), cursor_type=MySQLdb.cursors.Cursor):
    cursor = self.cursor(cursor_type)
    cursor.execute(sql, params)
    logger.debug('Executed query: %s', cursor._executed)
    return cursor
  
  def dquery(self, sql, params=tuple()):
    return self.xquery(sql, params, MySQLdb.cursors.DictCursor)
  
  def fetchall(self, sql, params=tuple()):
    cursor = self.xquery(sql, params)
    return cursor.fetchall()
  
  def fetchall_dict(self, sql, params=tuple()):
    cursor = self.dquery(sql, params)
    return cursor.fetchall()
  
  def force_utf8(self):
    c = self.cursor()
    c.execute('set names \'utf8\'')
  
  def get_table_list(self):
    cursor = self.xquery('show tables')
    return [row[0] for row in cursor]
  
  def get_create_stmt(self, table):
    c = self.cursor()
    c.execute('set option sql_quote_show_create = 1')
    c.execute('show create table {0}'.format(table))
    return c.fetchone()[1]
  
  def get_DictCursor(self):
    return self.cursor(MySQLdb.cursors.DictCursor)
  
  def drop(self, table):
    sql = 'drop table {0}'.format(table)
    try:
      self.xquery(sql)
    except MySQLdb.OperationalError as e:
      if e.args[0] == 1051:
        logger.warn('Table {0} not found'.format(table))
      else:
        raise
  
  def truncate(self, table_name):
    stmt = 'truncate table {0}'.format(table_name)
    self.xquery(stmt)
  
  def to_tsv(self, sql, filename, include_header=True):
    cursor = self.xquery(sql)
    colnames = [col[0] for col in cursor.description]
    with open(filename, 'wb') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter='\t', doublequote=False, escapechar='\\', lineterminator='\n')
      if include_header:
        csv_writer.writerow(colnames)
      #csv_writer.writerows(cursor)
      for row in cursor:
        row = tuple((o.replace('\n', '\\\n') if isinstance(o, basestring) else o for o in row))
        #row = tuple((o.encode('UTF-8') if isinstance(o, basestring) else o for o in row))
        csv_writer.writerow(row)


def _test():
  db = mycnf_connect('clientinfobrightRW')
  return db

