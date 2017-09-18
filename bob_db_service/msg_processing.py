#!/usr/bin/python3
""" interface_to_database.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import copy
import datetime
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_db_service.messages.heartbeat import HeartbeatMessage
from bob_db_service.messages.heartbeat_ack import HeartbeatMessageACK
from bob_db_service.messages.log_status_update import LogStatusUpdateMessage
from bob_db_service.messages.log_status_update_ack import LogStatusUpdateMessageACK
from bob_db_service.messages.return_command import ReturnCommandMessage
from bob_db_service.messages.return_command_ack import ReturnCommandMessageACK
from bob_db_service.messages.update_command import UpdateCommandMessage
from bob_db_service.messages.update_command_ack import UpdateCommandMessageACK
from bob_db_service.persistance import insert_record
from bob_db_service.persistance import query_command
from bob_db_service.persistance import update_processed
from bob_db_service.persistance import update_executed


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


def create_heartbeat_msg(logger, ref_num, destinations, source_addr, source_port, message_types):
    """ function to create one or more heartbeat messages """
    # Configure logger
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Generate a heartbeat message for each destination given
    for entry in destinations:
        out_msg = HeartbeatMessage(
            logger=logger,
            ref=ref_num.new(),
            dest_addr=entry[0],
            dest_port=entry[1],
            source_addr=source_addr,
            source_port=source_port,
            msg_type=message_types['heartbeat']
        )
        # Load message into output list
        logger.debug('Loading completed msg: %s', out_msg.complete)
        out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list


def process_heartbeat_msg(logger, ref_num, msg, message_types):
    """ function to ack wake-up requests to wemo service """
    # Configure logger
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into wemo wake-up message class
    message = HeartbeatMessage(logger=logger)
    message.complete = msg

    # Send response indicating query was executed
    logger.debug('Building response message header')
    out_msg = HeartbeatMessageACK(
        logger=logger,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['heartbeat_ack'])

    # Load message into output list
    logger.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list


# Process log status update message *******************************************
@asyncio.coroutine
def process_log_status_update_msg(logger, ref_num, database, msg, message_types):
    """ When a LSU message is received, log the contents of the message to
        the database
    """
    # Configure logger
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message header & payload to usable tags
    message = LogStatusUpdateMessage(logger=logger)
    message.complete = msg

    # Execute Insert Query
    logger.debug('Logging status change message to database: %s',
                 message.complete)
    insert_record(
        logger,
        database,
        message.dev_name,
        message.dev_status,
        message.dev_last_seen)

    # Send response indicating query was executed
    logger.debug('Generating LSU ACK message')
    out_msg = LogStatusUpdateMessageACK(
        logger=logger,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['log_status_update_ack'],
        dev_name=message.dev_name)

    # Load message into output list
    logger.debug('Loading completed msg: %s', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list


# Process return command message **********************************************
@asyncio.coroutine
def process_return_command_msg(logger, ref_num, database, msg, message_types):
    """ When a RC message is received, check the database for any pending
        commands
    """
    # Configure logger
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []
    result_list = []

    # Map message header & payload to usable tags
    message = ReturnCommandMessage(logger=logger)
    message.complete = msg

    # Execute select Query
    logger.debug('Querying database for pending device commands')
    result_list = query_command(
        logger,
        database)

    # Send response message for each record returned by query
    if len(result_list) > 0:
        logger.debug('Preparing response messages for pending commands')
        for pending_cmd in result_list:
            # Split pending command into separate parts
            pending_cmd_seg = pending_cmd.split(',')
            # Create message RC ACK message to automation service
            if len(pending_cmd_seg) >= 5:
                out_msg = ReturnCommandMessageACK(
                    logger=logger,
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

                # Execute update Query
                logger.debug('Querying database to mark command as processed: %s',
                             message.complete)
                update_processed(
                    logger,
                    database,
                    pending_cmd_seg[0],
                    str(datetime.datetime.now())[:19])

                # Load message into output list
                logger.debug('Loading completed msg: %s', out_msg.complete)
                out_msg_list.append(copy.copy(out_msg.complete))
            else:
                logger.warning('Invalid command received from DB: %s', pending_cmd)
    else:
        logger.debug('No pending commands found')

    # Return list of response messages from query
    return out_msg_list


# Process update command message **********************************************
@asyncio.coroutine
def process_update_command_msg(logger, ref_num, database, msg, message_types):
    """ When a UC message is received, perform an update query on the database
        to mark the original command as processed
    """
    # Configure logger
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message header & payload to usable tags
    message = UpdateCommandMessage(logger=logger)
    message.complete = msg

    # Update timestamp
    message.dev_processed = datetime.datetime.now()

    # Execute update Query
    logger.debug('Querying database to mark command as processed: %s',
                 message.complete)
    update_executed(
        logger,
        database,
        message.dev_id,
        message.dev_processed)

    # Send response indicating query was executed
    logger.debug('Generating UC ACK message')
    out_msg = UpdateCommandMessageACK(
        logger=logger,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['update_command_ack'],
        dev_id=message.dev_id)

    # Load message into output list
    logger.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list
