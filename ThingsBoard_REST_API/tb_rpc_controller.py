""" Place holder for methods related to the ThingsBoard REST API - rpc-controller methods """

import requests
import ambi_logger
import utils
import proj_config
import user_config
from mysql_database.python_database_modules import mysql_utils


def handleOneWayDeviceRPCRequests(deviceId):
    """POST method to place an one way RPC call to a device identified by the 'deviceId' parameter provided as argument"""
