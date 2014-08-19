#!/usr/bin/env python

import logging
from subprocess import check_call
from time import localtime, strftime

DEFAULT_SSH_ALIAS = 'verve-cc'
DEFAULT_PRIORITY = 'VERY_LOW'
DEFAULT_LOGBASE = '/var/verve/log/pig'

logger = logging.getLogger(__name__)


def remote_exec(cmd, ssh_alias=DEFAULT_SSH_ALIAS):
  # NOTE: for some commands, hangs without nohup or -n (redirects stdin from /dev/null) flag
  # TODO: ensure cmd is properly escaped
  cmd_wrapped = 'ssh {alias} -n "{cmd}"'.format(alias=ssh_alias, cmd=cmd)
  logger.debug('executing: %s', cmd_wrapped)
  out = check_call(cmd_wrapped, shell=True)
  logger.info('executed: %s', cmd_wrapped)
  return out


# TODO: probably belongs somewhere else
def build_pig_cmd(script, params={}, logname='/dev/null', priority=DEFAULT_PRIORITY):
  params = ['--param {0}={1}'.format(p[0], p[1]) for p in params.items()]
  params = ' '.join(params)
  # better to dump output to STDOUT and let caller handle?
  cmd = 'pig -Dmapred.job.priority={priority} {params} {script} >> {logname} 2>&1'.format(
    priority=priority,
    params=params,
    script=script,
    logname=logname
  )
  return cmd


def get_logname(application, logbase=DEFAULT_LOGBASE):
  # TODO: application subdirs preferred; but this breaks if subdir doesn't exist
  timestamp = strftime('%Y%m%d-%H%M%S', localtime())
  application = application.replace('=', '_').replace('/', '_')
  log = '{0}/{1}.{2}.out'.format(logbase, application, timestamp)
  return log

