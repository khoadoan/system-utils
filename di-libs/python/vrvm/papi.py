#!/usr/bin/python

import base64
from datetime import datetime
import json
import logging
import urllib2
import sys
import time

from ext import myConfigParser

PAPI_CRED_FILE = '~/.config/verve/papi.ini'
PAPI_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

logger = logging.getLogger(__name__)


# TODO: move to http lib
def _urlopen_retry(req, max_retries=3):
  retries = 0
  while retries < max_retries:
    try:
      logger.debug('urllib2 opening: ' + req.get_full_url())
      r = urllib2.urlopen(req)
    except urllib2.HTTPError:
      logger.warning('urllib2.HTTPError error, trying to retrieve: ' + req.get_full_url(), exc_info=True)
      retries = retries + 1
      if retries == max_retries:
        logger.error('Max retries exceeded trying to retrieve: ' + req.get_full_url(), exc_info=True)
        raise
      time.sleep(5*retries)
    except:
      logger.critical('should not be here')
    else:
      return r


def _sanitize(data):
  if data == None:
    data = '\N'
  elif isinstance(data, basestring):
    if isinstance(data, unicode):
      data = data.encode('utf-8')
    # hack to get timestamps into Infobright (otherwise truncated to date)
    #if len(data) == len('2013-01-01T00:00:00+0000') and data[-5:] == '+0000':
    try:
      unused_t = datetime.strptime(data, PAPI_TIMESTAMP_FORMAT)
    except ValueError:
      pass
    else:
      data = data[0:10] + ' ' + data[11:22]
    data = '"{0}"'.format(data)
  elif isinstance(data, bool):
    # convert to 0/1. MySQL Load Infile does not handle True/False
    data = str(int(data))
  else:
    data = str(data)
  return data


# TODO: move to JSON lib
def _json_query(obj, query, default=None):
  fields = query.split('.')
  try:
    for f in fields:
      obj = obj[f]
  except KeyError:
    return default
  else:
    return obj


# TODO: move to JSON lib
def extract(obj, fields):
  return [[_json_query(o, f) for f in fields] for o in obj]


def unnest(objects, field):
  objects = filter(lambda o: field in o, objects)
  objects = map(lambda o: o[field], objects)
  return objects


# TODO: defaults of '' for strings and -1 for ints ... push to DB
def to_tsv(data, output=sys.stdout, field_sep='\t'):
  for row in data:
    row = map(_sanitize, row)
    print >> output, field_sep.join(row)


class Error(Exception):
  pass


class NoDataError(Error):
  def __init__(self, msg):
    self.msg = msg


class papi:
  def __init__(self):
    cfg = myConfigParser.get_cfg(filename=PAPI_CRED_FILE)
    self.username = cfg.username
    self.password = cfg.password
    self.url = cfg.endpoint
  
  def _get(self, resource):
    auth = base64.encodestring('{0}:{1}'.format(self.username, self.password))[:-1]
    req = urllib2.Request(self.url + resource)
    req.add_header('Authorization', 'Basic {0}'.format(auth))
    r = _urlopen_retry(req)
    # commented out because the calls are so slow anyway ...
    time.sleep(1) # avoid clogging end point on repeated calls
    response = r.read()
    obj = json.loads(response)
    if hasattr(obj, 'errorMessage'):
      raise Exception(obj.errorMessage)
    return obj
  
  # expected output from pApi is a result object enclosing the list of results
  def get(self, resource):
    objects = self._get(resource)
    objects = objects.values()[0]
    if not isinstance(objects, list):
      raise TypeError('Expected list, found ' + type(objects))
    if len(objects) == 0:
      #raise NoDataError('No data found.')
      logger.warning('Empty results for resource: %s', resource)
    return objects

