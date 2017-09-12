#!/usr/bin/python3
""" service_main.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import datetime
import logging
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rpihome_v3.database_service.msg_processing import create_heartbeat_msg
from rpihome_v3.database_service.msg_processing import process_heartbeat_msg
from rpihome_v3.database_service.msg_processing import process_log_status_update_msg
from rpihome_v3.database_service.msg_processing import process_return_command_msg
from rpihome_v3.database_service.msg_processing import process_update_command_msg
from rpihome_v3.messages.return_command import ReturnCommandMessage



# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Internal Service Work Task **************************************************
class MainTask(object):
    def __init__(self, log, **kwargs):
        # Configure logger
        self.log = log or logging.getLogger(__name__)
        # Define instance variables
        self.ref_num = None
        self.database = None
        self.msg_in_queue = None
        self.msg_out_queue = None
        self.service_addresses = []
        self.message_types = []
        self.last_check_db = datetime.datetime.now()
        self.last_check_hb = datetime.datetime.now()
        self.out_msg = str()
        self.out_msg_list = []
        self.next_msg = str()
        self.next_msg_split = []
        self.msg_source_addr = str()
        self.msg_type = str()
        self.destinations = []
        # Map input variables
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == "ref":
                    self.ref_num = value
                    self.log.debug('Ref number generator set during __init__ '
                                   'to: %s', self.ref_num)
                if key == "db":
                    self.database = value
                    self.log.debug('Database set during __init__ '
                                   'to: %s', self.database)
                if key == "msg_in_queue":
                    self.msg_in_queue = value
                    self.log.debug('Message in queue set during __init__ '
                                   'to: %s', self.msg_in_queue)
                if key == "msg_out_queue":
                    self.msg_out_queue = value
                    self.log.debug('Message out queue set during __init__ '
                                   'to: %s', self.msg_out_queue)
                if key == "service_addresses":
                    self.service_addresses = value
                    self.log.debug('Service address list set during __init__ '
                                   'to: %s', self.service_addresses)
                if key == "message_types":
                    self.message_types = value
                    self.log.debug('Message type list set during __init__ '
                                   'to: %s', self.message_types)


    @asyncio.coroutine
    def run(self):
        """ task to handle the work the service is intended to do """
        self.log.info('Starting database service main task')

        while True:
            # Initialize result list
            self.out_msg_list = []

            # INCOMING MESSAGE HANDLING
            if self.msg_in_queue.qsize() > 0:
                self.log.debug('Getting Incoming message from queue')
                self.next_msg = self.msg_in_queue.get_nowait()
                self.log.debug('Message pulled from queue: [%s]', self.next_msg)

                # Determine message type
                self.next_msg_split = self.next_msg.split(',')
                if len(self.next_msg_split) >= 6:
                    self.log.debug('Extracting source address and message type')
                    self.msg_source_addr = self.next_msg_split[1]
                    self.msg_type = self.next_msg_split[5]
                    self.log.debug('Source Address: %s', self.msg_source_addr)
                    self.log.debug('Message Type: %s', self.msg_type)

                # Process heartbeat from remote service
                if self.msg_type == self.message_types['heartbeat']:
                    self.log.debug('Message is a heartbeat')
                    self.out_msg_list = process_heartbeat_msg(
                        self.log,
                        self.ref_num,
                        self.next_msg,
                        self.message_types)

                # Log Device status updates to database
                if self.msg_type == self.message_types['log_status_update']:
                    self.log.debug('Message is a log status update')
                    self.out_msg_list = yield from process_log_status_update_msg(
                        self.log,
                        self.ref_num,
                        self.database,
                        self.next_msg,
                        self.message_types)

                # Query for unprocessed device commands
                if self.msg_type == self.message_types['return_command']:
                    self.log.debug('Message is a return command')
                    self.out_msg_list = yield from process_return_command_msg(
                        self.log,
                        self.ref_num,
                        self.database,
                        self.next_msg,
                        self.message_types)

                # Mark completed device commands as processed
                if self.msg_type == self.message_types['update_command']:
                    self.log.debug('Message is a update command')
                    self.out_msg_list = yield from process_update_command_msg(
                        self.log,
                        self.ref_num,
                        self.database,
                        self.next_msg,
                        self.message_types)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log.debug('Queueing response message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(self.out_msg)
                        self.log.debug('Response message [%s] successfully queued',
                                       self.out_msg)


            # PERIODIC TASKS
            # Periodically send heartbeats to other services
            if datetime.datetime.now() >= (self.last_check_hb + datetime.timedelta(seconds=120)):
                self.destinations = [
                    (self.service_addresses['automation_addr'], self.service_addresses['automation_port'])
                ]
                self.out_msg_list = create_heartbeat_msg(
                    self.log,
                    self.ref_num,
                    self.destinations,
                    self.service_addresses['database_addr'],
                    self.service_addresses['database_port'],
                    self.message_types)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log.debug('Queueing message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(self.out_msg)
                        self.log.debug('Message [%s] successfully queued', self.out_msg)

                # Update last-check
                self.last_check_hb = datetime.datetime.now()


            # PERIODIC TASKS
            # Periodically check for pending commands
            if datetime.datetime.now() >= (self.last_check_db + datetime.timedelta(seconds=1)):
                # Device command not yet processed query
                self.log.debug('Performing periodic check of pending commands')
                self.out_msg_list = yield from process_return_command_msg(
                    self.log,
                    self.ref_num,
                    self.database,
                    ReturnCommandMessage(
                        dest_addr=self.service_addresses['database_addr'],
                        dest_port=self.service_addresses['database_port'],
                        source_addr=self.service_addresses['automation_addr'],
                        source_port=self.service_addresses['automation_port'],
                        msg_type=self.message_types['return_command']
                    ).complete,
                    self.message_types)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log.debug('Queueing response message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(self.out_msg)
                        self.log.debug('Response message [%s] successfully queued',
                                       self.out_msg)

                # Update timestamp
                self.last_check_db = datetime.datetime.now()


            # Yield to other tasks for a while
            yield from asyncio.sleep(0.25)
