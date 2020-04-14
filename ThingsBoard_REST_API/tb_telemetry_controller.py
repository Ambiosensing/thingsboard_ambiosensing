""" Place holder for methods related to the ThingsBoard REST API - telemetry-controller methods """

import utils
import proj_config
import requests
import ambi_logger
import datetime
from mysql_database.python_database_modules import mysql_utils, mysql_auth_controller as mac
from mysql_database.python_database_modules import mysql_device_controller


def getTimeseriesKeys(entityType, entityId):
    """This method executes the GET request that returns the name (the ThingsBoard PostGres database key associated to the Timeseries table) of the variable whose quantity is being produced by the element identified by the pair (entityType,
    entityId). This method is limited to 'DEVICE' type elements (it really doesn't make sense for any other type and that's why I should validate this against the allowed entityTypes).
    @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
    @:param entityType (str) - One of the elements in the config.thingsboard_supported_entityTypes dictionary, though for this particular method only 'DEVICE' type elements are allowed (the remote API returns an empty set otherwise)
    @:param entityId (str) - The associated id string. The expected format is 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx', where x is an hexadecimal character.
    @:return response (str) - A string identifying the quantity being measured by the device identified by the input arguments (e.g., 'temperature', 'water consumption', etc..)
    @:raise utils.InputValidationException - If any of the inputs fails validation
    """

    timeseries_key_log = ambi_logger.get_logger(__name__)
    # Input validation
    try:
        utils.validate_input_type(entityType, str)
        utils.validate_input_type(entityId, str)
    except utils.InputValidationException as ive:
        timeseries_key_log.error(ive.message)
        raise ive

    # For this case, I'm not even bothering checking if the entityType is one of the allowed one (config.thingsboard_supported_entityTypes) - This method only makes sense if the entityType is a DEVICE (including being all caps)
    error_msg = None
    expected_entity_type = 'DEVICE'

    if entityType.upper() != expected_entity_type:
        # Eliminate any potential issues with non-upper case characters passed in the entityType in one fell swoop
        error_msg = "The entityType provided is not {0}. This method is restricted to this entity Type!".format(str(expected_entity_type))
    # Validate the entityId string: check the format and if its characters are indeed all hexadecimal
    # The id strings are very strict regarding their format. I can either place bogus calls to the remote API server and catch for a HTTP 500 response or I can use Python to build a more intuitive and helpful logic to achieve the desired format,
    # since this information was only obtained by direct observation of the field itself - the id field is a 36 (32 bytes of data + 4 bytes for the '-') byte one with specific characters ('-') at positions 8, 13, 18 and 23.
    elif len(entityId) != 36:
        error_msg = "The entityId string provided has the wrong format: Wrong number of characters ({0}). Please provide a 36 character string.".format(str(len(entityId)))
    elif entityId[8] != '-' or entityId[13] != '-' or entityId[18] != '-' or entityId[23] != '-':
        error_msg = "The entityId doesn't have the expected format (expect a '-' at character positions 8, 13, 18 and 23): {0}".format(str(entityId))
        # Get out of the loop if as soon as an error is detected
    else:
        # Start by getting all the hexadecimal blocks in a nice list and removing the '-' character in the process
        segments = entityId.split('-')
        # The easiest way to test if a given string only has hexadecimal characters in it is to try to cast it to an integer forcing a base 16 in the process, i.e., doing a decoding operation assuming a base 16 reference. If any of the characters
        # in any of those segments is not hexadecimal (0-F), the operation throws a ValueError Exception that I can caught
        for segment in segments:
            try:
                int(segment, 16)
            except ValueError:
                error_msg = "One of the entityId string has non-hexadecimal characters in it: {0}. Please provide a 36 long, hexadecimal string for this field.".format(str(segment))
                # End this loop as soon something wrong is detected
                break

    if error_msg:
        timeseries_key_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Validation done. Lets get data from the remote API then
    service_endpoint = "/api/plugins/telemetry/"

    service_endpoint += "{0}/{1}/keys/timeseries".format(str(expected_entity_type), str(entityId))
    # NOTE: This particular service requires a REGULAR type authorization token, so admin=False
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        timeseries_key_log.error(error_msg)
        raise ce

    # Test the HTTP status code in the response (I'm only continuing if it is a 200 and, in this particular case, a single str element was returned)
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received an HTTP {0} with message: {1}".format(str(eval(response.text)['status']), str(eval(response.text)['message']))
        timeseries_key_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # The objective here is to return the string with the key that I need to call another endpoint service to get actual data from the device. If the data is correct and there's a key associated to that, I should get a single list with a
        # string as its only element back. If the device exists but it still doesn't have a timeSeries associated to it, I would get an empty list back
        # Start to cast the response.text to a list
        result = eval(response.text)

        try:
            # Raise an Exception if the data type obtained is different from the expected
            utils.validate_input_type(result, list)
        except utils.InputValidationException as ive:
            timeseries_key_log.error(ive.message)
            raise ive

        # In some cases I may have a multi-sensor device (which is actually the case in our prototype setting), which means that this result may be an array of all the supported timeseries keys. In this case, the return needs to be processed that way
        # Check if, at least, one result was returned
        if not len(result):
            # Warn the user first
            timeseries_key_log.warning("There are no keys associated to {0} with id {1} yet!".format(str(entityType), str(entityId)))
            # Return a result that is passable to be used by another calling method
            return None
        else:
            # If all goes well, return the expected value. NOTE: This method returns these results as is, i.e., just like they are returned from the remote API, which means that 'result' is going to be a list that potentially may have multiple
            # elements (if the DEVICE identified by the ID has multiple sensors measuring different variables at once). The method that consumes these results should take heed on this
            return result


