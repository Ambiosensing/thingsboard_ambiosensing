""" Place holder for methods related to the ThingsBoard REST API - entity-relation-controller """

import requests
import ambi_logger
import utils
import proj_config
from mysql_database.python_database_modules import mysql_auth_controller as mac


def findByQuery(entityType, entityId, direction, relationTypeGroup):
    """This method implements the much needed interface with the mysterious 'Relations' table in the ThingsBoard side database. This table is literally the only place where once can associate an ASSET to the DEVICEs that are related to it - the
    ASSET as a relation (Contains, Uses, Manages, etc..) to a set of DEVICEs. It turns out that this relation is one of the most important for the Ambiosensing project: its the quickest and direct way to find out which DEVICEs are
    installed/monitoring a given space, floor, room, etc..., which is identified before the ThingsBoard platform as ASSETs. Yet, there isn't a relation-controller or any sort, this API set being the closest of that that we've found so far
    @:param entityType (str) - An uppercase string identifying the type of entity to search for, i.e., this entityType is going to be used as a search parameter. The provided parameter is going to be validated against the supported ones in
    proj_config.valid_entity_types
    @:param entityId (str) - An id in the expected xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx format, in which each 'x' is an hexadecimal character (0-f), that identifies the element from the entityType provided
    @:param direction (str) - An uppercase string identified the direction of the relation that spawns from the element identifies by the (entityType, entityId) pair. If the element contains the expected results, the direction should be 'FROM',
    if the element identified is contained in a parent element (a device inside an asset for example), than the direction should be 'TO'. Arguments provided in this parameter are validated against the proj_config.valid_direction element list of
    allowed directions
    @:param relationTypeGroup (str) - An uppercase identifying the high level set of which the results belong to. Parameters provided in this argument are going to be validated against the proj_config.valid_relation_type list of allowed terms for
    this field.
    @:raise utils.InputValidationException - If the input arguments fail initial validation
    @:raise utils.ServiceEndpointException - If the call to the remote API was not successful
    @:raise utils.AuthenticationException - For errors related with the authentication token exchange with the remote API calls
    @:return result (list of dicts) - A list of dictionaries with the following structure (use eval(result.text) to retrieve the element in the dictionary format from the str format in which it is returned):
    [
      {
        "from": {
          "entityType": "string",
          "id": "string"
        },
        "to": {
          "entityType": "string",
          "id": "string"
        },
        "type": "string",
        "typeGroup": "string",
        "additionalInfo": null
      },
      {
        "from": {
          "entityType": "string",
          "id": "string"
        },
        "to": {
          "entityType": "string",
          "id": "string"
        },
        "type": "string",
        "typeGroup": "string",
        "additionalInfo": null
      },
      .
      .
      .
      {
        "from": {
          "entityType": "string",
          "id": "string"
        },
        "to": {
          "entityType": "string",
          "id": "string"
        },
        "type": "string",
        "typeGroup": "string",
        "additionalInfo": null
      }
    ]
"""
    # Get the usual log
    entity_relation_log = ambi_logger.get_logger(__name__)

    # Validate inputs
    utils.validate_input_type(entityType, str)
    utils.validate_input_type(entityId, str)
    utils.validate_input_type(direction, str)
    utils.validate_input_type(relationTypeGroup, str)

    # Cool, seems like everything has the right data type. Carry on with the validations then
    # Put all arguments except the id to uppercase first
    entityType = entityType.upper()
    direction = direction.upper()
    relationTypeGroup = relationTypeGroup.upper()

    # Validate the id format
    utils.validate_id(entity_id=entityId)

    # And now the rest of the parameters
    if entityType not in proj_config.valid_entity_types:
        raise utils.InputValidationException("Invalid entity type provided: {0}. Please provide one of the following entity types to continue: {1}".format(str(entityType), str(proj_config.valid_entity_types)))
    elif direction not in proj_config.valid_direction:
        raise utils.InputValidationException("Invalid direction provided: {0}. Please provide one of the following valid directions to continue: {1}".format(str(direction), str(proj_config.valid_direction)))
    elif relationTypeGroup not in proj_config.valid_relation_type:
        raise utils.InputValidationException("Invalid relation type provided: {0}. Please provide one of the following relation types to continue: {1}".format(str(relationTypeGroup), str(proj_config.valid_relation_type)))

    # Input validation completed!

    # Setup the base endpoint for the service call
    service_endpoint = '/api/relations'

    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint=service_endpoint)

    # I have almost everything to call this service so far. This one needs a dictionary as data payload in which the dictionary contents are the search terms to be used in the database query on the remote API side. Build the damn thing then. Start
    # by setting the 'filters' value empty for now... at least until I figure out what the hell this field does...
    data_payload = {"filters": [], "parameters": {"entityId": {"entityType": entityType, "id": entityId}, "rootId": entityId, "rootType": entityType, "direction": direction, "relationTypeGroup": relationTypeGroup,
                    "maxLevel": proj_config.max_query_level, "fetchLastLevelOnly": proj_config.last_level_fetching}}

    # Before submitting the data payload, it turns out that the ThingsBoard API is quite prickly with this one... It doesn't allow for single quotes (') as string delimiters - only double quotes allowed. Also, right now the data payload variable
    # is in dict format, which is irrelevant for the API since this data is going to be transmitted to it via HTTP POST operation, which transforms everything into string format first before sending it to the remote client/server. So,
    # to avoid plenty of headaches from here on (god knows how many I went through until finding out what the hell the API expects and doesn't expect...), cast the whole variable to string now and take the chance to replace any single quotes in it
    # for double ones
    data_payload = str(data_payload).replace("'", "\"")

    # Done. I'm ready to call the service then
    try:
        response = requests.post(url=service_dict['url'], headers=service_dict['headers'], data=data_payload)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        entity_relation_log.error(error_msg)
        raise ce

    # Check if the response code came back a nice HTTP 200
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP " + str(eval(response.text)['status']) + " with message: " + str(eval(response.text)['message'])
        entity_relation_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # All done it appears. Send back the response
        return response
