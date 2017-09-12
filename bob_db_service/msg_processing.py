#!/usr/bin/python3
""" interface_to_database.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import copy
import datetime
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rpihome_v3.messages.heartbeat import HeartbeatMessage
from rpihome_v3.messages.heartbeat_ack import HeartbeatMessageACK
from rpihome_v3.messages.log_status_update import LogStatusUpdateMessage
from rpihome_v3.messages.log_status_update_ack import LogStatusUpdateMessageACK
from rpihome_v3.messages.return_command import ReturnCommandMessage
from rpihome_v3.messages.return_command_ack import ReturnCommandMessageACK
from rpihome_v3.messages.update_command import UpdateCommandMessage
from rpihome_v3.messages.update_command_ack import UpdateCommandMessageACK
from rpihome_v3.database_service.persistance import insert_record
from rpihome_v3.database_service.persistance import query_command
from rpihome_v3.database_service.persistance import update_command


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


def create_heartbeat_msg(log, ref_num, destinations, source_addr, source_port, message_types):
    """ function to create one or more heartbeat messages """
    # Initialize result list
    out_msg_list = []

    # Generate a heartbeat message for each destination given
    for entry in destinations:
        out_msg = HeartbeatMessage(
            log=log,
            ref=ref_num.new(),
            dest_addr=entry[0],
            dest_port=entry[1],
            source_addr=source_addr,
            source_port=source_port,
            msg_type=message_types['heartbeat']
        )
        # Load message into output list
        log.debug('Loading completed msg: %s', out_msg.complete)
        out_msg_list.append(out_msg.complete)

    # Return response message
    return out_msg_list


def process_heartbeat_msg(log, ref_num, msg, message_types):
    """ function to ack wake-up requests to wemo service """
    # Initialize result list
    out_msg_list = []

    # Map message into wemo wake-up message class
    message = HeartbeatMessage(log=log)
    message.complete = msg

    # Send response indicating query was executed
    log.debug('Building response message header')
    out_msg = HeartbeatMessageACK(
        log=log,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['heartbeat_ack'])

    # Load message into output list
    log.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(out_msg.complete)

    # Return response message
    return out_msg_list


# Process log status update message *******************************************
@asyncio.coroutine
def process_log_status_update_msg(log, ref_num, database, msg, message_types):
    """ When a LSU message is received, log the contents of the message to
        the database
    """
    # Initialize result list
    out_msg_list = []

    # Map message header & payload to usable tags
    message = LogStatusUpdateMessage(log=log)
    message.complete = msg

    # Execute Insert Query
    log.debug('Logging status change message to database: %s',
              message.complete)
    insert_record(
        log,
        database,
        message.dev_name,
        message.dev_status,
        message.dev_last_seen)

    # Send response indicating query was executed
    log.debug('Generating LSU ACK message')
    out_msg = LogStatusUpdateMessageACK(
        log=log,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['log_status_update_ack'],
        dev_name=message.dev_name)

    # Load message into output list
    log.debug('Loading completed msg: %s', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list


# Process return command message **********************************************
@asyncio.coroutine
def process_return_command_msg(log, ref_num, database, msg, message_types):
    """ When a RC message is received, check the database for any pending
        commands
    """
    # Initialize result list
    out_msg_list = []
    result_list = []

    # Map message header & payload to usable tags
    message = ReturnCommandMessage(log=log)
    message.complete = msg

    # Execute select Query
    log.debug('Querying database for pending device commands')
    result_list = query_command(
        log,
        database)

    # Send response message for each record returned by query
    if len(result_list) > 0:
        log.debug('Preparing response messages for pending commands')
        for pending_cmd in result_list:
            # Split pending command into separate parts
            pending_cmd_seg = pending_cmd.split(',')
            # Create message RC ACK message to automation service
            if len(pending_cmd_seg) >= 5:
                out_msg = ReturnCommandMessageACK(
                    log=log,
                    ref=ref_num.new(),
                    dest_addr=message.source_addr,
                    dest_port=message.source_port,
                    source_addr=message.dest_addr,
                    source_port=message.dest_port,
                    msg_type=message_types['return_command_ack'],
                    dev_id=copy.copy(pending_cmd_seg[0]),
                    dev_name=copy.copy(pending_cmd_seg[1]),
                    dev_cmd=copy.copy(pending_cmd_seg[2]),
                    dev_timestamp=copy.copy(pending_cmd_seg[3]),
                    dev_processed=copy.copy(pending_cmd_seg[4]))

                # Load message into output list
                log.debug('Loading completed msg: %s', out_msg.complete)
                out_msg_list.append(out_msg.complete)
            else:
                log.warning('Invalid command received from DB: %s', pending_cmd)
    else:
        log.debug('No pending commands found')

    # Return list of response messages from query
    return out_msg_list


# Process update command message **********************************************
@asyncio.coroutine
def process_update_command_msg(log, ref_num, database, msg, message_types):
    """ When a UC message is received, perform an update query on the database
        to mark the original command as processed
    """
    # Initialize result list
    out_msg_list = []

    # Map message header & payload to usable tags
    message = UpdateCommandMessage(log=log)
    message.complete = msg

    # Update timestamp
    message.dev_processed = datetime.datetime.now()

    # Execute update Query
    log.debug('Querying database to mark command as processed: %s',
              message.complete)
    update_command(
        log,
        database,
        message.dev_id,
        message.dev_processed)

    # Send response indicating query was executed
    log.debug('Generating UC ACK message')
    out_msg = UpdateCommandMessageACK(
        log=log,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['update_command_ack'],
        dev_id=message.dev_id)

    # Load message into output list
    log.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(out_msg.complete)

    # Return response message
    return out_msg_list
