#!/usr/bin/python3
""" test_message_sds_ack.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import datetime
import logging
import os
import sys
import unittest
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bob_db_service.messages.update_command_ack import UpdateCommandMessageACK


# Define test class ***********************************************************
class TestUpdateCommandMessageACK(unittest.TestCase):
    """ unittests for Get Device Status Message Class """

    def __init__(self, *args, **kwargs):
        logging.basicConfig(stream=sys.stdout)
        self.log = logging.getLogger(__name__)
        self.log.level = logging.DEBUG
        self.temp_str = str()
        self.temp_str2 = str()
        super(TestUpdateCommandMessageACK, self).__init__(*args, **kwargs)


    def setUp(self):
        self.message = UpdateCommandMessageACK(log=self.log)
        super(TestUpdateCommandMessageACK, self).setUp()


    def test_init(self):
        """ test class __init__ and input variables """
        self.message = UpdateCommandMessageACK(
            log=self.log,
            ref='101',
            dest_addr='192.168.86.1',
            dest_port='17061',
            source_addr='192.168.5.4',
            source_port='12000',
            msg_type='601',
            dev_id='42',
        )
        self.assertEqual(self.message.ref, '101')
        self.assertEqual(self.message.dest_addr, '192.168.86.1')
        self.assertEqual(self.message.dest_port, '17061')
        self.assertEqual(self.message.source_addr, '192.168.5.4')
        self.assertEqual(self.message.source_port, '12000')
        self.assertEqual(self.message.msg_type, '601')
        self.assertEqual(self.message.dev_id, '42')


    def test_ref_number(self):
        """ test setting and getting message reference number field """
        self.message.ref = 100
        self.assertEqual(self.message.ref, '100')
        self.message.ref = '202'
        self.assertEqual(self.message.ref, '202')


    def test_dest_addr(self):
        """ test setting and getting message destination address field """
        self.message.dest_addr = '192.168.1.1'
        self.assertEqual(self.message.dest_addr, '192.168.1.1')
        self.message.dest_addr = '192.168.2.x'
        self.assertEqual(self.message.dest_addr, '192.168.1.1')


    def test_dest_port(self):
        """ test setting and getting message destination port field """
        self.message.dest_port = 11000
        self.assertEqual(self.message.dest_port, '11000')
        self.message.dest_port = '12000'
        self.assertEqual(self.message.dest_port, '12000')
        self.message.dest_port = 100
        self.assertEqual(self.message.dest_port, '12000')
        self.message.dest_port = '101'
        self.assertEqual(self.message.dest_port, '12000')
        self.message.dest_port = '100000'
        self.assertEqual(self.message.dest_port, '12000')
        self.message.dest_port = 101000
        self.assertEqual(self.message.dest_port, '12000')
        self.message.dest_port = 17061
        self.assertEqual(self.message.dest_port, '17061')
        self.message.dest_port = '?'
        self.assertEqual(self.message.dest_port, '17061')
        self.message.dest_port = 'a'
        self.assertEqual(self.message.dest_port, '17061')


    def test_source_addr(self):
        """ test setting and getting message source address field """
        self.message.source_addr = '192.168.1.1'
        self.assertEqual(self.message.source_addr, '192.168.1.1')
        self.message.source_addr = '192.168.2.x'
        self.assertEqual(self.message.source_addr, '192.168.1.1')


    def test_source_port(self):
        """ test setting and getting message source port field """
        self.message.source_port = 11000
        self.assertEqual(self.message.source_port, '11000')
        self.message.source_port = '12000'
        self.assertEqual(self.message.source_port, '12000')
        self.message.source_port = 100
        self.assertEqual(self.message.source_port, '12000')
        self.message.source_port = '101'
        self.assertEqual(self.message.source_port, '12000')
        self.message.source_port = '100000'
        self.assertEqual(self.message.source_port, '12000')
        self.message.source_port = 101000
        self.assertEqual(self.message.source_port, '12000')
        self.message.source_port = 17061
        self.assertEqual(self.message.source_port, '17061')
        self.message.source_port = '?'
        self.assertEqual(self.message.source_port, '17061')
        self.message.source_port = 'a'
        self.assertEqual(self.message.source_port, '17061')           


    def test_message_type(self):
        """ test setting and getting message type field """
        self.message.msg_type = 101
        self.assertEqual(self.message.msg_type, '101')
        self.message.msg_type = '102'
        self.assertEqual(self.message.msg_type, '102')


    def test_device_id(self):
        """ test setting and getting device name field """
        self.message.dev_id = 101
        self.assertEqual(self.message.dev_id, '101')
        self.message.dev_id = '202'
        self.assertEqual(self.message.dev_id, '202')   


    def test_complete(self):
        self.temp_str = '142,127.0.0.1,12000,192.168.5.45,13000,' \
                        '301,42'
        self.temp_str2 = '142,127.0.0.1,12000,192.168.5.45,13000,' \
                         '301,42'
        self.message.complete = copy.copy(self.temp_str)
        self.assertEqual(self.message.ref, '142')
        self.assertEqual(self.message.dest_addr, '127.0.0.1')
        self.assertEqual(self.message.dest_port, '12000')
        self.assertEqual(self.message.source_addr, '192.168.5.45')
        self.assertEqual(self.message.source_port, '13000')
        self.assertEqual(self.message.msg_type, '301')
        self.assertEqual(self.message.dev_id, '42')


if __name__ == "__main__":
    unittest.main()
