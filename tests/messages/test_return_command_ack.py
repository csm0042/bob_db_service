#!/usr/bin/python3
""" test_message_ccs_ack.py:
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
from bob_db_service.messages.return_command_ack import ReturnCommandMessageACK


# Define test class ***********************************************************
class TestReturnCommandMessageACK(unittest.TestCase):
    """ unittests for Log Status Update Message Class """

    def __init__(self, *args, **kwargs):
        logging.basicConfig(stream=sys.stdout)
        self.log = logging.getLogger(__name__)
        self.log.level = logging.DEBUG
        self.datetime = datetime.datetime
        self.datetime_str = str()
        super(TestReturnCommandMessageACK, self).__init__(*args, **kwargs)


    def setUp(self):
        self.message = ReturnCommandMessageACK(log=self.log)
        super(TestReturnCommandMessageACK, self).setUp()


    def test_init(self):
        """ test class __init__ and input variables """
        self.datetime = datetime.datetime.combine(
            datetime.date(2017, 8, 5),
            datetime.time(9, 10)
        )
        self.datetime_str = '2017-08-05 09:10:00'
        self.message = ReturnCommandMessageACK(
            log=self.log,
            ref='101',
            dest_addr='192.168.86.1',
            dest_port='17061',
            source_addr='192.168.5.4',
            source_port='12000',
            msg_type='601',
            dev_id='4',
            dev_name='fylt1',
            dev_cmd='on',
            dev_timestamp=self.datetime,
            dev_processed=self.datetime_str
        )

        self.assertEqual(self.message.ref, '101')
        self.assertEqual(self.message.dest_addr, '192.168.86.1')
        self.assertEqual(self.message.dest_port, '17061')
        self.assertEqual(self.message.source_addr, '192.168.5.4')
        self.assertEqual(self.message.source_port, '12000')
        self.assertEqual(self.message.msg_type, '601')
        self.assertEqual(self.message.dev_id, '4')        
        self.assertEqual(self.message.dev_name, 'fylt1')
        self.assertEqual(self.message.dev_cmd, 'on')
        self.assertEqual(self.message.dev_timestamp, self.datetime_str)
        self.assertEqual(self.message.dev_processed, self.datetime_str)


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


    def test_message_type(self):
        """ test setting and getting message type field """
        self.message.msg_type = 101
        self.assertEqual(self.message.msg_type, '101')
        self.message.msg_type = '102'
        self.assertEqual(self.message.msg_type, '102')


    def test_device_id(self):
        """ test setting and getting message type field """
        self.message.dev_id = 101
        self.assertEqual(self.message.dev_id, '101')
        self.message.dev_id = '102'
        self.assertEqual(self.message.dev_id, '102')        


    def test_device_name(self):
        """ test setting and getting device name field """
        self.message.dev_name = 101
        self.assertEqual(self.message.dev_name, '101')
        self.message.dev_name = 'fylt1'
        self.assertEqual(self.message.dev_name, 'fylt1')


    def test_dev_cmd(self):
        """ test setting and getting device command field """
        self.message.dev_cmd = 'off'
        self.assertEqual(self.message.dev_cmd, 'off')
        self.message.dev_cmd = '1'
        self.assertEqual(self.message.dev_cmd, '1')


    def test_dev_timestamp(self):
        """ test setting and getting device command timestamp field """
        self.datetime = datetime.datetime.combine(
            datetime.date(2017, 9, 5),
            datetime.time(9, 10)
        )
        self.datetime_str = '2017-09-05 09:10:00'
        self.message.dev_timestamp = self.datetime
        self.assertEqual(self.message.dev_timestamp, self.datetime_str)
        self.datetime_str = '2017-08-04 09:10:03'
        self.message.dev_timestamp = '2017-08-04 09:10:03'
        self.assertEqual(self.message.dev_timestamp, self.datetime_str)


    def test_dev_processed(self):
        """ test setting and getting device command processed field """
        self.datetime = datetime.datetime.combine(
            datetime.date(2017, 9, 5),
            datetime.time(9, 10)
        )
        self.datetime_str = '2017-09-05 09:10:00'
        self.message.dev_processed = self.datetime
        self.assertEqual(self.message.dev_processed, self.datetime_str)
        self.datetime_str = '2017-08-04 09:10:03'
        self.message.dev_processed = '2017-08-04 09:10:03'
        self.assertEqual(self.message.dev_processed, self.datetime_str)             


    def test_complete(self):
        self.temp_str = '142,127.0.0.1,12000,192.168.5.45,13000,' \
                        '301,5,device01,on,2017-10-04 07:01:03.000034,'
        self.temp_str2 = '142,127.0.0.1,12000,192.168.5.45,13000,' \
                        '301,5,device01,on,2017-10-04 07:01:03,'
        self.message.complete = copy.copy(self.temp_str)
        self.assertEqual(self.message.ref, '142')
        self.assertEqual(self.message.dest_addr, '127.0.0.1')
        self.assertEqual(self.message.dest_port, '12000')
        self.assertEqual(self.message.source_addr, '192.168.5.45')
        self.assertEqual(self.message.source_port, '13000')
        self.assertEqual(self.message.msg_type, '301')
        self.assertEqual(self.message.dev_id, '5')        
        self.assertEqual(self.message.dev_name, 'device01')
        self.assertEqual(self.message.dev_cmd, 'on')
        self.assertEqual(self.message.dev_timestamp, '2017-10-04 07:01:03')
        self.assertEqual(self.message.dev_processed, '')
        self.assertEqual(self.message.complete, self.temp_str2)

        self.temp_str = '142,127.0.x.1,12002,192.168.5.45,13000,' \
                        '301,5,device01,on,2017-10-04 07:01:04.000034,' \
                        '2017-10-05 08:00:00'
        self.temp_str2 = '142,127.0.0.1,12002,192.168.5.45,13000,' \
                        '301,5,device01,on,2017-10-04 07:01:04,' \
                        '2017-10-05 08:00:00'
        self.message.complete = copy.copy(self.temp_str)
        self.assertEqual(self.message.ref, '142')
        self.assertEqual(self.message.dest_addr, '127.0.0.1')
        self.assertEqual(self.message.dest_port, '12002')
        self.assertEqual(self.message.source_addr, '192.168.5.45')
        self.assertEqual(self.message.source_port, '13000')
        self.assertEqual(self.message.msg_type, '301')
        self.assertEqual(self.message.dev_id, '5')        
        self.assertEqual(self.message.dev_name, 'device01')
        self.assertEqual(self.message.dev_cmd, 'on')
        self.assertEqual(self.message.dev_timestamp, '2017-10-04 07:01:04')
        self.assertEqual(self.message.dev_processed, '2017-10-05 08:00:00')
        self.assertEqual(self.message.complete, self.temp_str2)       


if __name__ == "__main__":
    unittest.main()
