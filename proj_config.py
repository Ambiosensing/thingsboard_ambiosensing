""" This is going to be the main repository for configurable elements, such as paths, constants, database access credentials and so on. This file is for only project specific configurations (such as database table names,
lists of expected arguments, etc.. For user-specific configuration, please use the user_config.py file"""

import os
import logging

# Set the basic connectivity parameters for the thingsboard installation
# This project base_path, which is always useful
base_path = os.getcwd()

# Authorization token backup file location - path defined relatively to the working path; should work with any installation as long as the
# main folder structure is maintained
auth_token_path = os.path.join(os.getcwd(), "ThingsBoard_REST_API\\auth_token")

# Basic (empty) authentication dictionary expected by the authentication and refresh tokens methods. Recall this whenever a serious error is detected
# (mal formed or missing auth_token file for example)
auth_data = {
    'admin':
        {
            'token': None,
            'refreshToken': None
        },
    'regular':
        {
            'token': None,
            'refreshToken': None
        }
}

# Next follows a list of supported entityTypes by the ThingsBoard platform (as mentioned in https://thingsboard.io/docs/user-guide/telemetry/, just bellow the curl example code to access the Timeseries data keys API. Most services require
# than one of these types be specified in the service
# endpoint
thingsboard_supported_entityTypes = [
    "TENANT",
    "CUSTOMER",
    "USER",
    "DASHBOARD",
    "ASSET",
    "DEVICE",
    "ALARM",
    "ENTITY_VIEW"
]

# This dictionary maps the complete table names in the ambiosensing database to a more simple term or name. This abstraction allows us to change the table names at will in the future, but as long as we maintain the same key in the next
# dictionary and all the table names in further methods are obtained referencing the key instead of the table name, the operation should be trivial
mysql_db_tables = {
    'tenants': 'thingsboard_tenants_table',
    'devices': 'thingsboard_devices_table',
    'customers': 'thingsboard_customers_table',
    'authentication': 'thingsboard_authentication_table'
}
# --------------------------------------------- TYPE VALIDATION ----------------------------------------------------------------------------------
# Allowed entityTypes in the ThingsBoard platform
valid_entity_types = ['TENANT', 'CUSTOMER', 'USER', 'DASHBOARD', 'ASSET', 'DEVICE', 'ALARM', 'RULE_CHAIN', 'RULE_NODE', 'ENTITY_VIEW', 'WIDGETS_BUNDLE', 'WIDGETS_TYPE']

# Allowed relation types
valid_relation_type = ['COMMON', 'ALARM', 'DASHBOARD', 'RULE_CHAIN', 'RULE_NODE']

# Allowed direction (for relation queries)
valid_direction = ['FROM', 'TO']

# --------------------------------------------- LOGGER CONFIGURATION ----------------------------------------------------------------------------------
# The next string establishes a base format for the lines output by the logger objects. The syntax used was defined by the logging module itself (its in its
# manual) but it is quite straight forward. The datefmt variable establishes a rule to print datetime elements and the '-10' extra element associated with
# the levelname argument a fixed 10-character space for this item (only if the levelname has a status name with more than 10 characters, this space matches
# that length, otherwise it forces this 10-character space regardless of what is in it.
LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-10s [%(filename)s:%(name)s:%(lineno)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Where the log files are going to be located
LOG_FILENAME = "ambi_main.log"
LOG_FILE_LOCATION = os.path.join(base_path, 'ambiosensing_logs', LOG_FILENAME)


