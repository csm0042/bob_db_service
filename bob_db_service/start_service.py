#!/usr/bin/python3
""" start_service.py: """

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
from contextlib import suppress
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_db_service.configure import ConfigureService
from bob_db_service.service_main import MainTask
from bob_db_service.tools.ref_num import RefNum
from bob_db_service.tools.message_handlers import MessageHandler



# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Application wide objects ****************************************************
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file = os.path.join(parent_path, 'config.ini')
print("\n\nUsing Config file:\n" + config_file + "\n\n")
SERVICE_CONFIG = ConfigureService(config_file)
LOGGER = SERVICE_CONFIG.get_logger()
SERVICE_ADDRESSES = SERVICE_CONFIG.get_servers()
MESSAGE_TYPES = SERVICE_CONFIG.get_message_types()
CREDENTIALS = SERVICE_CONFIG.get_credentials()
DATABASE = SERVICE_CONFIG.get_database()

REF_NUM = RefNum(logger=LOGGER)
LOOP = asyncio.get_event_loop()
COMM_HANDLER = MessageHandler(LOOP, logger=LOGGER)
MAINTASK = MainTask(
    logger=LOGGER,
    ref=REF_NUM,
    db=DATABASE,
    msg_in_queue=COMM_HANDLER.msg_in_queue,
    msg_out_queue=COMM_HANDLER.msg_out_queue,
    service_addresses=SERVICE_ADDRESSES,
    message_types=MESSAGE_TYPES
)


# Main ************************************************************************
def main():
    """ Main application routine """

    LOGGER.debug('Starting main()')

    # Create incoming message server
    try:
        LOGGER.debug('Creating incoming message listening server at [%s:%s]',
                     SERVICE_ADDRESSES['database_addr'],
                     SERVICE_ADDRESSES['database_port'])
        msg_in_server = asyncio.start_server(
            COMM_HANDLER.handle_msg_in,
            host=SERVICE_ADDRESSES['database_addr'],
            port=int(SERVICE_ADDRESSES['database_port']))
        LOGGER.debug('Wrapping servier in future task and scheduling for '
                  'execution')
        msg_in_task = LOOP.run_until_complete(msg_in_server)
    except Exception:
        LOGGER.debug('Failed to create socket listening connection at %s:%s',
                     SERVICE_ADDRESSES['database_addr'],
                     SERVICE_ADDRESSES['database_port'])
        sys.exit()

    # Create main task for this service
    LOGGER.debug('Scheduling main task for execution')
    asyncio.ensure_future(MAINTASK.run())

    # Create outgoing message task
    LOGGER.debug('Scheduling outgoing message task for execution')
    asyncio.ensure_future(COMM_HANDLER.handle_msg_out())

    # Serve requests until Ctrl+C is pressed
    LOGGER.info('Database Persistance Service')
    LOGGER.info('Serving on {}'.format(msg_in_task.sockets[0].getsockname()))
    LOGGER.info('Press CTRL+C to exit')
    try:
        LOOP.run_forever()
    except asyncio.CancelledError:
        LOGGER.info('All tasks have been cancelled')
    except KeyboardInterrupt:
        pass
    finally:
        LOGGER.info('Shutting down incoming message server')
        msg_in_server.close()
        LOGGER.info('Finding all running tasks to shut down')
        pending = asyncio.Task.all_tasks()
        LOGGER.info('[%s] Task still running.  Closing them now', str(len(pending)))
        for i, task in enumerate(pending):
            with suppress(asyncio.CancelledError):
                LOGGER.info('Waiting for task [%s] to shut down', i)
                task.cancel()
                LOOP.run_until_complete(task)
        LOGGER.info('Shutdown complete.  Terminating execution loop')

    # Terminate the execution loop
    LOOP.close()


# Call Main *******************************************************************
if __name__ == "__main__":
    main()
