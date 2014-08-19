#!/usr/bin/env python

import logging
import sys

import boto.sqs.connection
import boto.sqs.message

logger = logging.getLogger(__name__)


def send(sqs_conn, queue, message):
  q = sqs_conn.create_queue(queue)
  m = boto.sqs.message.Message()
  m.set_body(message)
  if not q.write(m):
    raise Exception('Cannot write message to SQS. Queue: {0}, Message: {1}'.format(queue, message))
  print 'Wrote message to SQS. Queue: {0}, Message: {1}'.format(queue, message)


# args: queue message
def main():
  sqs_conn = boto.sqs.connection.SQSConnection()
  send(sqs_conn, sys.argv[1], sys.argv[2])


if __name__ == '__main__':
  main()

