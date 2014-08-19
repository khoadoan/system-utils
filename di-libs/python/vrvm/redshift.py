#!/usr/bin/env python
"""
# sudo yum install postgresql-devel postgresql-libs
# sudo yum groupinstall 'Development Tools'

sudo yum install python-devel libpq-dev gcc
sudo python-pip install psycopg2
"""
import logging
import json
import os
from subprocess import check_call

import psycopg2

logger = logging.getLogger(__name__)


class RedshiftBase(object):
  def __init__(self, dsn):
    self.dsn = dsn
  
  def _get_aws_creds(self):
    if hasattr(self, '_aws_creds'):
      return self._aws_creds
    
    f = os.path.expanduser('~/credentials.json')
    with open(f) as fp:
      o = json.load(fp)
    self._aws_creds = {
      'aws_access_key_id': o['access_id'],
      'aws_secret_access_key': o['private_key']
    }
    return self._aws_creds


# use RedshiftPsql (psql) instead of redshift (psychopg2) to support multi-statement sql scripts
class RedshiftPsql(RedshiftBase):
  def __init__(self, dsn):
    super(RedshiftPsql, self).__init__(dsn)
    # NOTE: AWS creds not req'd for all statements
    c = self._get_aws_creds()
    os.environ['AWS_ACCESS_KEY_ID'] = c['aws_access_key_id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = c['aws_secret_access_key']
  
  def run(self, filename, params):
    params.update({
      'aws_access_key_id': '$AWS_ACCESS_KEY_ID',
      'aws_secret_access_key': '$AWS_SECRET_ACCESS_KEY'
    })
    pp_params = [' \\\n  -v {0}={1}'.format(p[0], p[1]) for p in params.iteritems()]
    pp_cmd = 'psql service={0} -f {1}'.format(self.dsn, filename) + ''.join(pp_params)
    check_call(pp_cmd, shell=True)
    logger.info('Executed command: %s', pp_cmd)


class redshift(RedshiftBase):
  def __init__(self, dsn):
    super(redshift, self).__init__(dsn)
    self.conn = psycopg2.connect('service={0}'.format(self.dsn))
  
  def _get_aws_creds_string(self):
    c = self._get_aws_creds()
    return 'aws_access_key_id={0};aws_secret_access_key={1}'.format(
      c['aws_access_key_id'],
      c['aws_secret_access_key']
    )
  
  def run(self, sql):
    with self.conn.cursor() as cur:
      cur.execute(sql)
    self.conn.commit()  # not needed on DDL, but recommended by Redshift docs
    logger.info('Executed query: %s', sql)
  
  def truncate(self, tbl):
    sql = """truncate {0}""".format(tbl)
    self.run(sql)
  
  def s3_load(self, tbl, src, opts):
    creds = self._get_aws_creds_string()
    # TODO: use cur.copy_expert?
    sql = """copy {0} from '{1}' credentials '{2}' {3}""".format(tbl, src, creds, opts)
    self.run(sql)
  
  def delete(self, tbl, where_clause):
    sql = """delete from {0} {1}""".format(tbl, where_clause)
    self.run(sql)
  
  def s3_trunc_load(self, tbl, src, opts):
    self.truncate(tbl)
    self.s3_load(tbl, src, opts)

