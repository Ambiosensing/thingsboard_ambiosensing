""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group asset-controller """

import requests
import ambi_logger
import utils
import urllib.parse


def getAssetTypes():
    """This method employs the same logic as all the ThingsBoard interface methods so far: it creates the necessary endpoint, gather any arguments necessary for the service call, places a GET request to the remote API and returns the response,
    in a dictionary data structure, as usual
    @:raise utils.ServiceEndpointException - If errors occur when accessing the remote API
    @:return result (dict) - A dictionary in the following format (dictated by the remote API):
        result = [
                    {
                        "tenantId": {
                            "entityType": <str>,
                            "id": <str>
                        },
                        "entityType": <str>,
                        "type": <str>
                    }
                ]
    This dictionary contains a list of the information associated to each asset as a whole (this dictionary doesn't reveal how many assets exist in the database, just the types that were defined so far)
    """
    # The usual log
    asset_types_log = ambi_logger.get_logger(__name__)

    # Base endpoint string
    service_endpoint = "/api/asset/types"

    # Build the full service dictionary for the executing the remote call
    service_dict = utils.build_service_calling_info(utils.get_auth_token(admin=False), service_endpoint)

    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a request from {0}...".format(str(service_dict['url']))
        asset_types_log.error(error_msg)
        raise ce

    # Check the status code of the HTTP response before moving forward
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP {0} with message {1}.".format(str(eval(response.text)['status']), str(eval(response.text)['message']))
        asset_types_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Return the response
        return response


def getTenantAssets(type=None, textSearch=None, idOffset=None, textOffset=None, limit=10):
    pass