""" Place holder for methods related to the ThingsBoard REST API - assets-controller methods """

import requests
import ambi_logger
import utils
import urllib.parse
import user_config
from mysql_database.python_database_modules import mysql_auth_controller as mac


def getAssetTypes():
    """This method employs the same logic as all the ThingsBoard interface methods so far: it creates the necessary endpoint, gather any arguments necessary for the service call, places a GET request to the remote API and returns the response,
    in a dictionary data structure, as usual
    @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
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
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

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
    """This is the standard method to retrieve all ASSETs currently in the ThingsBoard installation database (regardless which database is implemented). As with all services of this type so far, this is the ThingsBoard side of the whole process,
    the one that places a request in the expected format to the ThingsBoard API.
    @:param type (str): OPTIONAL Use this argument to filter the results for a specific asset type (eg. 'building', 'room', 'floor', etc...) This is a free text field from the ThingsBoard side, which means any string can be set in this field. If you
    know a
    priori which exact ASSET type you're interested in, use this argument to narrow down the results to be returned
    @:param textSearch (str): OPTIONAL Use this argument to provide a str to be used to narrow down the returned results based on 'name' field from the ASSET description. As with similar methods, this field is quite limited: unless an exact match
    is found between the provided textSearch argument and the contents of the 'name' field, no filtering actually takes place.
    @:param idOffset (str): OPTIONAL Analogous field to the previous one but this one applies to the 'id' field. The filtering abilities of this argument are also quite limited. Check similar methods that use this argument too for more detailed
    descriptions.
    @:param textOffset (str): OPTIONAL So far, still no idea of what this does. Other than determining that it only accepts strings, I still have no clue to what is the actual purpose of this element.
    @:param limit (int): Use this field to limit the number of results returned from this service. If the argument in this field prevents the full scope of results to be returned, a specific set of structures, namely a 'nextPageLink' and
    'hasNext' are also returned. In this event, the method warn the caller that are results left to return but in the end is up to the caller to specify an higher limit value to return them.
    @:return result (list of dict): If the API call was successful, this method returns an HTTP response object back with the following dictionary in its 'text' field:
    "data": [
    # ASSET 1 data
    {
        "id": {
        "entityType": string,
        "id": string
      },
      "createdTime": int,
      "additionalInfo": {
        "description": "A dummy building that I'm planning to fill with dead rats and cockroaches once I'm done with it"
      },
      "tenantId": {
        "entityType": string,
        "id": string
      },
      "customerId": {
        "entityType": string,
        "id": string
      },
      "name": string,
      "type": string
    },
    # ASSET 2 Data
    {
        "id": {
        "entityType": string,
        "id": string
      },
      "createdTime": int,
      "additionalInfo": {
        "description": string
      },
      "tenantId": {
        "entityType": string,
        "id": string
      },
      "customerId": {
        "entityType": string,
        "id": string
      },
      "name": string,
      "type": string
    },
    .
    .
    .
    # ASSET N Data
    {
        "id": {
        "entityType": string,
        "id": string
      },
      "createdTime": int,
      "additionalInfo": {
        "description": string
      },
      "tenantId": {
        "entityType": string,
        "id": string
      },
      "customerId": {
        "entityType": string,
        "id": string
      },
      "name": string,
      "type": string
    }
    ]
    """
    asset_control_log = ambi_logger.get_logger(__name__)

    # Validate mandatory inputs first
    utils.validate_input_type(limit, int)

    # And now for the OPTIONAL ones
    if type:
        utils.validate_input_type(type, str)
    if textSearch:
        utils.validate_input_type(textSearch, str)
    if idOffset:
        utils.validate_input_type(idOffset, str)
    if textOffset:
        utils.validate_input_type(textOffset, str)

    # Validate the limit a bit further
    if limit <= 0:
        error_msg = "Invalid limit provided: {0}. Please provide a positive, greater than zero limit value!".format(str(limit))
        asset_control_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Setup the base endpoint
    service_endpoint = "/api/tenant/assets?"

    url_strings = []

    # Check the provided inputs and add the necessary elements to the endpoint to call the service
    if type:
        url_type = "type=" + urllib.parse.quote(type.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_type)

    if textSearch:
        url_textSearch = "textSearch=" + urllib.parse.quote(textSearch.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_textSearch)

    if idOffset:
        url_idOffset = "idOffset=" + urllib.parse.quote(idOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_idOffset)

    if textOffset:
        url_textOffset = "textOffset=" + urllib.parse.quote(textOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_textOffset)

    url_strings.append("limit=" + str(limit))

    # Concatenate the elements in the url_strings list into a single url string
    service_endpoint += '&'.join(url_strings)

    # Get the standard dictionary to call the remote service. It appears that different installations require different sets of user credentials... still trying to figure out what the hell is going on with this one
    service_dict = utils.build_service_calling_info(mac.get_auth_token('tenant_admin'), service_endpoint=service_endpoint)

    # And try to get a response from the remote API
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        asset_control_log.error(error_msg)
        raise ce

    # Check the HTTP response code first
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP " + str(eval(response.text)['status']) + " with message: " + str(eval(response.text)['message'])
        asset_control_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Check if the 'hasNext' flag is set, i.e., if there are still results to return from the ThingsBoard side of things. In any case, the result structure has that flag set to either 'true' or 'false', which are not recognized as proper
        # boolean values by Python (those are boolean natives from Postgres/Cassandra). As such, I need to 'translate' the returned text to Python-esque first using the method built for that purpose
        if eval(utils.translate_postgres_to_python(response.text))['hasNext']:
            asset_control_log.warning("Only {0} results returned. There are still more results to return from the remote API side. Increase the 'limit' argument to obtain them.".format(str(limit)))

        # But return the response nonetheless
        return response