def getTimeseries(device_name, end_date, start_date=None, time_interval=None, interval=None, limit=100, agg=None, timeseries_keys_filter=None):
    """This method is the real deal, at least to establish a base methodology to retrieve hard data from the remote API server. Unlike other API based methods so far, this one requires some data to be present in the MySQL server already because
    that is where the actual method call input data is going to come from. The remote API service that retrieves the requested data requires 5 mandatory elements (the optional arguments are explicit in the calling signature of this method where
    they are set to their default values already, in case that down the line there is a need to use them): entityType, entityId, keys, startTs and endTs. The first 3 parameters are going to be retrieved with a call to the MySQL
    thingsboard_devices_table and the timestamp ones are going to be determined from the triplet start_time (mandatory), ent_time and time_interval (only one of these is required). The method returns a dictionary with a list of timestamp,
    value pairs that can or cannot be limited by the limit value
    @:type user_types allowed for this service: TENANT_ADMIN, CUSTOMER_USER
    @:param device_name (str) - The name of the device to retrieve data from (e.g., 'Thermometer A-1', 'Water Meter A-1', etc... whatever the string used when registering the device in the ThingsBoard system). This value is certainly easier to
    retained and/or memorized from the user than the id string, for instance.
    @:param end_date (datetime.datetime) - A datetime.datetime object, i.e., in the format YYYY-MM-DD hh:mm:ss but that belongs to the datetime.datetime class. This is the latest value of the interval and, to avoid invalid dates into the input (
    like future dates and such) this one is mandatory. The interval to be considered is going to be defined by either start_time (earliest) -> end_time (latest) or end_time - time_interval (in seconds) -> end_time, but one of the next two input
    arguments has to be provided.
    @:param start_date (datetime.datetime) - A datetime.datetime object delimiting the earliest point of the time interval for data retrieval
    @:param time_interval (int) - An interval, in seconds, to be subtracted to the end_time datetime object in order to define the time window to return data from
    @:param interval (int) - This is an OPTIONAL API side only parameter whose use still eludes me... so far I've tried to place calls to the remote service with all sorts of values in this field and I'm still to discover any influence of it in
    the returned results. NOTE: My initial assumption was it to be able to be set as a API side version of my time_interval. Yet, that is not the case because the API requires both the end and start timestamps to be provided by default.
    @:param limit (int) - The number of results to return in the request. Device data can be quite a lot to process and that's why this parameter, though optional, is set to 100 by default. Two things with this value: though the API doesn't
    explicitly says so, it doesn't like limit <= 0. It doesn't return an error per se but instead the service gets stuck until eventually an HTTP 503 - Service Unavailable is thrown instead. As such I'm going to validate this input accordingly.
    Also, unlike other limit parameters so far, there's no indication in the response structure if the number of results returned were limited by this value or by the time interval defined. To provide the user with more helpful information in this
    regard, this method is going to count the number of returned results and, if they do match the limit value provided, warn the user about it.
    @:param agg (str) - No idea what this one does too... The API testing interface has it set to NONE by default, though it is an optional parameter whose effect on the returned results is still yet to be understood. ALl I know so far is that the
    remote API expects a string on it
    @:param timeseries_keys_filter (list of str) - A list with strings with the keys to be returned from the remote API. Some devices contain multiple sensors, which means that there are going to be multiple records from different variables under
    the same device ID. To limit the returned results to a sub set of all parameters, provide a list in this argument with the correct names to limit the entries to be returned. Omitting this parameter (which defaults to None) returns all
    timeseries keys under the provided device ID
    @:return result_list (list of tuple) - The returned results are going to be processed and returned as a list of 2 element-tuples: a timestamp and the associated value for the timeseriesKey provided.
    @:raise utils.InputValidationException - If any of the inputs provided fails validation
    @:raise utils.ServiceEndpointException - If something goes wrong with any of the external service calls to the remote API executed in the method
    @:raise mysql_utils.MySQLDatabaseException - For errors derived from the MySQL database accesses
    @:raise Exception - For any other detected errors during the method's execution
    """
    timeseries_log = ambi_logger.get_logger(__name__)

    # Before moving forward, check if at least one of the start_time, time_interval inputs was provided. NOTE: If both inputs are present, i.e., not None, the method validates both and if both are valid it prioritizes start_time over
    # time_interval. If one of them happens to be invalid, the method execution is not stopped but the user gets warned (through the logger) about this and how the method is going to be operated. But at this stage, I'm only moving forward if I
    # have the conditions to setup a valid time window for the API request
    if not start_date and not time_interval:
        error_msg = "Please provide at least one valid start_time (datetime.datetime) or a time_interval (int). Cannot compute a time window for data retrieval otherwise.."
        timeseries_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Time for validate inputs
    utils.validate_input_type(device_name, str)
    utils.validate_input_type(end_date, datetime.datetime)
    # Limit is OPTIONAL but, because of what is explained in this method's man entry, I need this value to be sort of mandatory. This verification, given that the input is already set with a decent default value, is just to protect the
    # method's execution against a user setting it to None by whatever reason that may be
    utils.validate_input_type(limit, int)
    if start_date:
        utils.validate_input_type(start_date, datetime.datetime)
    if time_interval:
        utils.validate_input_type(time_interval, int)
    if interval:
        utils.validate_input_type(interval, int)
    if agg:
        utils.validate_input_type(agg, str)

    # Validate the argument against the list type
    if timeseries_keys_filter:
        utils.validate_input_type(timeseries_keys_filter, list)

        if len(timeseries_keys_filter) <= 0:
            timeseries_log.warning("Invalid timeseries keys filter provided: empty list. This filter is going to be ignored")
            timeseries_keys_filter = None
        else:
            # And each of its elements against the expected str type
            for timeseries in timeseries_keys_filter:
                utils.validate_input_type(timeseries, str)

    # Data type validation done. Now for the functional validations
    error_msg = None
    if limit <= 0:
        error_msg = "Invalid limit value: {0}. Please provide a greater than zero integer for this argument.".format(str(limit))
    elif end_date > datetime.datetime.now():
        error_msg = "Invalid end_date date provided: {0}! The date hasn't happen yet (future date). Please provide a valid datetime value!".format(str(end_date))
    elif start_date and not time_interval and start_date >= end_date:
        error_msg = "Invalid start_date date! The start_date provided ({0}) is newer/equal than/to the end_date date ({1}): invalid time window defined!".format(str(start_date), str(end_date))
    elif time_interval and not end_date and time_interval <= 0:
        error_msg = "Invalid time interval ({0})! Please provide a greater than zero value for this argument (the number of seconds to subtract from end_date).".format(str(time_interval))
    elif start_date and time_interval and start_date >= end_date and time_interval <= 0:
        error_msg = "Both start_date and time_interval arguments provided are invalid!\nThe start_date provided ({0}) is newer than the end_date indicated ({1}) and the time_interval as an invalid value ({2}).\n" \
                    "Please provide a valid (older) start_date or a valid (greater than 0) time_interval".format(str(start_date), str(end_date), str(time_interval))

    if error_msg:
        timeseries_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # And now for the cases where both valid start_time and time_interval were provided. The previous validation bundle made sure that, if only one of these two parameters was provided, it was valid. If I got to this point I can have both of these
    # parameter set to valid inputs but I need to warn the user that I'm only going to use one to define the time window
    if start_date and time_interval:
        timeseries_log.warning("Both start_time and time_interval provided arguments are valid but only start_time is going to be considered moving on. Set this argument to None/Invalid to use the time_interval instead")
        # So, if I'm dropping the time_interval, I need to signal this somehow moving forward:
        time_interval = None

    # Retrieve the device's credentials using the appropriate method
    device_cred = mysql_device_controller.get_device_credentials(device_name=device_name)

    # Check if a valid set of credentials was found
    if device_cred is None:
        error_msg = "Unable to retrieve a set of valid credentials to device '{0}'".format(str(device_name))
        timeseries_log.error(error_msg)
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    # The first 3 elements that I need to build the service endpoint are valid and retrieved. Lets deal with the time window then. The service endpoint requires that the limits of this window (startTs, endTs) to be passed in that weird POSIX
    # timestamp-like format that the ThingsBoard PostGres database adopted, i.e, a 13 digit number with no decimal point (10 digits for the integer part + 3 for the microseconds value... but with the decimal point omitted...). Fortunately I've
    # written the 'translate' functions already for this situation
    end_ts = mysql_utils.convert_datetime_to_timestamp_tb(end_date)

    # If the other end is defined by the start_time datetime.datetime object
    if start_date:
        # Easy
        start_ts = mysql_utils.convert_datetime_to_timestamp_tb(start_date)

    # If I got to this point in the code, given the brutality of validations undertaken so far, I can only get here with start_time = None and something valid in time_interval. Proceed accordingly
    else:
        # I need to convert this interval to a timedelta object to be able to subtract it to the end_time one
        time_interval = datetime.timedelta(seconds=int(time_interval))
        start_time = end_date - time_interval
        start_ts = mysql_utils.convert_datetime_to_timestamp_tb(start_time)

    # Done with the validations. Start building the service endpoint then.
    service_endpoint = "/api/plugins/telemetry/" + str(device_cred[0]) + "/" + str(device_cred[1]) + "/values/timeseries?"

    url_elements = []

    if interval:
        url_elements.append("interval=" + str(interval))

    url_elements.append("limit=" + str(limit))

    if agg:
        url_elements.append("agg=" + str(agg))

    # The element in result[2] can be a string containing multiple timeseries keys (if the device in question is a multisensor one). If a timeseries filter was provided, it is now time to apply it to reduce the number of variable types returned
    if timeseries_keys_filter:
        # Grab the original string list to a single variable
        device_ts_keys_list = str(device_cred[2])
        valid_keys = []
        for timeseries_key in timeseries_keys_filter:
            # And now check if any of the elements passed in the filter list is in the initial list
            if timeseries_key in device_ts_keys_list:
                # Add it to the valid keys list if so
                valid_keys.append(timeseries_key)
            # Otherwise warn the user of the mismatch
            else:
                timeseries_log.warning("The filter key '{0}' provided in the filter list is not a valid timeseries key. Ignoring it...".format(str(timeseries_key)))

        # If the last loop didn't yield any valid results, warn the user and default to the original string list
        if not len(valid_keys):
            timeseries_log.warning("Unable to apply timeseries key filter: none of the provided keys had a match. Defaulting to {0}...".format(str(device_ts_keys_list)))
            valid_keys = device_ts_keys_list
        else:
            # And inform the user of the alteration
            timeseries_log.info("Valid filter found. Running remote API query with keys: {0}".format(str(valid_keys)))

        url_elements.append("keys=" + ",".join(valid_keys))

    else:
        # No filters required. Append the full timeseries elements then
        url_elements.append("keys=" + ",".join(device_cred[2]))

    url_elements.append("startTs=" + str(start_ts))
    url_elements.append("endTs=" + str(end_ts))

    # Done. Now mash up the whole thing into a '&' separated string
    service_endpoint += "&".join(url_elements)

    # I'm finally ready to query the remote endpoint. This service requires a REGULAR type authorization token
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint)

    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout):
        error_msg = "Unable to establish a connection with {0}...".format(str(service_dict['url']))
        timeseries_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)

    # Check first if the response came back with a HTTP 200
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received HTTP {0} with message: {1}".format(str(response.status_code), str(eval(response.text)['message']))
        timeseries_log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # The results are going to be returned as a dictionary of dictionaries in the following format:
        # result_dict = {
        #               "timeseries_key_1": [
        #                   {'ts': int, 'value': str},
        #                   {'ts': int, 'value': str},
        #                   ...
        #                   {'ts': int, 'value': str}
        #               ],
        #               "timeseries_key_2": [
        #                   {'ts': int, 'value': str},
        #                   {'ts': int, 'value': str},
        #                   ...
        #                   {'ts': int, 'value': str}
        #               ],
        #               ...
        #               "timeseries_key_N": [
        #                   {'ts': int, 'value': str},
        #                   {'ts': int, 'value': str},
        #                   ...
        #                   {'ts': int, 'value': str}
        #               ]
        # }
        # Use this as a reference for when another method needs to consume data from this response. Its a over complicated structure, honestly, and its not hard to create a simple method to call after this to simplify it greatly. But there's no
        # point in doing that until we know exactly what is the format that need to be returned.

        # Apply the 'eval' base method just to transform the str that is returned into a dict
        result_dict = eval(response.text)

        # Finally, check if any of the entries in the returned dictionary matches the 'limit' parameter and warn the user of potential missing results if so
        for result_key in list(result_dict.keys()):
            if len(result_dict[result_key]) == limit:
                timeseries_log.warning("Timeseries key '{0}' results were limited by the 'limit' parameter: got {1} valid results back".format(str(result_key), str(limit)))

        # Return the result dictionary finally
        return result_dict


