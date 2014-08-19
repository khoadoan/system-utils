#!/usr/bin/env python

import logging

logger = logging.getLogger(__name__)


@outputSchema("t:chararray")
def bagJoin(bag):
  if bag is None:
    return None
  # TODO: doesn't work because unicode?
  #strlist = [str(x[0]).translate(None, '(),') for x in bag]
  strlist = [str(x[0]).replace('(', '').replace(')', '').replace(',', '') for x in bag]
  strlist.sort()
  return ','.join(strlist);


@outputSchema("t:chararray")
def get_distance_range(x):
  try:
    d = float(x)
  except ValueError:
    return None
  
  if d <= 1: return '00-01m'
  elif d <= 2: return '01-02m'
  elif d <= 3: return '02-03m'
  elif d <= 4: return '03-04m'
  elif d <= 5: return '04-05m'
  elif d <= 6: return '05-06m'
  elif d <= 7: return '06-07m'
  elif d <= 8: return '07-08m'
  elif d <= 9: return '08-09m'
  elif d <= 10: return '09-10m'
  elif d <= 15: return '10-15m'
  elif d <= 20: return '15-20m'
  elif d <= 25: return '20-25m'
  elif d <= 30: return '25-30m'
  else: return '30+m'

