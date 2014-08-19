#!/usr/bin/env python

import base64
import httplib
import json
import logging
import os
import urllib

import xlog
from ext import myboto
from ext import myConfigParser

SERVER = 'vlsm.vervemobile.com'
AWS_FILE = '~/.config/verve/vlsm.boto'
VLSM_CRED_FILE = '~/.config/verve/vlsm.ini'

logger = logging.getLogger(__name__)


class vlsm():
  def __init__(self):
    self.s3 = myboto.s3(AWS_FILE)
    self.server = SERVER
    self.token = self.get_token()
  
  def check_upload_status(self, segment_id, upload_id):
    params = {}
    dataj = self.request('GET', '/audiences/' + str(segment_id) + '/uploads/' + str(upload_id) + '.json', params)
    if dataj['finished_at'] is None:
      return -1
    return dataj
  
  def request(self, method, url, params):
    conn = httplib.HTTPSConnection(self.server)
    headers = {'Authorization': 'Basic ' + base64.b64encode(self.token + ':x')}
    conn.request(method, url, urllib.urlencode(params), headers)
    response = conn.getresponse()
    data = response.read()
    return json.loads(data)
  
  @classmethod
  def get_token(cls, cfg_section=None, cfg_file=VLSM_CRED_FILE):
    if cfg_section is None:
      xlog.deprecated('retained for backwards compatibility; should remove')
      cfg_section = 'old'
    cfg = myConfigParser.get_cfg(filename=cfg_file, section=cfg_section)
    return cfg.token
  
  def create_segment(self, segment_name, ttl = 604800):
    params = {'audience[name]': segment_name, 'audience[ttl]': ttl}
    url = '/audiences.json'
    dataj = self.request('POST', url, params)
    return dataj['id']
  
  def set_upload_path(self, segment_id, file_name):
    params = {'upload[path]': file_name}
    url = '/audiences/{0}/uploads/custom.json'.format(segment_id)
    dataj = self.request('POST', url, params)
    if 'id' in dataj:
      return dataj['id']
    elif 'errors' in dataj:
      return dataj['errors']
    else:
      return -1
  
  # TODO: create a more generic DB for managing uploads to VLSM
  def get_config(self, whdb):
    sql = """select id, bluekai_category_id, bluekai_category_name, vlsm_segment_id, vlsm_segment_ttl, audience_last_uploaded, audience_last_pushed from dim_bluekai_categories"""
    result_set = whdb.fetchall_dict(sql)
    config = {}
    for row in result_set:
      config[row['id']] = row
    return config

