#!/usr/bin/python3
""" persistance.py: Provides required interfaces to the MySql database for this
application.  The following functions are supported here:
1) insert record into device_log table
2) query commands from device_cmd table
3) update records as processed in device_cmd table
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import logging


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The rpihome Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Insert Record into log table in database function ***************************
def insert_record(logger, database, name, status, last_seen):
    """ Inserts a new record into the device log table """
    # Configure logger
    logger = logger or logging.getLogger(__name__)
    logger.debug('insert_record function has been called')

    # Attempt database record insert
    try:
        # Check first if valid database connection was made
        if database is not None:
            logger.debug('Connection to database is ok')
            cursor = database.cursor()
            logger.debug('Connection to cursor successful')
            query = ("INSERT INTO device_log "
                     "(device, status, timestamp) "
                     "VALUES (%s, %s, %s)")
            data = (name, status, str(last_seen))
            full_query = query % data
            logger.debug('Ready to execute query: %s', full_query)
            cursor.execute(query, data)
            logger.debug('Query execution successful')
        else:
            logger.warning('No connection to database')
    except Exception:
        logger.warning('Attempt to inesrt record into database failed')
    finally:
        database.commit()
        logger.debug('Changed committed to database')
        cursor.close()
        logger.debug('Closed connection to database cursor')


# Return pending commands from device_cmd table function **********************
def query_command(logger, database):
    """ Returns a list of un-processed commands from the device_cmd table """
    # Configure logger
    logger = logger or logging.getLogger(__name__)
    logger.debug('query_command function has been called')

    # initialize result list
    result_list = []

    # Attempt database record insert
    try:
        # Check first if valid database connection was made
        if database is not None:
            logger.debug('Connection to database is ok')
            # Grab cursor and prepare query
            cursor = database.cursor()
            logger.debug('Connection to cursor successful')

            query = "SELECT id_device_cmd, device, cmd, timestamp, processed " \
                    "FROM device_cmd " \
                    "WHERE processed Is NULL " \
                    "AND (device, timestamp) " \
                    "IN (SELECT device, Max(timestamp) " \
                    "FROM device_cmd GROUP BY device) LIMIT 5"

            logger.debug('Ready to execute query: %s', query)
            cursor.execute(query)
            logger.debug('Query execution successful')
            row = cursor.fetchone()
            while row is not None:
                logger.debug('Building result')
                result = '%s,%s,%s,%s,%s' % (row[0], row[1], row[2], row[3], row[4])
                logger.debug('Found pending cmd: [%s]', result)
                result_list.append(copy.copy(result))
                logger.debug('Fetching next record in cursor')
                row = cursor.fetchone()
            logger.debug('Select query complete')
        else:
            logger.warning('No connection to database')
    except Exception:
        logger.warning('Attempt to query database failed')
    finally:
        database.commit()
        logger.debug('Changed committed to database')
        cursor.close()
        logger.debug('Closed connection to database cursor')

    # Return results
    return result_list


# Update processed status of commands in device_cmd table function ************
def update_processed(logger, database, id_cmd, processed_cmd):
    """ Updates processed field for an individual record in the device
    cmd table """
    # Configure logger
    logger = logger or logging.getLogger(__name__)
    logger.debug('update_command function has been called')

    # Attempt database record insert
    try:
        # Check first if valid database connection was made
        if database is not None:
            logger.debug('Connection to database is ok')

            # Grab cursor and prepare query
            cursor = database.cursor()
            logger.debug('Connection to cursor successful')
            query = ("UPDATE device_cmd "
                     "SET processed = %s "
                     "WHERE id_device_cmd = %s")
            data = (processed_cmd[:19], id_cmd)
            full_query = query % data
            logger.debug('Ready to execute query: %s', full_query)
            cursor.execute(query, data)
            logger.debug('Query execution successful')
        else:
            logger.warning('No connection to database')
    except Exception:
        logger.warning('Attempt to query database failed')
    finally:
        database.commit()
        logger.debug('Changed committed to database')
        cursor.close()
        logger.debug('Closed connection to database cursor')


# Update processed status of commands in device_cmd table function ************
def update_executed(logger, database, id_cmd, processed_cmd):
    """ Updates processed field for an individual record in the device
    cmd table """
    # Configure logger
    logger = logger or logging.getLogger(__name__)
    logger.debug('update_command function has been called')

    # Attempt database record insert
    try:
        # Check first if valid database connection was made
        if database is not None:
            logger.debug('Connection to database is ok')

            # Grab cursor and prepare query
            cursor = database.cursor()
            logger.debug('Connection to cursor successful')
            query = ("UPDATE device_cmd "
                     "SET executed = %s "
                     "WHERE id_device_cmd = %s")
            data = (processed_cmd[:19], id_cmd)
            full_query = query % data
            logger.debug('Ready to execute query: %s', full_query)
            cursor.execute(query, data)
            logger.debug('Query execution successful')
        else:
            logger.warning('No connection to database')
    except Exception:
        logger.warning('Attempt to query database failed')
    finally:
        database.commit()
        logger.debug('Changed committed to database')
        cursor.close()
        logger.debug('Closed connection to database cursor')
