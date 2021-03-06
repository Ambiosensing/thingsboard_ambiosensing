""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group telemetry-controller"""
import proj_config
import user_config
import utils
import datetime
import ambi_logger
from mysql_database.python_database_modules import mysql_utils
from mysql_database.python_database_modules import database_table_updater
from ThingsBoard_REST_API import tb_telemetry_controller


def populate_device_data_table(collection_time_limit=None, device_name_list=None):
    """
    This method aggregates a whole bunch of methods developed so far in order to fill out the main data repository for devices in the MySQL database. This method scans the device table for all devices configured there and, from the information
    retrieved from it, populates this table. Given how complex and populated this table may become, only the data from the current time up to either the provided collection_time_limit or a default 24 hour period, which is also going to be the
    value to use if an invalid parameter is provided in this parameter.
    :param collection_time_limit (datetime.datetime or datetime.timedelta) - A datetime object to be defined as the start date to start retrieving server data (if a datetime.datetime is provided) or subtracted to the current datetime.datetime.now(
    ) (if a datetime.timedelta is provided instead).
    :param device_name_list (list of str) - Use this argument to provide a list with the names of the devices whose data is to be updated. If no list is provided through this argument, the method updated all devices currently configured in the
    tb_devices table.
    :raise utils.InputValidationException - If the input fails initial validation.
    :raise mysql_utils.MySQLDatabaseException - If problems occur when accessing the database.
    :raise utils.ServiceEndpointException - If the remote server cannot be accessed/returns access errors
    :return:
    """
    log = ambi_logger.get_logger(__name__)

    # Validate inputs
    if collection_time_limit:
        try:
            utils.validate_input_type(collection_time_limit, datetime.datetime, datetime.timedelta)
        except utils.InputValidationException:
            log.warning("Invalid collection time limit provided: {0}. Defaulting to {1}".format(str(collection_time_limit), str(proj_config.default_collection_time_limit)))
            collection_time_limit = proj_config.default_collection_time_limit
    else:
        log.warning("No collection time limit provided. Defaulting to {0}".format(str(proj_config.default_collection_time_limit)))
        collection_time_limit = proj_config.default_collection_time_limit

    if device_name_list:
        utils.validate_input_type(device_name_list, list)
        for device_name in device_name_list:
            utils.validate_input_type(device_name, str)

    # Finally, check if an empty list was provided and replace the variable by a None if so. Otherwise it may break this method later on
    if len(device_name_list) == 0:
        device_name_list = None

    # Validation done. Start by creating the usual database access objects
    database_name = user_config.access_info['mysql_database']['database']
    device_table_name = proj_config.mysql_db_tables['devices']
    data_table_name = proj_config.mysql_db_tables['device_data']
    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)

    # Grab the full list of column names for the device list
    device_columns = mysql_utils.get_table_columns(database_name=database_name, table_name=device_table_name)

    if device_name_list:
        # If a device list was provided, build the next SQL select accordingly
        # Start with the base statement
        sql_select = """SELECT * FROM """ + str(device_table_name) + """ WHERE """

        # And now concatenate all the names of devices provided separated by 'OR' in this case. The loop only goes to one short of the end of the list because the last element cannot have an 'OR' after it or the SQL statement is invalid
        for i in range(0, len(device_name_list) - 1):
            sql_select += """name = %s OR """

        # And add one last element without the 'OR' at the end and closing semi colon
        sql_select += """name = %s;"""

        # Create the data_tuple too
        data_tuple = tuple(device_name_list)
    else:
        # Use a broader SELECT then
        # Start by getting all device data from the relevant tenant (all requests within this module are attached to the set of credentials used to interact with the remote server and API)
        sql_select = """SELECT * FROM """ + str(device_table_name) + """;"""

        # The data tuple in this case is empty, but necessary nonetheless
        data_tuple = ()

    # Execute the statement and check if any results came back
    select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=data_tuple)

    # Cannot do anything if no device data comes back, there's nothing more to do in this case...
    if select_cursor.rowcount is 0:
        error_msg = "{0}.{1} wasn't populated with device data yet. Cannot continue...".format(str(database_name), str(device_table_name))
        log.error(error_msg)
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    # Define the time window before going into the main while loop
    end_date = datetime.datetime.now().replace(microsecond=0)
    # end_date = datetime.datetime(year=2020, month=7, day=10, hour=0, minute=0, second=0)
    if type(collection_time_limit) == datetime.datetime:
        start_date = collection_time_limit
    else:
        start_date = end_date - collection_time_limit

    # Use the data from the previous SELECT data to retrieve the next piece of important data - the attribute list - and proceed to populate the table with timeseries data only if both element were obtained
    device_record = select_cursor.fetchone()

    # Establish a limit of records so that it can be possible to retrieve multiple pages of results, if needed
    limit = 1000000

    while device_record:
        # Start by fetching the device's attributes, if any exist
        device_attributes = tb_telemetry_controller.getAttributes(
            entityType=device_record[device_columns.index('entityType')],
            entityId=device_record[device_columns.index('id')]
        )

        # If the last call returned a None, it means no attributes are currently defined for the device in question
        if not device_attributes:
            log.warning("Device '{0}' has no attributes configured yet! Skipping...".format(str(device_record[device_columns.index('name')])))

            # Grab the next record at hand in this case
            device_record = select_cursor.fetchone()

            # Skip the rest of this cycle
            continue

        # The results from the last call provide me with a key element for the next call - the timeseriesKeys that are being used by the device to send data to the ThingsBoard database. Right now, the device timeseriesKeys are the keys of the
        # dictionary returned previously, so grab them to a list. Since the only results returned from the last call are the ones with an ontology term associated to them and I'm only interested in these, might as well use the key list returned as
        # a filter for the timeseries retrieval too
        device_ts = list(device_attributes.keys())

        # Grab the data produced by the device within the time window established
        ts_data_dict = tb_telemetry_controller.getTimeseries(
            device_name=device_record[device_columns.index('name')],
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            timeseries_keys_filter=device_ts
        )

        # Create the database update dictionary template
        device_data_dict = {
            'ontologyId': None,
            'timeseriesKey': None,
            'timestamp': None,
            'value': None,
            'deviceName': device_record[device_columns.index('name')],
            'deviceType': device_record[device_columns.index('type')],
            'deviceId': device_record[device_columns.index('id')],
            'tenantId': device_record[device_columns.index('tenantId')],
            'customerId': device_record[device_columns.index('customerId')]
        }

        # I'm now ready to send data to the device_data table. Prepare the dictionary with the values to write then
        for timeseriesKey in ts_data_dict:
            # At this point I can fulfill the ontologyId and timeseriesKeys for this measurement alone
            device_data_dict['timeseriesKey'] = timeseriesKey
            device_data_dict['ontologyId'] = device_attributes[timeseriesKey]

            # Onwards with the actual data then
            for data_point in ts_data_dict[timeseriesKey]:
                # Fill out the remaining of the database updater dictionary and write it in the database before going for another record
                device_data_dict['timestamp'] = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=data_point['ts'])

                # Before dealing with the associated value, take heed that sometimes there are sensors that, either due to malfunction or other reasons, do not produce a valid value, i.e., one that can be directly cast into a float value. When
                # that happens, the sensor sends back a 'NaN' (Not a Number), which is actually a valid numeric type, so much so that Python is able to cast a 'NaN' string into the rare but valid nan float! Unfortunately the database is not that
                # flexible too and when a 'nan' goes into a DOUBLE field, nothing good comes out... The best approach in this case is to see if the value that comes back is indeed a 'NaN' and immediately set it as a None, since the mysql-python
                # connector has no problems in converting these to NULL types when writing to the MySQL database.
                if data_point['value'] == 'NaN':
                    # If a NaN' came back, replace it immediately by a None
                    device_data_dict['value'] = None
                else:
                    # Cast the value to float since it is always returned as a string
                    device_data_dict['value'] = float(data_point['value'])

                # The updater is complete. Write the data into the database
                database_table_updater.add_table_data(data_dict=device_data_dict, table_name=data_table_name)

        # This is the end of the previous for cycles. Grab another device record and go for another round of the outer while
        device_record = select_cursor.fetchone()
