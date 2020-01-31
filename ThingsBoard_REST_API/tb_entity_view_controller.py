""" Place holder for methods related to the ThingsBoard REST API - entity-view-controller methods """

import utils
import requests
from mysql_database.python_database_modules import mysql_auth_controller as mac


def getEntityViewTypes():
    """ GET method to retrieve the types associated to the entityView structure
     @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
     @:return
                {
                    "entityType": string,
                    "tenantId":
                    {
                        "id": string
                    },
                    "type": string
                }
     """
    service_endpoint = "/api/entityView/types"
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    response = requests.get(url=service_dict["url"], headers=service_dict["headers"])

    # Replace the troublesome elements from the API side to Python-esque (Pass it just the text part of the response. I have no use for the rest of the object anyway)
    return response
