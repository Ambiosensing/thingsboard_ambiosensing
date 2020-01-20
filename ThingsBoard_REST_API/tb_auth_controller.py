""" Place holder for methods related to the ThingsBoard REST API - auth-controller methods """

import utils
import requests
import user_config
import ambi_logger
import proj_config
from mysql_database.python_database_modules import mysql_utils


def get_session_tokens(sys_admin=True, tenant_admin=True, customer_user=True):
    """This method is the entry point for all the remote accesses that are about to happen withing this project. All service calls require an authorization token to be passed within the Request URL in order to get a proper response back. The issue
    here is that the ThingsBoard platform supports 3 types of users (SYS_ADMIN, TENANT_ADMIN and CUSTOMER_USER) and they have distinct sets of permissions. For example, a remote service that requires a TENANT_ADMIN authorization token doesn't
    accept a SYS_ADMIN token, though technically a SYS_ADMIN user is above a TENANT_ADMIN user in its internal hierarchy. This has an enormous bug breeding problem, as I've experienced so far. Thus I'm going with the 'shotgun' approach on this
    one: I have a valid pair of credentials for each user type in the user_config.access_info dictionary and this method can, at once, get a valid token for each of these users. On a later stage I can then develop extremely resilient methods that
    simply test each available authorization tokens (stored in the local MySQL database) to eventually get a valid response from the remote API. Its not elegant but it is efficient nonetheless.
    By default, i.e., without no arguments provided, the method fetches a token for each one of the user types. If you want to skip any of the users, set the corresponding argument flag to False. The response features both the authorization token
    ('token') and the respective token used to refresh an expired authorization token without needing to provide the authentication credentials again ('refreshToken')
    @:param sys_admin (bool) - Triggers the retrieval of a SYS_ADMIN type authentication token
    @:param tenant_admin (bool) - Triggers the retrieval of a TENANT_ADMIN type authentication token
    @:param customer_user (bool) - Triggers the retrieval of a CUSTOMER_USER type authentication token
    @:raises utils.InputValidationException - If arguments from invalid data types are provided
    @:raises utils.ServiceEndpointException - For problems with the remote API's access and non-HTTP 200 responses
    @:return auth_dict (dict) - A dictionary in the format:
    auth_dict = {
        'sys_admin': {
            'token': str,
            'refreshToken': str
        },
        'tenant_admin': {
            'token': str,
            'refreshToken': str
        },
        'customer_user': {
            'token': str,
            'refreshToken': str
        }
    }
    If any of these users are omitted by un-setting the respective flag in the argument list, the respective sub-dictionary under this entry is going to be set to 'None'.
    """
    session_tokens_log = ambi_logger.get_logger(__name__)

    # Build the common elements
    url = str(user_config.access_info['host']) + ':' + str(user_config.access_info['port']) + '/api/auth/login'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    # And the template for the return dictionary
    auth_dict = {
        'sys_admin': None,
        'tenant_admin': None,
        'customer_user': None
    }

    # Now go for each of the user types in the above dictionary
    for user_type in list(auth_dict.keys()):
        if not sys_admin and user_type == 'sys_admin':
            # Ignore the current run if the flag is not set
            continue
        elif not tenant_admin and user_type == 'tenant_admin':
            continue
        elif not customer_user and user_type == 'customer_user':
            continue
        else:
            # Otherwise (if the corresponding flag is True and the loop is running the same key)
            data = '{"username": "' + str(user_config.access_info[user_type]['username']) + '", "password": "' + str(user_config.access_info[user_type]['password']) + '"}'

            try:
                response = requests.post(url=url, headers=headers, data=data)
            except (requests.ConnectionError, requests.ConnectTimeout):
                error_msg = "Unable to establish connection with {0}. Exiting...".format(str(user_config.access_info['host'] + ": " + str(user_config.access_info['port'])))
                session_tokens_log.error(error_msg)
                raise utils.ServiceEndpointException(message=error_msg)

            # If the response code is anything other than HTTP-200, chances are that you have authentication issues
            if response.status_code != 200:
                session_tokens_log.error(response.text)
                # Raise the proper Exception with the original message and cost
                raise utils.AuthenticationException(message=response.text, error_code=response.status_code)

            # Otherwise, fill out the corresponding auth_dict entry
            else:
                auth_dict[user_type] = eval(response.text)

    # Done. Return the authentication structures
    return auth_dict


