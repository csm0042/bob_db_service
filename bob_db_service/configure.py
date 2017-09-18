#!/usr/bin/python3
""" configure.py:
    Configuration process for the RPiHome application.
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import configparser
import logging
import logging.handlers
import os
import sys
import mysql.connector
import mysql.connector.errorcode as errorcodes


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


    def get_logger(self):
        # Set up application logging
        self.config_file.read(self.filename)
        self.log_path = self.config_file['LOG FILES']['log_file_path']
        self.logger = logging.getLogger('master')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []
        os.makedirs(self.log_path, exist_ok=True)
        # Console handler
        self.handlers = []
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(logging.INFO)
        self.cf = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.cf)
        self.logger.addHandler(self.ch)
        self.logger.info('Console logger handler created and applied')
        # File handler
        self.fh = logging.handlers.TimedRotatingFileHandler(
            os.path.join(self.log_path, "Debug.log"),
            when='d',
            interval=1,
            backupCount=4
        )
        self.fh.setLevel(logging.DEBUG)
        self.ff = logging.Formatter(
            '%(asctime)-25s %(levelname)-10s '
            '%(funcName)-22s %(message)s'
        )
        self.fh.setFormatter(self.ff)
        self.logger.addHandler(self.fh)
        self.logger.info('File logger handler created and applied')
        # Return configured objects to main program
        return self.logger


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
            self.logger.debug('Credentails file found')
        except:
            self.logger.error('No credentials file found')
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
            self.logger.debug("Successfully connected to database")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.database = None
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.database = None
            else:
                self.database = None
            pass
            self.logger.debug("Could not connect to database")
        # Return configured objects to main program
        return self.database
 