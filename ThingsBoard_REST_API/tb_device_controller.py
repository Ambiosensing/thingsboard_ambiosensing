""" Place holder for methods related to the ThingsBoard REST API - device-controller methods """
import requests
import ambi_logger
import utils
import proj_config
import user_config
import urllib.parse
from mysql_database.python_database_modules import mysql_utils, mysql_auth_controller as mac


def getDeviceTypes():
    """ Simple GET method to retrieve the list of all device types stored in the ThingsBoard platform
    @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
    @:return standard request response """

    # The service endpoint to call
    service_endpoint = "/api/device/types"
    # Get the standard request elements
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    # Execute the service call
    response = requests.get(url=service_dict["url"], headers=service_dict["headers"])

    return response


def getTenantDevices(type=None, textSearch=None, idOffset=None, textOffset=None, limit=10):
    """GET method to retrieve the list of devices with their associations, namely Tenants and Customers. The indexer of the returned list is the DEVICE (or its id to be more precise).
    @:type user_types allowed for this service: CUSTOMER_USER
    @:param type (str) - Use this field to narrow down the type of device to return. The type referred in this field is the custom device type defined by the user upon its creation (e.g., 'Thermometer', 'Water meter' and so on) and this field is
    ultra sensitive. If a device type is defined as 'Thermometer', providing type = 'thermometer' doesn't return any results just because the uppercase difference. So, in order to be used, the caller must know precisely which types of devices were
    defined in the system so far.
    @:param textSearch (str) - Use this field to narrow down results based only in the 'name' field. Like the previous parameter, the string inserted in this field has to be exactly identical to what is in a record's 'name' field to return any
    results. For example, if a device is named 'Water Meter A2', just using 'water Meter A2' instead of the exact string (upper/lower case respected) is enough to get an empty set as response
    @:param idOffset (str) - A similar field as the two before in the sense that its search scope is limited to 'id' fields. But in this particular case, since a device can be potentially associated to several types of other ids (a single device
    can be
    associated to multiple tenants and/or multiple customers, each having its id value explicit in the records), a search using this parameter can result in all devices with a given id, along with their associated tenants and customers if the id
    in the argument belongs to a device, or it can return all devices associated to a particular tenant or customer if the id string provided is of this type. Also, unlike the previous fields, this one allows searches for partial id strings (but
    only if part of the last segment of the id string are omitted. More than that yields no results whatsoever).
    @:param textOffset (str) - Still no clue what this field does... Leave it empty or write your whole life story in it and it always returns the full result set... (If none of the other fields are filled)
    @:param limit (int) - Use this field to limit the number of results returned, regardless of other limiters around (the other fields of the method). If the limit field did truncated the results returned, the result dictionary is returned with
    the 'nextPageLink' key set to another dictionary describing just that and the 'hasNext' key is set to True. Otherwise, if all record were returned, 'nextPageLink' is set to NULL and 'hasNext' comes back set to False.
    @:raise utils.InputValidationException - For errors during the validation of inputs
    @:raise utils.ServiceEndpointException - For errors during the API operation
    @:raise Exception - For any other types of errors
    @:return A HTTP response object containing the following result dictionary (if the API call was successful):
    {
        "data": [
            {
               device_1_data
           },
           {
               device_2_data
           },
           ...
           {
               device_n_data
           }],
    "nextPageLink": null,
    "hasNext": false
    }
    Each element of the 'data' key associated list is the description of a single device in the database using the following format:
    {
      "id": {
        "entityType": str,
        "id": str
      },
      "createdTime": int,
      "additionalInfo": str,
      "tenantId": {
        "entityType": str,
        "id": str
      },
      "customerId": {
        "entityType": str,
        "id": str
      },
      "name": str,
      "type": str,
      "label": str
    }
    The way that ThingsBoard manages these devices internally guarantees that a single device can only be associated to a single tenant and a single customer, which simplifies quite a lot the logic that I need to take to process this data later on
     """
    tenant_device_log = ambi_logger.get_logger(__name__)

    # Validate inputs
    # Start by the mandatory ones (only the limit)
    utils.validate_input_type(limit, int)
    # And then go for the optional ones
    if type:
        utils.validate_input_type(type, str)
    if textSearch:
        utils.validate_input_type(textSearch, str)
    if idOffset:
        utils.validate_input_type(idOffset, str)
    if textOffset:
        utils.validate_input_type(textOffset, str)

    # Check the number passed in limit: zero or negative values are not allowed by the API
    if limit <= 0:
        error_msg = "Invalid limit provided: {0}. Please provide a positive, greater than zero limit value!".format(str(limit))
        tenant_device_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Start with the base endpoint
    service_endpoint = "/api/tenant/devices?"

    url_strings = []

    # Lets start building the API request strings to add to the endpoint
    if type:
        # Escape the string to URL-esque before adding it to the main service endpoint URL string as well as the forward slashes to '%2F' given that the quote method doesn't do that
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

    # Concatenate all the url_strings elements into single string, each individual element separated by '&' as expected by the remote API and appended to the base service endpoint
    service_endpoint += '&'.join(url_strings)

    # Get the standard service dictionary from the utils method

    service_dict = utils.build_service_calling_info(mac.get_auth_token('tenant_admin' if user_config.remote_server else 'customer_user'), service_endpoint)

    # Try to get a response from the remote API
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        tenant_device_log.error(error_msg)
        raise ce

    # If I got a response, check first if it was the expected HTTP 200 OK
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP " + str(eval(response.text)['status']) + " with message: " + str(eval(response.text)['message'])
        tenant_device_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Before sending the result back, check first the status of the 'hasNext' key in the result dictionary and inform the user that, if it is True, there are results still left to return in the remote API server
        if eval(utils.translate_postgres_to_python(response.text))['hasNext']:
            tenant_device_log.warning("Only {0} results returned. There are still more results to return from the remote API side. Increase the 'limit' argument to obtain them.".format(str(limit)))

        return response