def refresh_session_token(sys_admin=False, tenant_admin=False, customer_user=False):
    """This method is analogous to the get_session_token one but using the refreshToken, that is assumed to be in the respective database already, to get a valid authorization token without needing to provide the access credentials again,
    thus a more secure way to keep sessions active. This requires at least one of the input argument flags to be set to function. All three currently supported user_types can be refreshed by one call to this method, as long as the flags are set.
    The idea here being that, when requested, the remote API returns a pair of authentication token/refresh token in which the authentication token as a shorter validity period than the refresh token. But once the authentication token get expired,
    if a call to this method is placed before the refresh token also expires (which also happened, though later than the first one) allows to reset the whole thing, since using the refresh token routine results in a new, fresh pair with both
    expiration periods reset
    @:param sys_admin (bool) - Flag to set a refresh on the tokens for the SYS_ADMIN
    @:param tenant_admin (bool) - Flag to set a refresh on the tokens for the TENANT_ADMIN
    @:param customer_user (bool) - Flag to set a refresh on the tokens for the CUSTOMER_USER
    @:raise utils.AuthenticationException - If the access credentials cannot be used to retrieve authentication data
    @:raise utils.ServiceCallException - If errors happen when accessing the remote service
    @:raise utils.InputValidationException - If an invalid argument is provided (data type wise)
    @:raise mysql_utils.MySQLDatabaseException - If errors happen with the database access or with the integrity of the data in the database
    @:return auth_dict (dict) - An authentication dictionary in the same format used so far:
        auth_dict = {
            'sys_admin': {
                'token': str,
                'refreshToken': str
            },
            'tenant_admin': {
                'token': str,
                'refreshToken': str
            },
            'customer_user': {
                'token': str,
                'refreshToken': str
            }
        }
    As before, omitted user types have their sub dictionary set to None. This method only returns this structure back. Its up to the calling method to update the database table, to keep things decoupled as much as possible at this point
    """
    refresh_token_log = ambi_logger.get_logger(__name__)

    # Check first if at least one of the argument flags was set, after validation that is
    if sys_admin:
        utils.validate_input_type(sys_admin, bool)

    if tenant_admin:
        utils.validate_input_type(tenant_admin, bool)

    if customer_user:
        utils.validate_input_type(customer_user, bool)

    # If all argument flags are False
    if not (sys_admin or tenant_admin or customer_user):
        error_msg = "No user types set. Please set one of the argument flags when calling this method..."
        refresh_token_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Retrieve the existing tokens from the database into the typical authentication dictionary
    auth_dict = {
        'sys_admin': None,
        'tenant_admin': None,
        'customer_user': None
    }

    # Add all the requested user type to a list
    user_type_list = []

    # Add the relevant user type strings to a list for iterating
    if sys_admin:
        user_type_list.append('sys_admin')

    if tenant_admin:
        user_type_list.append('tenant_admin')

    if customer_user:
        user_type_list.append('customer_user')

    # And grab the results from the database
    database_name = user_config.mysql_db_access['database']
    table_name = proj_config.mysql_db_tables['authentication']

    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)
    select_column = 'user_type'

    sql_select = """SELECT * FROM """ + str(table_name) + """ WHERE """

    data_tuple = tuple(user_type_list)
    where_list = []

    for i in range(0, len(user_type_list)):
        where_list.append(select_column + " = %s")

    sql_select += """ OR """.join(where_list) + """;"""

    # Execute the statement then
    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, data_tuple)

    # Check if any results were returned
    if not select_cursor.rowcount:
        error_msg = "The statement '{0}' didn't return any results from {1}.{2}.".format(str(select_cursor.statement), str(database_name), str(table_name))
        refresh_token_log.error(error_msg)
        select_cursor.close()
        cnx.close()
        raise mysql_utils.MySQLDatabaseException(message=error_msg)
    # Move on if you got any results back
    else:
        # Get the list of column names from the authentication table to use as a reference to obtain the data I'm looking for
        column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)

        # Create the base endpoint (for getting a new pair of authorization tokens from an expired authorization one and a still valid refresh token, provide both tokens (with the refreshToken sent as data payload) to the '/token' endpoint
        service_endpoint = '/api/auth/token'

        # Now I can pick up a record at a time, refresh the authentication token and update the return dictionary with the reply
        result = select_cursor.fetchone()

        # Do the following as long as there is a non-None element returned from the database cursor
        while result:
            # Start by getting the standard service call structures
            con_dict = utils.build_service_calling_info(auth_token=result[column_list.index('token')], service_endpoint=service_endpoint)

            # Build the additional data payload structure which is needed for this service call in particular
            data = {'refreshToken: ' + str(result[column_list.index('refreshToken')])}

            # And call the remote API with the refresh request
            try:
                api_response = requests.post(url=con_dict['url'], headers=con_dict['headers'], data=data)
            except (requests.ConnectionError, requests.ConnectTimeout):
                error_msg = "Unable to establish a connection with {0}:{1}. Exiting...".format(str(user_config.thingsboard_host), str(user_config.thingsboard_port))
                refresh_token_log.error(error_msg)
                select_cursor.close()
                cnx.close()
                raise utils.ServiceEndpointException(message=error_msg)

            # If a non-HTTP 200 status code was returned, its probably a credential issue. Raise an exception with the proper information in it
            if api_response.status_code != 200:
                refresh_token_log.error(api_response.text)
                select_cursor.close()
                cnx.close()
                raise utils.AuthenticationException(message=api_response.text, error_code=api_response.status_code)

            # Got a pair of valid tokens back. Update the structures then
            else:
                auth_dict[column_list.index('user_type')] = eval(api_response.text)

            # And grab the next result for another iteration of this
            result = select_cursor.fetchone()

        # The while loop is done here and I've processed all results thus far. All its left to do is return the updated authorization dictionary
        return auth_dict


