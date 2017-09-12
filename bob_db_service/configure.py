#!/usr/bin/python3
""" configure.py:
    Configuration process for the RPiHome application.
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import configparser
import logging
import sys
import mysql.connector
import mysql.connector.errorcode as errorcodes
if __name__ == "__main__":
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rpihome_v3.helpers.log_support import setup_log_handlers


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Config Function Def *********************************************************
class ConfigureService(object):
    def __init__(self, filename):
        self.filename = filename
        self.service_addresses = {}
        self.message_types = {}
        self.credentials = str()
        self.database = None
        # Define connection to configuration file
        self.config_file = configparser.ConfigParser()
        self.credential_file = configparser.ConfigParser()
        # Configure logger
        self.log = self.get_logger()


    def get_logger(self):
        # Set up application logging
        self.config_file.read(self.filename)
        self.log = setup_log_handlers(
            __file__,
            self.config_file['LOG FILES']['database_debug_log_file'],
            self.config_file['LOG FILES']['database_info_log_file'])
        # Return configured objects to main program
        return self.log


    def get_servers(self):
        # Create dict with all services defined in INI file
        self.config_file.read(self.filename)
        for option in self.config_file.options('SERVICES'):
            self.service_addresses[option] = self.config_file['SERVICES'][option]
        # Return dict of configured addresses and ports to main program
        return self.service_addresses


    def get_message_types(self):
        # Create dict with all services defined in INI file
        self.config_file.read(self.filename)
        for option in self.config_file.options('MESSAGE TYPES'):
            self.message_types[option] = self.config_file['MESSAGE TYPES'][option]
        # Return dict of configured addresses and ports to main program
        return self.message_types


    def get_credentials(self):
        # Define connection to configuration file
        self.config_file.read(self.filename)
        # Read credential info from file
        try:
            self.credentials = self.config_file['CREDENTIALS']['file']
            self.log.debug('Credentails file found')
        except:
            self.log.error('No credentials file found')
        # Return configured objects to main program
        return self.credentials


    def get_database(self):
        # Define connection to configuration file
        self.config_file.read(self.filename)
        self.credential_file.read(self.credentials)
        # Set up database connection
        try:
            self.database = mysql.connector.connect(
                host=self.config_file['DATABASE']['host'],
                port=self.config_file['DATABASE']['port'],
                database=self.config_file['DATABASE']['schema'],
                user=self.credential_file['DATABASE']['username'],
                password=self.credential_file['DATABASE']['password'])
            self.log.debug("Successfully connected to database")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.database = None
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.database = None
            else:
                self.database = None
            pass
            self.log.debug("Could not connect to database")
        # Return configured objects to main program
        return self.database
 