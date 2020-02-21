""" Place holder for methods related to the ThingsBoard REST API - rpc-controller methods """

import requests
import ambi_logger
import utils
import json
import proj_config
import user_config
from mysql_database.python_database_modules import mysql_utils, mysql_auth_controller as mac


def handleOneWayDeviceRPCRequests(deviceId, remote_method, param_dict=None):
    """POST method to place an one way RPC call to a device identified by the 'deviceId' parameter provided as argument. The RPC command needs to have a valid target in the device (client) side to have any effect. This command should be specified
    in the 'remote_method argument' and any expected arguments required for its execution should be provided in the 'param_dict' argument
    This method is equivalent to a 'fire-and-forget' routine: no replies are expected nor are going to be returned either from the client side (this service doesn't wait for a response msg in the respective topic. This means that this method
    should be use for ACTUATE only. To get any information from the device side use the two way version of this method since all device-side communications are to be initiated from "this" side (the ThingsBoard/application side) and thus a response
    is expected following a request
    @:param deviceId (str) - The typical 32-byte, dash separated hexadecimal string that uniquely identifies the device in the intended ThingsBoard installation
    @:param remote_method (str) - The name of the method that is defined client-side that is to be executed with this call
    @:param param_dict (dict) - If the remote method requires arguments to be executed, use this dictionary argument to provide them
    @:return http_status_code (int) - This method only returns the HTTP status code regarding the execution of the HTTP request and nothing more

    Usage example: Suppose that there's a device configured in the Thingsboard installation that abstracts a lighting switch that can be turned ON or OFF. The device (Raspberry Pi) that controls that switch has a continuously running method (via a
    while True for instance) that listens and reacts to messages received from the ThingsBoard server instance. One of these control methods is called "setLightSwitch" and expects a boolean action "value" passed in the message strucure (True or
    False) regarding what to do with the light switch (False = OFF, True = ON). The switch is currently OFF. To turn it ON using this method, use the following calling structure:

    handleOneWayDeviceRPCRequests(deviceId="3806ac00-5411-11ea-aa0c-135d877fb643", remote_method="setLightSwitch", param_dict={"value": True})

    The message that is going to be forward to the device as a RPC request is the following JSON structure:
    {
        "method": "setLightSwitch",
        "params":
        {
            "value": true
        }
    }

    The "method" - "params" JSON is somewhat of a format for RPC interactions, with "params" being a complex (multi-level) dictionary to allow for complex, multi-argument remote method executions
    """

    one_way_log = ambi_logger.get_logger(__name__)

    # Validate inputs
    utils.validate_input_type(deviceId, str)
    utils.validate_id(entity_id=deviceId)

    utils.validate_input_type(remote_method, str)

    if param_dict:
        utils.validate_input_type(param_dict, dict)

    # The rest is pretty much more of the same. This one gets the deviceId built in the calling URL
    service_endpoint = '/api/plugins/rpc/oneway/' + deviceId

    # Crete the data payload in the dictionary format
    data = {
        "method": str(remote_method),
        "params": param_dict
    }

    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type="tenant_admin"), service_endpoint=service_endpoint)

    # Done. Set things in motion then

    response = requests.post(url=service_dict["url"], headers=service_dict["headers"], data=json.dumps(data))

    return response.status_code