def getUser(auth_token):
    """This method uses the authorization token transmitted via the service endpoint string to return which type of user the provided token is associated with: SYS_ADMIN, TENANT_ADMIN or CUSTOMER USER. If successful, the API returns a dictionary
    with the user information that is currently stored in the server side database
    @:param auth_token (str) - A string of apparently random characters that was issues preemptively by the remote server after providing it with a pair of username-password access credentials
    @:raise utils.ServiceEndpointException - If the remote call failed. The exception message provides details on the failure reason
    @:return result_dict (dict) - If successful, the remote API returns the following structure:
    result_dict = {
          "id": {
            "entityType": str (one from proj_config.thingsboard_supported_entityTypes),
            "id": str (and 32 byte hexadecimal string with the characters/bytes grouped as 8-4-4-4-12)
          },
          "createdTime": int (a POSIX-type timestamp),
          "additionalInfo": {
            "description": str
          },
          "tenantId": {
            "entityType": str (one from proj_config.thingsboard_supported_entityTypes),
            "id": str (and 32 byte hexadecimal string with the characters/bytes grouped as 8-4-4-4-12)
          },
          "customerId": {
            "entityType": str (one from proj_config.thingsboard_supported_entityTypes),
            "id": str (and 32 byte hexadecimal string with the characters/bytes grouped as 8-4-4-4-12)
          },
          "email": str,
          "authority": str (a user type from the set (SYS_ADMIN, TENANT_ADMIN, CUSTOMER_USER),
          "firstName": str,
          "lastName": str,
          "name": str
}
    """
    # Validate the token real quickly
    utils.validate_input_type(auth_token, str)

    # Set the service endpoint
    service_endpoint = '/api/auth/user'

    # Grab the automatic elements needed to call the service (headers, url and such)
    service_dict = utils.build_service_calling_info(auth_token=auth_token, service_endpoint=service_endpoint)

    # And execute the damn thing
    response = requests.get(url=service_dict['url'], headers=service_dict['headers'])

    return response
