""" Place holder for methods related to the ThingsBoard REST API - tenant-controller methods """

import utils
import ambi_logger
import urllib.parse
import requests
from mysql_database.python_database_modules import mysql_auth_controller as mac


def getTenants(textSearch=None, idOffset=None, textOffset=None, limit=10):
    """GET method to retrieve either all tenants registered in the thingsboard server or a specific tenant by providing the related search terms.
    @:param OPTIONAL textSearch (str) - A text search string to limit the number of tenants to be returned by this operation. This functionality is quite limited I may add. It only searches the title field and only returns any results if
    this element is EXACTLY equal to the title field. Eg. textSearch='Mr Ricardo Almeida' returns that tenant information but textSearch='Ricardo Almeida' return nothing even though this string matches exactly the 'name' field
    @:param OPTIONAL idOffset (str) - A possible search pattern for just the 'id' field. (Strangely enough, using the tenant's id in the textSearch parameter yields no results). A tenant id has a fixed format [8]-[4]-[4]-[4]-[8], that is,
    a 8 character block, a '-' character, then a 4 character block, another '-' character and so on. If the idOffset provided is anything but the first four blocks, including the last '-', the remote API returns a HTTP 400 - Invalid UUID
    string. Yet adding just one character after the last '-' returns a list of all registered tenants... again, I'm still failing to see the use of this field to be honest
    @:param OPTIONAL textOffset (any) - No idea what this field is used for. I've tried searches with matching and un-matching strings, ints, floats, etc... and I always get all the tenants back. Pointless field if I ever saw one...
    @:param limit (int) - The only required field in this methods. Limits the number of results to return
    @:return tenant_data (dict) - The return element is a complex one. If successful, the returned structure is as follows:
    tenant_data = {
        'data': [
            {
                tenant_data_1
            },
            {
                tenant_data_2
            }, ...
            {
                tenant_data_n
            }
        ],
        'nextPageLink': nextPageData,
        'hasNext': bool
    }

    The latter is the overall framework of how the results are returned: a dictionary with 3 keys: 'data', 'nextPageLink' and 'hasNext'.
    The 'data' key contains a list of dictionaries, with as many items as either existing tenants or limit number, whatever is lower. Each item of the data list has the following format:
    tenant_data = {
        'id': {
            'entityType': str,
            'id': str
        },
        'createdTime': int (POSIX timestamp),
        'description': str,
        'country': str,
        'state', str,
        'city': str,
        'address': str,
        'address2': str,
        'zip': str,
        'phone': str,
        'email': str,
        'title': 'str'
        'region': str,
        'name': str
    }
    The 'nextPageLink' is either set to 'None' if all existing tenant data was returned in the 'data' value or, if the limit argument has clipped the number or returned elements, then it has the following dictionary format:
    'nextPageLink': {
        'limit': int,
        'textSearch': str,
        'textSearchBound': str,
        'textOffset': str,
        'idOffset': str
  }
  while the 'hasNext' (a boolean) key is set to either False if the limit argument was high enough or True if there are still results left to return from the remote ThingsBoard API
    """

    # Fetch a local logger for this method only
    tenant_log = ambi_logger.get_logger(__name__)

    # Validate inputs
    try:
        # Validate the mandatory inputs
        utils.validate_input_type(limit, int)
        # As for the optional ones, I need to check if they were passed with non-default values first
        if textSearch:
            utils.validate_input_type(textSearch, str)
        elif idOffset:
            utils.validate_input_type(idOffset, str)
        elif textOffset:
            utils.validate_input_type(textOffset, str)
    except utils.InputValidationException as ive:
        tenant_log.error(ive.message)
        raise ive

    # The limit parameter needs a bit more validation. Passing limit=0 also triggers an error from the remote API. By validating this parameter at this stage, there no need to deal with this potential error later on.
    if limit <= 0:
        error_msg = "Invalid limit provided: {0}. Please provide a positive, greater than zero limit value!".format(str(limit))
        tenant_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    service_endpoint = "/api/tenants?"

    # This service point for this particular method has its arguments built-in using a standard URL format. Because of this, I need to make sure that
    # whatever characters are passed in this method's arguments, they are properly escaped before (URL strings are notoriously picky) being added to
    # URL string

    url_strings = []
    if textSearch:
        # First encode the string into a safe character set (UTF-8) and only then do the escaping of all characters to URL charset. NOTE: By a some reason the following method escapes all problematic characters to URL-esque except one of
        # the worst ones in that regard: '/'. The forward slash, a basic character in URL strings to denote paths, should be escaped to '%2F' if it appears in an argument string but the method bellow ignores this, not sure really why...
        # Anyway, an easily solved problem by forcing a string replace for this character after executing the base function
        url_textSearch = "textSearch=" + urllib.parse.quote(textSearch.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_textSearch)

    if idOffset:
        url_idOffset = "idOffset=" + urllib.parse.quote(idOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_idOffset)

    if textOffset:
        url_textOffset = "textOffset=" + urllib.parse.quote(textOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append(url_textOffset)

    # Add the mandatory parameter to the list as is
    url_strings.append("limit=" + str(limit))
    service_endpoint += '&'.join(url_strings)

    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='sys_admin'), service_endpoint)
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}..".format(str(service_dict['url']))
        tenant_log.error(error_msg)
        raise ce

    # In order to continue, I'm only interested in HTTP 200. Whatever comes back different than that, I'm shutting down this thing
    if response.status_code != 200:
        # Capture the error message that is returned in the message body, as a dictionary encoded in a str (hence the eval to cast it from str back to dict)
        error_msg = "Received an HTTP " + str(eval(response.text)['status']) + " with the message: " + str(eval(response.text)['message'])
        tenant_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg, error_code=int(eval(response.text)['errorCode']))
    else:
        # Replace the troublesome elements from the API side to Python-esque (Pass it just the text part of the response. I have no use for the rest of the object anyway)

        # At this point, I'm going to check the state of the 'hasNext' key in the response and warning the user if its set to True (means that the limit argument was set at value that left some records still on the API side)
        if eval(utils.translate_postgres_to_python(response.text))['hasNext']:
            # In this case, warn the user and carry on
            tenant_log.warning("There are still more results to return from the API side. Increase the 'limit' argument value to obtain them.")

        # I'm done. Send back the response data
        return response




