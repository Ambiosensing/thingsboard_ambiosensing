""" Place holder for methods related to the ThingsBoard REST API - auth-controller methods """

import utils
import requests
import user_config
import ambi_logger


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

    # Validate inputs, if any
    if sys_admin:
        utils.validate_input_type(sys_admin, bool)

    if tenant_admin:
        utils.validate_input_type(tenant_admin, bool)

    if customer_user:
        utils.validate_input_type(customer_user, bool)

    # Done with the validations. Now check if the flags are True and, if so, build the calling URLs and the rest of the request body
    url = str(user_config.access_info['host']) + ':' + str(user_config.access_info['port']) + '/api/auth/login'
    headers = {'Content-Type': 'application/json'}




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