def getLatestTimeseries(device_name, timeseries_keys_filter=None):
    """
    This method is analogous to the previous one, i.e., it also retrieves Timeseries data that is associated to the device identified by 'device_name', but in this particular case only one timestamp/value pair is returned for each of the device's
    measurements, namely the last one recorded by the Thingsboard installation that oversees that device. This method is very useful to:
    1. Determine if a device is working by retrieving the last recorded data.
    2. Determine the timeseries keys associated to the device, as well the last timestamp associated to them.
    3. Determine the most recent end_date possible for that device in a direct way - once this parameter is known, a more complete and insightful getTimeseries call can then be placed.
    @:param device_name (str) - The name of the device to which the latest associated timeseries should be retrieved by this method.
    @:param timeseries_keys_filter (list of str) - A list with the names of the timeseries keys to be returned by the remote API. If a valid list is provided, only data for the keys specified in this list are going to be returned. This method
    validates this list against any associated timeseriesKeys for the device: mismatched elements from this list are to be ignored.
    @:raise utils.InputValidationException - If any of the inputs fails initial validation
    @:raise utils.ServiceEndpointException - If errors occur when invoking any remote API services
    @:raise mysql_utils.MySQLDatabaseException - If errors occur when accessing the database
    @:return None if the API returns an empty set, otherwise returns a dictionary with the following format:
    device_data =
    {
        "timeseriesKey_1": [
            {
              "ts": int,
              "value": str
            }
        ],
        "timeseriesKey_2": [
            {
              "ts": int,
              "value": str
            }
        ],
        ...
        "timeseriesKey_N": [
            {
                "ts": int,
                "value": str
            }
        ]
    }
    """
    log = ambi_logger.get_logger(__name__)

    utils.validate_input_type(device_name, str)
    if timeseries_keys_filter:
        utils.validate_input_type(timeseries_keys_filter, list)

        for ts_key in timeseries_keys_filter:
            utils.validate_input_type(ts_key, str)

    # Grab the device credentials at this point. If the method returns anything (not None), than assume that its the following tuple: (entityType, entityId, timeseriesKeys_list)
    device_cred = mysql_device_controller.get_device_credentials(device_name=device_name)

    if device_cred is None:
        error_msg = "Could not get valid credentials for device '{0}'. Cannot continue...".format(str(device_name))
        log.error(error_msg)
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    # Validate the timeseries keys, if any were provided
    keys = None
    if timeseries_keys_filter:
        valid_keys = []
        for ts_filter_key in timeseries_keys_filter:
            # Filter out only the valid keys, i.e., the ones with a correspondence in the list returned from the database
            if ts_filter_key in device_cred[2]:
                valid_keys.append(ts_filter_key)

        # Check if at least one of the proposed keys made it to the valid list. If not, default to the list returned from the database (if this one is also not empty)
        if not len(valid_keys):
            log.warning("Could not validate any of the filter keys ({0}) provided as argument!".format(str(timeseries_keys_filter)))

            # Check if the timeseriesKeys element returned from the device credentials request was a single element list with an empty string inside it
            if len(device_cred[2]) == 1 and device_cred[2][0] == "":
                log.warning("The database didn't return any valid set of timeseriesKeys. Omitting this argument in the API call")
                # Don't do anything else. The 'keys' parameter is already None. Keep it as that then
        else:
            keys = ",".join(valid_keys)

    # I have all I need to execute the remote API call
    service_endpoint = "/api/plugins/telemetry/{0}/{1}/values/timeseries".format(str(device_cred[0]), str(device_cred[1]))

    # Add the keys filter, if it was provided
    if keys is not None:
        service_endpoint += "?keys={0}".format(str(keys))

    # Service endpoint is done. Grab the service calling dictionary
    service_dict = utils.build_service_calling_info(auth_token=mac.get_auth_token(user_type='tenant_admin'), service_endpoint=service_endpoint)

    # Execute the remote call finally
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout):
        error_msg = "Unable to establish a connection with {0}...".format(str(service_dict['url']))
        log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)

    # Check the HTTP status code in the response
    if response.status_code != 200:
        error_msg = "Request unsuccessful: Received HTTP {0} with message {1}!".format(str(response.status_code), str(eval(response.text)['message']))
        log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Send back the response already in dictionary form
        return eval(response.text)


