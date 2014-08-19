#!/usr/bin/env python

import logging
import sys
import subprocess
import time

import boto.sqs.connection
import boto.sqs.message

logger = logging.getLogger(__name__)


def main():
  queue_name_in = sys.argv[1]
  
  sqs_conn = boto.sqs.connection.SQSConnection()
  q = sqs_conn.create_queue(queue_name_in)
  
  # TODO: refactor to use common library (see myboto.sqs)
  while True:
    current_message = q.read()
    while current_message is None:
      time.sleep(30)
      current_message = q.read()
    
    body = current_message.get_body()
    step_args = body.split('\t')
    
    pig_command = step_args[0]
    queue_name_out = step_args[1]
    completion_queue_message = step_args[2]
    
    # create a pig job with the first argument
    p = subprocess.Popen(pig_command.split('|'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    
    # send a message to the queue signaling job is done
    output_queue = sqs_conn.create_queue(queue_name_out)
    m = boto.sqs.message.Message()
    m.set_body(completion_queue_message)
    status = output_queue.write(m)
    
    q.delete_message(current_message)


if __name__ == '__main__':
  main()

