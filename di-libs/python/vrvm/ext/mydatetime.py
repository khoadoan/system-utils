#!/usr/bin/env python

import argparse
from datetime import date, datetime, timedelta
import logging

DATE_FORMAT = '%Y-%m-%d'

logger = logging.getLogger(__name__)


class mydate(date):
  date_format = DATE_FORMAT
  
  @classmethod
  def fromdate(cls, d):
    return cls(d.year, d.month, d.day)
  
  @classmethod
  def fromstring(cls, s):
    d = datetime.strptime(s, cls.date_format).date()
    return cls.fromdate(d)
  
  @classmethod
  def yesterday(cls):
    return cls.today() - 1
  
  def __str__(self):
    return self.strftime(self.date_format)
  
  def __add__(self, other):
    if isinstance(other, int):
      d = super(mydate, self).__add__(timedelta(other))
    else:
      d = super(mydate, self).__add__(other)
    return self.fromdate(d)
  
  def __sub__(self, other):
    if isinstance(other, int):
      d = super(mydate, self).__sub__(timedelta(other))
      return self.fromdate(d)
    else:
      return super(mydate, self).__sub__(other)
  
  def prev(self):
    return self.fromdate(self - 1)
  
  def next(self):
    return self.fromdate(self + 1)


def day_parser(desc, default_day=mydate.yesterday()):
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('--day', type=mydate.fromstring, default=default_day, help=DATE_FORMAT)
  args = parser.parse_args()
  return args


def daterange_parser(desc, default_start=mydate.yesterday()):
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('--start_date', type=mydate.fromstring, default=default_start, help=DATE_FORMAT)
  parser.add_argument('--end_date', type=mydate.fromstring, help='{0}, defaults to start_date'.format(DATE_FORMAT))
  args = parser.parse_args()
  if args.end_date == None:
    args.end_date = args.start_date
  return args


def daterange(start_date, end_date):
  if isinstance(start_date, basestring):
    start_date = mydate.fromstring(start_date)
    end_date = mydate.fromstring(end_date)
  if start_date <= end_date:
    for n in range((end_date - start_date).days + 1):
      yield start_date + n
  else:
    for n in range((start_date - end_date).days + 1):
      yield start_date - n

