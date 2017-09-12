#!/usr/bin/python3
""" test_msg_processing.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import configparser
import copy
import datetime
import logging
import os
import sys
import unittest
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rpihome_v3.helpers.ref_num import RefNum
from rpihome_v3.database_service.configure import ConfigureService
from rpihome_v3.database_service.msg_processing import create_heartbeat_msg
from rpihome_v3.database_service.msg_processing import process_heartbeat_msg
from rpihome_v3.database_service.msg_processing import process_log_status_update_msg
from rpihome_v3.database_service.msg_processing import process_return_command_msg
from rpihome_v3.database_service.msg_processing import process_update_command_msg


# Define test class ***********************************************************
class Test_message_processing_db(unittest.TestCase):
    """ unittests for Device Class, methods, and functions """

    def __init__(self, *args, **kwargs):
        # Configure logging
        logging.basicConfig(stream=sys.stdout)
        self.log = logging.getLogger(__name__)
        self.log.level = logging.DEBUG
        # Create tags for testing
        self.msg_in = str()
        self.msg_out = []
        self.ref_num = RefNum(self.log)
        self.last_ref_num = int()
        self.temp_dt = datetime.datetime
        self.destinations = []
        # Create items that will come from config file
        self.parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_file = os.path.join(self.parent_path, 'config.ini')
        self.config = ConfigureService(self.config_file)
        self.service_addresses = self.config.get_servers()
        self.message_types = self.config.get_message_types()
        self.credentials = self.config.get_credentials()
        self.database = self.config.get_database()
        # Call parent class init
        super(Test_message_processing_db, self).__init__(*args, **kwargs)


    def setUp(self):
        # call parent class setup
        super(Test_message_processing_db, self).setUp()


    def test_init(self):
        """ test class __init__ and input variables """
        pass


    def test_create_heartbeat_msg(self):
        """ test correct outputs result from various inputs """
        # Capture initial ref number
        self.last_ref_num = int(self.ref_num.source)
        # Create list of inputs to test with
        self.destinations = [
            (self.service_addresses['database_addr'], self.service_addresses['database_port']),
            (self.service_addresses['motion_addr'], self.service_addresses['motion_port']),
            (self.service_addresses['nest_addr'], self.service_addresses['nest_port']),
            (self.service_addresses['occupancy_addr'], self.service_addresses['occupancy_port']),
            (self.service_addresses['schedule_addr'], self.service_addresses['schedule_port']),
            (self.service_addresses['wemo_addr'], self.service_addresses['wemo_port'])
        ]
        # call function
        self.msg_out = create_heartbeat_msg(
            self.log,
            self.ref_num,
            self.destinations,
            self.service_addresses['database_addr'],
            self.service_addresses['database_port'],
            self.message_types)
        # check output
        self.assertEqual(len(self.msg_out), 6)
        for i, j in enumerate(self.msg_out):
            self.msg_out_split = j.split(",")
            self.assertNotEqual(self.msg_out_split[0], self.last_ref_num)
            self.assertEqual(self.msg_out_split[1], self.destinations[i][0])
            self.assertEqual(self.msg_out_split[2], self.destinations[i][1])
            self.assertEqual(self.msg_out_split[3], self.service_addresses['database_addr'])
            self.assertEqual(self.msg_out_split[4], self.service_addresses['database_port'])
            self.assertEqual(self.msg_out_split[5], self.message_types['heartbeat'])


    def test_process_heartbeat_msg(self):
        """ test correct outputs result from various inputs """
        # Create test input message
        self.msg_in = self.ref_num.new() + "," \
                      + "127.3.3.1,27005," \
                      + "127.4.4.1,28000," \
                      + self.message_types['heartbeat_ack']
        # call function
        self.msg_out = process_heartbeat_msg(
            self.log,
            self.ref_num,
            self.msg_in,
            self.message_types)
        # check output
        self.assertEqual(len(self.msg_out), 1)
        self.msg_out_split = self.msg_out[0].split(",")
        self.assertEqual(self.msg_out_split[0], self.ref_num.source)
        self.assertEqual(self.msg_out_split[1], '127.4.4.1')
        self.assertEqual(self.msg_out_split[2], '28000')
        self.assertEqual(self.msg_out_split[3], '127.3.3.1')
        self.assertEqual(self.msg_out_split[4], '27005')
        self.assertEqual(
            self.msg_out_split[5], self.message_types['heartbeat_ack'])


    def test_process_log_status_update_msg(self):
        """ test correct outputs result from various inputs """
        # Create test input message
        self.ts = str(datetime.datetime.now())[:19]
        self.msg_in = self.ref_num.new() + "," \
                      + "127.0.0.1,27011," \
                      + "127.0.0.1,27001," \
                      + self.message_types['log_status_update'] \
                      + ",test_dev,192.168.99.99,on," \
                      + self.ts
        # call function
        self.msg_out = yield from process_log_status_update_msg(
            self.log,
            self.ref_num,
            self.database,
            self.msg_in,
            self.message_types)
        # check output
        self.assertEqual(len(self.msg_out), 1)
        self.msg_out_split = self.msg_out[0].split(",")
        self.assertEqual(self.msg_out_split[0], self.ref_num.source)
        self.assertEqual(self.msg_out_split[1], '127.0.0.1')
        self.assertEqual(self.msg_out_split[2], '27001')
        self.assertEqual(self.msg_out_split[3], '127.0.0.1')
        self.assertEqual(self.msg_out_split[4], '27011')
        self.assertEqual(
            self.msg_out_split[5],
            self.message_types['log_status_update_ack']
        )
        self.assertEqual(self.msg_out_split[6], 'test_dev')


    def test_process_return_command_msg(self):
        """ test correct outputs result from various inputs """
        # Create test input message
        self.ts = str(datetime.datetime.now())[:19]
        self.msg_in = self.ref_num.new() + "," \
                      + "127.0.0.1,27011," \
                      + "127.0.0.1,27001," \
                      + self.message_types['log_status_update'] \
                      + ",test_dev,192.168.99.99,on," \
                      + self.ts
        # call function
        self.msg_out = yield from process_process_return_command_msg(
            self.log,
            self.ref_num,
            self.database,
            self.msg_in,
            self.message_types)
        # check output
        self.assertEqual(len(self.msg_out), 1)
        self.msg_out_split = self.msg_out[0].split(",")
        self.assertEqual(self.msg_out_split[0], self.ref_num.source)
        self.assertEqual(self.msg_out_split[1], '127.0.0.1')
        self.assertEqual(self.msg_out_split[2], '27001')
        self.assertEqual(self.msg_out_split[3], '127.0.0.1')
        self.assertEqual(self.msg_out_split[4], '27011')
        self.assertEqual(
            self.msg_out_split[5],
            self.message_types['log_status_update_ack']
        )
        self.assertEqual(self.msg_out_split[6], 'test_dev')


if __name__ == "__main__":
    unittest.main()