def getAttributes(entityType=None, entityId=None, deviceName=None, keys=None):
    """
    GET method to retrieve all server-type attributes configured for the device identified by the pair entityType/entityId or deviceName provided. This method requires either the entityType/entityId pair or the deviceName to be provided to execute
    this method. If insufficient data is provided, the relevant Exception shall be raised.
    :param entityType (str) - The entity type of the object whose attributes are to be retrieved.
    :param entityId (str) - The id string that identifies the device whose attributes are to be retrieved.
    :param deviceName (str) - The name of the device that can be used to retrieve the entityType/entityId.
    :param keys (list of str) - Each attribute returned is a key-value pair. Use this argument to provide a key based filter, i.e., if this list is set, only attributes whose keys match any of the list elements are to be returned.
    :raise utils.InputValidationException - If any of the inputs has the wrong data type or the method doesn't have the necessary data to execute.
    :raise utils.ServiceEndpointException - If problem occur when accessing the remote API
    :return attribute_dictionary (dict) - A dictionary with the retrieved attributes in the following format:
        attribute_dictionary =
        {
            'attribute_1_key': 'attribute_1_value',
            'attribute_2_key': 'attribute_2_value',
            ...
            'attribute_N_key': 'attribute_N_value'
        }
        where the keys in the dictionary are the ontology-specific names (official names) and the respective values are the timeseries keys being measured by the device that map straight into those ontology names.
        If the device identified by the argument data does exist but doesn't have any attributes configured, this method returns None instead.
    """
    log = ambi_logger.get_logger(__name__)

    # Validate inputs
    if entityId:
        utils.validate_id(entity_id=entityId)

        # The entityId seems OK but its useless unless the entityType was also provided or, at least, the deviceName, the method cannot continue
        if not entityType and not deviceName:
            error_msg = "A valid entityId was provided but no entityType nor deviceName were added. Cannot execute this method until a valid entityType/entityId or a valid deviceName is provided!"
            log.error(error_msg)
            raise utils.InputValidationException(message=error_msg)

    if entityType:
        utils.validate_entity_type(entity_type=entityType)

        # Again, as before, the method can only move forward if a corresponding entityId or deviceName was also provided
        if not entityId and not deviceName:
            error_msg = "A valid entityType was provided but no corresponding entityId nor deviceName. Cannot continue until a valid entityType/entityId or a valid deviceName is provided!"
            log.error(error_msg)
            raise utils.InputValidationException(message=error_msg)

    if deviceName:
        utils.validate_input_type(deviceName, str)

    if keys:
        utils.validate_input_type(keys, list)
        for key in keys:
            utils.validate_input_type(key, str)

    # If the code got to this point, I either have a valid entityId/entityType pair or a deviceName. Check if only the deviceName was provided and retrieve the entityId/entityType from it
    if deviceName and (not entityType or not entityId):
        # Get the entityId and entityType from the deviceName provided
        device_data = mysql_device_controller.get_device_credentials(device_name=deviceName)

        # Check if the previous statement returned a non-empty (not None) result. If that is the case, either the device is not (yet) configured in the device table or the table needs to be updated
        if not device_data:
            error_msg = "Cannot retrieve a pair of entityId/entityType from the device name provided: {0}. Either:" \
                        "\n1. The device is not yet configured in the database/ThingsBoard platform" \
                        "\n2. The MySQL device table needs to be updated." \
                        "\nCannot continue for now".format(str(deviceName))
            log.error(error_msg)
            raise utils.InputValidationException(message=error_msg)

        # The previous method returns a 3-element tuple in the format (entityType, entityId, timeseriesKeys). Grab the relevant data straight from it
        entityType = device_data[0]
        entityId = device_data[1]

    # Validation complete. I have all I need to execute the remote call
    service_endpoint = "/api/plugins/telemetry/{0}/{1}/values/attributes".format(str(entityType), str(entityId))

    # If a list of keys was provided, concatenate them to the current endpoint
    if keys:
        service_endpoint += "?keys="

        # Add all the keys to the endpoint concatenated in a single, comma separated (without any spaces in between) string
        service_endpoint += ",".join(keys)

    # Build the service dictionary from the endpoint already built
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='tenant_admin'), service_endpoint=service_endpoint)

    # Query the remote API
    try:
        response = requests.get(url=service_dict['url'], headers=service_dict['headers'])
    except (requests.ConnectionError, requests.ConnectTimeout) as ce:
        error_msg = "Could not get a response from {0}...".format(str(service_dict['url']))
        log.error(error_msg)
        raise utils.ServiceEndpointException(message=ce)

    # If a response was returned, check the HTTP return code
    if response.status_code != 200:
        error_msg = "Request not successful: Received an HTTP " + str(eval(response.text)['status']) + " with message: " + str(eval(response.text)['message'])
        log.error(error_msg)
        raise utils.ServiceEndpointException(message=error_msg)
    else:
        # Got a valid result. Format the returned objects for return
        data_to_return = eval(utils.translate_postgres_to_python(response.text))

        if len(data_to_return) is 0:
            # Nothing to return then. Send back a None instead
            return None

        # If the request was alright, I've received the following Response Body (after eval)
        # data_to_return =
        # [
        #   {
        #       "lastUpdateTs": int,
        #       "key": str,
        #       "value": str
        #   },
        # ...
        #   {
        #       "lastUpdateTs": int,
        #       "key": str,
        #       "value": str
        #   }
        # ]
        #
        # So I need to transform this into the return structure defined above

        attribute_dictionary = {}
        for attribute_pair in data_to_return:
            # Use this opportunity to filter out any attribute returned that is not part of the measurement list desired
            if attribute_pair['value'] not in proj_config.ontology_names:
                # If the attribute value is not one in the 'official list of names', skip it
                continue
            # Create the entries defined in the man entry of this method from the list elements returned from the remote API
            attribute_dictionary[attribute_pair['key']] = attribute_pair['value']

        # All done. Return the attributes dictionary
        return attribute_dictionary
