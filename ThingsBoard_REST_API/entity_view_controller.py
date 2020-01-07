""" Place holder for methods related to the ThingsBoard REST API - entity-view-controller methods """

import utils
import requests


def getEntityViewTypes(auth_token):
    """ GET method to retrieve the types associated to the entityView structure
     @:param auth_token - a valid authorization token
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
    service_dict = utils.build_service_calling_info(auth_token, service_endpoint)

    response = requests.get(url=service_dict["url"], headers=service_dict["headers"])

    # Replace the troublesome elements from the API side to Python-esque (Pass it just the text part of the response. I have no use for the rest of the object anyway)
    return response
