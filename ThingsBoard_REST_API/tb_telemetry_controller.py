""" Place holder for methods related to the ThingsBoard REST API - telemetry-controller methods """

import utils
import proj_config
import requests
import ambi_logger
import datetime
from mysql_database.python_database_modules import mysql_utils


def getTimeseriesKeys(entityType, entityId):
    """This method executes the GET request that returns the name (the ThingsBoard PostGres database key associated to the Timeseries table) of the variable whose quantity is being produced by the element identified by the pair (entityType,
    entityId). This method is limited to 'DEVICE' type elements (it really doesn't make sense for any other type and that's why I should validate this against the allowed entityTypes).
    @:param entityType (str) - One of the elements in the config.thingsbard_supported_entityTypes dictionary, though for this particular method only 'DEVICE' type elements are allowed (the remote API returns an empty set otherwise)
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
    service_dict = utils.build_service_calling_info(utils.get_auth_token(admin=False), service_endpoint)

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

        # This should never happen, but check it anyway
        if len(result) > 1:
            # If I do get a list back but it is empty
            error_msg = "There are multiple key associated to {0} with id {1}: Found {2} timeseries keys!".format(str(entityType), str(entityId), str(len(result)))
            timeseries_key_log.error(error_msg)
            raise Exception(error_msg)
        # If the result returned is an empty list
        elif not len(result):
            # Warn the user first
            timeseries_key_log.warning("There are no keys associated to {0} with id {1} yet!".format(str(entityType), str(entityId)))
            # Return a result that is passable to be used by another calling method
            return None
        else:
            # If all goes well, return the expected value
            return result[0]


def getTimeseries(device_name, end_time, start_time=None, time_interval=None, interval=None, limit=100, agg=None):
    """This method is the real deal, at least to establish a base methodology to retrieve hard data from the remote API server. Unlike other API based methods so far, this one requires some data to be present in the MySQL server already because
    that is where the actual method call input data is going to come from. The remote API service that retrieves the requested data requires 5 mandatory elements (the optional arguments are explicit in the calling signature of this method where
    they are set to their default values already, in case that down the line there is a need to use them): entityType, entityId, keys, startTs and endTs. The first 3 parameters are going to be retrieved with a call to the MySQL
    thingsboard_devices_table and the timestamp ones are going to be determined from the triplet start_time (mandatory), ent_time and time_interval (only one of these is required). The method returns a dictionary with a list of timestamp,
    value pairs that can or cannot be limited by the limit value
    @:param device_name (str) - The name of the device to retrieve data from (e.g., 'Thermometer A-1', 'Water Meter A-1', etc... whatever the string used when registering the device in the ThingsBoard system). This value is certainly easier to
    retained and/or memorized from the user than the id string, for instance.
    @:param end_time (datetime.datetime) - A datetime.datetime object, i.e., in the format YYYY-MM-DD hh:mm:ss but that belongs to the datetime.datetime class. This is the latest value of the interval and, to avoid invalid dates into the input (
    like future dates and such) this one is mandatory. The interval to be considered is going to be defined by either start_time (earliest) -> end_time (latest) or end_time - time_interval (in seconds) -> end_time, but one of the next two input
    arguments has to be provided.
    @:param start_time (datetime.datetime) - A datetime.datetime object delimiting the earliest point of the time interval for data retrieval
    @:param time_interval (int) - An interval, in seconds, to be subtracted to the end_time datetime object in order to define the time window to return data from
    @:param interval (int) - This is an OPTIONAL API side only parameter whose use still eludes me... so far I've tried to place calls to the remote service with all sorts of values in this field and I'm still to discover any influence of it in
    the returned results. NOTE: My initial assumption was it to be able to be set as a API side version of my time_interval. Yet, that is not the case because the API requires both the end and start timestamps to be provided by default.
    @:param limit (int) - The number of results to return in the request. Device data can be quite a lot to process and that's why this parameter, though optional, is set to 100 by default. Two things with this value: though the API doesn't
    explicitly says so, it doesn't like limit <= 0. It doesn't return an error per se but instead the service gets stuck until eventually an HHTP 503 - Service Unavailable is thrown instead. As such I'm going to validate this input accordingly.
    Also, unlike other limit parameters so far, there's no indication in the response structure if the number of results returned were limited by this value or by the time interval defined. To provide the user with more helpful information in this
    regard, this method is going to count the number of returned results and, if they do match the limit value provided, warn the user about it.
    @:param agg (str) - No idea what this one does too... The API testing interface has it set to NONE by default, though it is an optional parameter whose effect on the returned results is still yet to be understood. ALl I know so far is that the
    remote API expects a string on it
    @:return result_list (list of tuple) - The returned results are going to be processed and returned as a list of 2 element-tuples: a timestamp and the associated value for the timeseriesKey provided.
    @:raise utils.InputValidationException - If any of the inputs provided fails validation
    @:raise utils.ServiceEndpointException - If something goes wrong with any of the external service calls to the remote API executed in the method
    @:raise mysql_utils.MySQLDatabaseException - For errors derived from the MySQL database accesses
    @:raise Exception - For any other detected errors during the method's execution
    """
    timeseries_log = ambi_logger.get_logger(__name__)
    # The key that I need to use to retrieve the name of the table in the MySQL database where the necessary data to call this method is currently stored (specifically, the entityType, entityId and timeseriesKey
    module_table_key = "devices"
    # Put those in an handy list to so that I don't need to type them down all the time
    columns_to_retrieve = ['entityType', 'id', 'timeseriesKey']

    # Before moving forward, check if at least one of the start_time, time_interval inputs was provided. NOTE: If both inputs are present, i.e., not None, the method validates both and if both are valid it prioritizes start_time over
    # time_interval. If one of them happens to be invalid, the method execution is not stopped but the user gets warned (through the logger) about this and how the method is going to be operated. But at this stage, I'm only moving forward if I
    # have the conditions to setup a valid time window for the API request
    if not start_time and not time_interval:
        error_msg = "Please provide at least one valid start_time (datetime.datetime) or a time_interval (int). Cannot compute a time window for data retrieval otherwise.."
        timeseries_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Time for validate inputs
    try:
        utils.validate_input_type(device_name, str)
        utils.validate_input_type(end_time, datetime.datetime)
        # Limit is OPTIONAL but, because of what is explained in this method's man entry, I need this value to be sort of mandatory. This verification, given that the input is already set with a decent default value, is just to protect the
        # method's execution against a user setting it to None by whatever reason that may be
        utils.validate_input_type(limit, int)
        if start_time:
            utils.validate_input_type(start_time, datetime.datetime)
        if time_interval:
            utils.validate_input_type(time_interval, int)
        if interval:
            utils.validate_input_type(interval, int)
        if agg:
            utils.validate_input_type(agg, str)
    except utils.InputValidationException as ive:
        timeseries_log.error(ive.message)
        raise ive

    # Data type validation done. Now for the functional validations
    error_msg = None
    if limit <= 0:
        error_msg = "Invalid limit value: {0}. Please provide a greater than zero integer for this argument.".format(str(limit))
    elif end_time > datetime.datetime.now():
        error_msg = "Invalid end_time date provided: {0}! The date hasn't happen yet (future date). Please provide a valid datetime value!".format(str(end_time))
    elif start_time and not time_interval and start_time >= end_time:
        error_msg = "Invalid start_time date! The start_date provided ({0}) is newer/equal than/to the end_time date ({1}): invalid time window defined!".format(str(start_time), str(end_time))
    elif time_interval and not end_time and time_interval <= 0:
        error_msg = "Invalid time interval ({0})! Please provide a greater than zero value for this argument (the number of seconds to subtract from end_time).".format(str(time_interval))
    elif start_time and time_interval and start_time >= end_time and time_interval <= 0:
        error_msg = "Both start_time and time_interval arguments provided are invalid!\nThe start_time provided ({0}) is newer than the end_time indicated ({1}) and the time_interval as an invalid value ({2}).\n" \
                    "Please provide a valid (older) start_time or a valid (greater than 0) time_interval".format(str(start_time), str(end_time), str(time_interval))

    if error_msg:
        timeseries_log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # And now for the cases where both valid start_time and time_interval were provided. The previous validation bundle made sure that, if only one of these two parameters was provided, it was valid. If I got to this point I can have both of these
    # parameter set to valid inputs but I need to warn the user that I'm only going to use one to define the time window
    if start_time and time_interval:
        timeseries_log.warning("Both start_time and time_interval provided arguments are valid but only start_time is going to be considered moving on. Set this argument to None/Invalid to use the time_interval instead")
        # So, if I'm dropping the time_interval, I need to signal this somehow moving forward:
        time_interval = None

    # The inputs seem to be all valid. Lets get the necessary data to call the remote service then. To make this service more robust, I'm doing an initial SELECT to the devices database using the device_name as it is provided. If the SELECT
    # statement doesn't return any results, I will then repeat the statement but using a LIKE name = %device_name statement instead of the WHERE clause, followed by a LIKE name = device_name% and ending with a final call using LIKE name =
    # %device_name%, i.e., using wildcard search parameters in the beginning, end and both beginning and end of the device name string. The objective here is to get a single entry from the database table: multiple results or no results discard the
    # current SQL SELECT statement and move the code to the next option. If non definite results are obtained, a MySQLDatabaseException is going to be raised signaling this fact.

    cnx = mysql_utils.connect_db(proj_config.mysql_db_access['database'])
    select_cursor = cnx.cursor(buffered=True)

    # Create the base SQL SELECT statement. I can then change the wildcards to be considered in the LIKE clause directly in the argument to replace the follwing %s
    sql_select = """SELECT """ + ", ".join(columns_to_retrieve) + """ FROM """ + str(proj_config.mysql_db_tables[module_table_key]) + """ WHERE name LIKE %s;"""

    # Execute the statement in its basic form
    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (device_name,))

    # The number of returned results from the previous statement can be determined by checking the cursor's rowcount variable (cool, I was afraid that I had to do SELECT COUNT(*) to determine this. The python-mysql adapter does have its advantages
    # indeed!)
    if select_cursor.rowcount != 1:
        # Add a wild card value to the end of the device name
        new_device_name = device_name + "%"
        timeseries_log.warning("Unable to get a single result searching for device_name = {0} (got {1} results instead). Trying again using device_name = {2}...".format(str(device_name), str(select_cursor.rowcount), str(new_device_name)))
        select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (new_device_name,))

        if select_cursor.rowcount != 1:
            timeseries_log.warning("Unable to get a single result searching for device_name = {0} (got {1} results instead). Trying again using device_name = {2}...".format(str(new_device_name), str(select_cursor.rowcount), str("%" + device_name)))
            # Try again with a new wildcard position
            new_device_name = "%" + device_name
            select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (new_device_name,))

            if select_cursor.rowcount != 1:
                timeseries_log.warning("Unable to get a single result searching for device_name = {0} (got {1} results instead). Trying again using device_name = {2}..."
                                       .format(str(new_device_name), str(select_cursor.rowcount), str(new_device_name + "%")))
                # One last try with wildcards on both ends of the device name
                new_device_name += "%"
                select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (new_device_name,))

                if select_cursor.rowcount != 1:
                    error_msg = "The method was unable to retrieve an unique record for device_name = {0} (got {1} results instead). Nowhere to go but out now...".format(str(new_device_name), str(select_cursor.rowcount))
                    timeseries_log.error(error_msg)
                    exit(-1)

    # If my select_cursor was able to transverse the last swamp in safety, retrieve the result that I'm looking for (I shall get a 3 element tuple with (entityType, id, timeseriesKey) - all strings then)
    result = select_cursor.fetchone()

    # There's a possibility that a device is already in the MySQL database but, by some reason, it doesn't have an associated timeseriesKey yet (the 3rd element of the result tuple should be NULL then). Check for that first before moving further
    if not result[2]:
        error_msg = "Found a valid device with id = {0} but without an associated timeseriesKey - device not initialized yet! Cannot continue.".format(str(result[1]))
        timeseries_log.error(error_msg)
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    try:
        utils.validate_input_type(result, tuple)
    except utils.InputValidationException as ive:
        timeseries_log.error(ive.message)
        raise ive

    if len(result) != 3:
        error_msg = "Wrong number of values returned from the MySQL database! Expected 3 elements, got {0}!".format(str(len(result)))
        timeseries_log.error(error_msg)
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    # The first 3 elements that I need to build the service endpoint are valid and retrieved. Lets deal with the time window then. The service endpoint requires that the limits of this window (startTs, endTs) to be passed in that weird POSIX
    # timestamp-like format that the ThingsBoard PostGres database adopted, i.e, a 13 digit number with no decimal point (10 digits for the integer part + 3 for the microseconds value... but with the decimal point omitted...). Fortunately I've
    # written the 'translate' functions already for this situation
    end_ts = mysql_utils.convert_datetime_to_timestamp_tb(end_time)

    # If the other end is defined by the start_time datetime.datetime object
    if start_time:
        # Easy
        start_ts = mysql_utils.convert_datetime_to_timestamp_tb(start_time)

    # If I got to this point in the code, given the brutality of validations undertaken so far, I can only get here with start_time = None and something valid in time_interval. Proceed accordingly
    else:
        # I need to convert this interval to a timedelta object to be able to subtract it to the end_time one
        time_interval = datetime.timedelta(seconds=int(time_interval))
        start_time = end_time - time_interval
        start_ts = mysql_utils.convert_datetime_to_timestamp_tb(start_time)

    # Done with the validations. Start building the service endpoint then.
    service_endpoint = "/api/plugins/telemetry/" + str(result[0]) + "/" + str(result[1]) + "/values/timeseries?"

    url_elements = []

    if interval:
        url_elements.append("interval=" + str(interval))

    url_elements.append("limit=" + str(limit))

    if agg:
        url_elements.append("agg=" + str(agg))

    url_elements.append("keys=" + str(result[2]))
    url_elements.append("startTs=" + str(start_ts))
    url_elements.append("endTs=" + str(end_ts))

    # Done. Now mash up the whole thing into a '&' separated string
    service_endpoint += "&".join(url_elements)

    # I'm finally ready to query the remote endpoint. This service requires a REGULAR type authorization token
    service_dict = utils.build_service_calling_info(utils.get_auth_token(admin=False), service_endpoint)

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
        # So, I got a valid response with a bunch or little dictionaries in a list, which is itself another dictionary with the timeseriesKey as its key. Extract the list first of all
        data_list = eval(response.text)[str(result[2])]

        if len(data_list) == limit:
            # Give an heads up to the user that the number of results that came back were not limited by the time window defined but by the 'limit' argument instead. Continue after that
            timeseries_log.warning("The number of results returned from the remote API was limited by the 'limit' parameter: got {0} valid results back".format(str(limit)))

        # Nothing more to do but to return the result list
        return data_list