def getCustomerDevices(customer_name, type=None, textSearch=None, idOffset=None, textOffset=None, limit=50):
    """Method that executes a GET request to the device-controller.getCustomerDevice service to the remote API in order to obtain a list of devices associated with the customer identified by 'customer_name'. For now, this method then sends that
    information to be used to update the ambiosensing_thingsboard.thingsboard_devices_tables. This method is but a subset of the getTenantDevices method from this own module in the sense that, by specifying a user during the method call,
    the list of devices returned is limited to just the devices assigned to this customer while the getTenantDevices returns the list of all devices, as long as they are assigned to a tenant, regardless of whom that tenant may be.
    @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
    @:param customer_name (str) - The name of the customer as it was defined in its registration in the ThingsBoard interface. This parameter is going to be use to perform SELECT operations in the MySQL database using 'LIKE' clauses so,
    unlike some of the fields in the API service requests, there's some flexibility here for using names that are not exactly identical to what is in the database. The search is going to be applied to the 'name' column of the
    thingsboard_customers_table. Retrieved customer records via this interface are then used to build the service call to the remote API
    @:param type (str) - Use this field to narrow down results based on the type of device to return. The type field is set during the device registration in the ThingsBoard platform and can then be used later to associate various devices to the
    same type (e.g., 'Thermometer', 'luximeter', etc..). The search operation is case-sensitive, i.e., only complete type matches are returned.
    @:param textSearch (str) - Use this field to narrow down the number of returned results based on the 'name' field. Like the previous field, this one is also case-sensitive (only identical matches return results)
    @:param idOffset (str) - Another search field based on the 'id' parameter this time. It does provide just a little bit of flexibility when compared with previous search fields, in the sense that it accepts and processes incomplete id strings,
    as long as some (but not all) of the 12 character segment of its last block are omitted.
    @:param textOffset (str) - Still no clue on what this might be used for...
    @:param limit (int) - Use this field to truncate the number of returned results. If the result set returned from the remote API was truncated for whatever reason, the result dictionary is returned with another dictionary under the
    'nextPageLink' key detailing the results still to be returned and the 'hasNext' key set to True. Otherwise 'nextPageLink' is set to NULL and 'hasNext' to False
    @:raise utils.InputValidationException - For errors during the validation of inputs
    @:raise utils.ServiceEndpoointException - For error during the remote API access
    @:raise Exception - For any other errors
    @:return A HTTP response object containing the following result dictionary:
    {
        "data": [
            {
                customer_device_1_data
            },
            {
                customer_device_2_data
            },
            ...
            {
                customer_device_n_data
            }
        ],
        "nextPageLink": null,
        "hasNext": false
    }

    Each customer_device_data element is a dictionary in the following format:
    customer_device_n_data = {
        "id": {
            "entityType": str,
            "id": str
        },
        "createdTime": int,
        "additionalInfo": null or {
            "description": str
        },
        "tenantId": {
            "entityType": str,
            "id": str
        },
        "customerId": {
            "entityType": str,
            "id": str
        },
        "name": str,
        "type": str,
        "label": str
    }
    """

    customer_device_log = ambi_logger.get_logger(__name__)
    module_table_key = 'customers'
    columns_to_retrieve = ['id']

    # Validate inputs
    try:
        # Start by the mandatory ones first
        utils.validate_input_type(customer_name, str)
        utils.validate_input_type(limit, int)
        if type:
            utils.validate_input_type(type, str)
        if textSearch:
            utils.validate_input_type(textSearch, str)
        if idOffset:
            utils.validate_input_type(idOffset, str)
        if textOffset:
            utils.validate_input_type(textOffset, str)
    except utils.InputValidationException as ive:
        customer_device_log.error(ive.message)
        raise ive

    # Check the number passed in the limit argument for consistency
    if limit <= 0:
        error_msg = "Invalid limit provided: {0}. Please provide a greater than zero limit value!".format(str(limit))
        customer_device_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Before going any further, there a limiting factor here: the customer id. I need to use the customer_name parameter to fetch it through a database consultation. The customer search is going to be an exhaustive one: I'll first try to search
    # for the customer_name that was passed as is. If a single result is returned - the desired outcome - cool, move on. If not, try to add a wildcard character at the end of customer_name (customer_name%), then to just the beginning (
    # %customer_name) and, if I still can't find a single result, try one last time with wildcard on both ends of the string (%customer_name%) in order to get an unique record (multiple records returned are also disregarded). If no clear answer is
    # obtained thus far, raise an Exception with this information
    # Connect to the MySQL database
    cnx = mysql_utils.connect_db(user_config.mysql_db_access['database'])

    # And get a buffered cursor to run SQL statements
    select_cursor = cnx.cursor(buffered=True)

    # Build the SQL SELECT statement to execute in the MySQL database context
    sql_select = """SELECT """ + ", ".join(columns_to_retrieve) + """ FROM """ + str(proj_config.mysql_db_tables[module_table_key]) + """ WHERE name LIKE %s;"""

    # Run the statement and check what comes back
    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (str(customer_name),))

    # If I got a single result from the last SQL execution, I don't need to retrieve the record itself to check it: the cursor retains the number of records found in the statement that was just executed in its rowcount internal variable (which is
    # effectively the same as running a SELECT COUNT(*) instead)

    if select_cursor.rowcount != 1:
        # If the last statement failed, try again with a wildcard character at the end of the customer_name
        customer_device_log.warning("Unable to get an unique result searching for a customer_name = {0} (got {1} results instead). Trying again using customer_name = {2}..."
                                    .format(str(customer_name), str(select_cursor.rowcount), str(customer_name + "%")))
        select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (str(customer_name + "%"),))

        if select_cursor.rowcount != 1:
            customer_device_log.warning("Unable to get an unique result searching for a customer_name = {0} (got {1} result instead). Trying again using customer_name = {2}..."
                                        .format(str(customer_name + "%"), str(select_cursor.rowcount), str("%" + customer_name)))
            select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (str("%" + customer_name),))

            if select_cursor.rowcount != 1:
                customer_device_log.warning("Unable to get an unique result searching for a customer_name = {0} (got {1} result instead). Trying again using customer_name = {2}..."
                                            .format(str("%" + customer_name), str(select_cursor.rowcount), str("%" + customer_name + "%")))
                select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (str("%" + customer_name + "%"),))

                if select_cursor.rowcount != 1:
                    error_msg = "The method was unable to retrieve an unique record for customer_name = {0} (got {1} results instead). Nowhere to go but out now..."\
                        .format(str("%" + customer_name + "%"), str(select_cursor.rowcount))
                    customer_device_log.error(error_msg)
                    exit(-1)

    # If my select_cursor was able to go through the last flurry of validation, retrieve the result obtained
    result = select_cursor.fetchone()

    # The SQL SELECT result returns records as n-element tuples, n the number of columns returned. The SQL statement in this method queries for a single column: 'id', so any result returned should be a single element tuple
    customer_id = str(result[0])

    # I now have everything that I need to place a call to the remote API service. Build the service endpoint
    service_endpoint = "/api/customer/{0}/devices?".format(customer_id)

    url_strings = []
    if type:
        # Don't forget to escape the url strings characters to URL-compatible characters, including the '/' character for '%2F'
        url_strings.append("type=" + urllib.parse.quote(type.encode('UTF-8')).replace('/', '%2F'))
    if textSearch:
        url_strings.append("textSearch=" + urllib.parse.quote(textSearch.encode('UTF-8')).replace('/', '%2F'))
    if idOffset:
        url_strings.append("idOffset=" + urllib.parse.quote(idOffset.encode('UTF-8')).replace('/', '%2F'))
    if textOffset:
        url_strings.append("textOffset=" + urllib.parse.quote(textOffset.encode('UTF-8')).replace('/', '%2F'))
    url_strings.append("limit=" + str(limit))

    # Concatenate all the gathered url_strings together with the rest of the service_endpoint, using '&' as a separator
    service_endpoint += '&'.join(url_strings)

    # Get the request dictionary using a REGULAR type authorization token
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    # Query the remote API
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        customer_device_log.error(error_msg)
        raise ce

    # If I got a response, check first if it was the expected HTTP 200 OK
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP " + str(eval(response.text)['status']) + " with message: " + str(eval(response.text)['message'])
        customer_device_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # I got a valid results, it appears. Check if the number of results returned was truncated by the limit parameter. If so, warn the user only (there's no need to raise Exceptions on this matter)
        # Translate the results to Python-speak first before going for the comparison given that this result set was returned from a MySQL backend
        if eval(utils.translate_postgres_to_python(response.text))['hasNext']:
            customer_device_log.warning("Only {0} results returned. There are still results to return from the remote API side. Increase the 'limit' argument to obtain them.".format(str(limit)))

    # I'm good then. Return the result set back
    return response
