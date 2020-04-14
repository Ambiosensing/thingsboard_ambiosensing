""" Place holder for methods related to the ThingsBoard REST API - customer-controller methods """

import requests
import ambi_logger
import utils
import urllib.parse
from mysql_database.python_database_modules import mysql_auth_controller as mac


def getCustomers(textSearch=None, idOffset=None, textOffset=None, limit=10):
    """This in one of the simplest GET methods in the customer-controller section of the ThingsBoard API. With it I only need to provide a valid limit number and I can request a list of all registered customers in the platform so far,
    so that I can then populate my own MySQL database table with them.
    All parameters initialized to None in the method signature are OPTIONAL (textSearch, idOffset and textOffset). Those that were set to specific values and data types are MANDATORY (limit)
    @:type user_types allowed for this service: CUSTOMER_USER
    @:param textSearch (str) - Use this field to narrow down results based only in the 'name' field (which in this case should be the same as 'title', though the textSearch field only goes to the former). Yet, in order to yield any results,
    the textSearch field has to be exactly equal to whatever is in the 'name' field in the remote API (put case sensitive in this case...)
    @:param idOffset (str) - A similar field as the one before in the sense that it the sense that its search scope is limited to the 'id' fields. It provides a bit more of flexibility than the last one - id string can be inserted with, at most,
    11 of their last characters omitted and meaningful results are still returned. Any id string smaller than that results in a 'Invalid UUID string' errors.
    @:param textOffset (str) - I'm still at a loss as to what the hell this parameter does... This is the third API service that I process using a python module, with loads of testing using the ThingsBoard Swagger testing application and I still
    waiting for a test that can shed any light on what this... thing... really does. Leave it empty or write your favorite poem in it: its all the same for the remote API really...
    @:param limit (int) - Use this field to limit the number of results returned, regardless of other limiters around. If the limit field did truncates the set of returned results, the result dictionary is returned with its 'nextPageLink' key set
    to another dictionary describing just that and the 'hasNext' key is set to True. Otherwise, if all records were returned, 'nextPageLink' is set to NULL and 'hasNext' is returned set to False.
    @:raise utils.InputValidationException - For errors during the validation of inputs
    @:raise utils.ServiceEndpointException - For errors occurring during the interface with the remote API
    @:raise Exception - For any other types of errors
    @:return an HTTP response object containing the following result dictionary:
    {
        "data": [
            {
                customer_data_1
            },
            {
                customer_data_2
            },
            ...
            {
                customer_data_n
            }
        ],
        "nextPageLink": null or dict,
        "hasNext": bool
    }
    Each "customer_data" sub dictionary has the following format:
    customer_data = {
        "id": {
            "entityType": str,
            "id": str
        },
        "createTime": int,
        "additionalInfo": null or {
            "description": str
        },
        "country": str,
        "state": str,
        "city": str,
        "address": str,
        "address2": str,
        "zip": str,
        "phone": str,
        "email": str,
        "title": str,
        "tenantId": {
            "entityType": str,
            "id": str
        },
        "name": str
    }
    """
    customer_log = ambi_logger.get_logger(__name__)

    # Validate inputs
    try:
        utils.validate_input_type(limit, int)
        if textSearch:
            utils.validate_input_type(textSearch, str)
        if idOffset:
            utils.validate_input_type(idOffset, str)
        if textOffset:
            utils.validate_input_type(textOffset, str)
    except utils.InputValidationException as ive:
        customer_log.error(ive.message)
        raise ive

    if limit <= 0:
        error_msg = "Invalid limit provided: {0}. Please provide a value greater than zero for the limit value!".format(str(limit))
        customer_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    service_endpoint = "/api/customers?"

    url_strings = []

    if textSearch:
        textSearch = urllib.parse.quote(textSearch.encode('UTF-8')).replace('/', '%2F')
        url_strings.append("textSearch=" + str(textSearch))
    if idOffset:
        idOffset = urllib.parse.quote(idOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append("idOffset=" + str(idOffset))
    if textOffset:
        textOffset = urllib.parse.quote(textOffset.encode('UTF-8')).replace('/', '%2F')
        url_strings.append("textOffset=" + str(textOffset))
    url_strings.append("limit=" + str(limit))

    # Create the endpoint request string
    service_endpoint += '&'.join(url_strings)

    # Place the HTTP GET request using a REGULAR type authorization token
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    # Query the remote API
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a request from {0}...".format(str(service_dict['url']))
        customer_log.error(error_msg)
        raise ce

    # Check the status code of the HTTP response before moving forward
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP {0} with message {1}.".format(str(eval(response.text)['status']), str(eval(response.text)['message']))
        customer_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Check the status of the 'hasNext' parameter returned
        if eval(utils.translate_postgres_to_python(response.text))['hasNext']:
            customer_log.warning("Only {0} results returned. There are still more results to return from the remote API side. Increase the 'limit' argument to obtain them.".format(str(limit)))

        return response
