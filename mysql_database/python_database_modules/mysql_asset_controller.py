""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group asset-controller"""

import user_config
import proj_config
import utils
import ambi_logger
import datetime
from ThingsBoard_REST_API import tb_asset_controller
from mysql_database.python_database_modules import database_table_updater
from mysql_database.python_database_modules import mysql_utils


def get_asset_env_data(base_date, time_interval, variable_list, asset_name=None, asset_id=None, filter_nones=True):
    """
    Use this method to retrieve the environmental data between two dates specified by the pair base_date and time_interval, for each of the variables indicated in the variables list and for an asset identified by at least one of the elements in
    the pair asset_name/asset_id.
    :param base_date: (datetime.datetime) The date for which to start the retrieval window, i.e., this one is the newest end of the time window.
    :param time_interval: (datetime.timedelta) A timedelta object that is going to be subtracted to the base_date provided in order to establish a valid operational window.
    :param variable_list: (list of str) A list with the variable names (ontology names) that are to be retrieved from the respective database table. Each one of the elements in the list provided is going to be validated against the 'official'
    list
    in proj_config.ontology_names.
    :param asset_name: (str) The name of the asset entity from where the data is to be retrieved from. This method expects either this parameter or the respective id to be provided and does not execute unless at least one of them is present.
    :param asset_id: (str) The id string associated to an asset element in the database, i.e., the 32 byte hexadecimal string in the usual 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' format. This method expects either this element or the asset name to
    be provided before continuing. If none are present, the respective Exception is raised.
    :param filter_nones: (bool) Set this flag to True to exclude any None values from the final result dictionary. Otherwise the method returns all values, including NULL/None ones.
    :raise utils.InputValidationException: If any of the inputs fails the initial data type validation or if none of the asset identifiers (name or id) are provided.
    :raise mysql_utils.MySQLDatabaseException: If any errors occur during the database accesses.
    :return response (dict): This method returns a response dictionary in a format that is expected to be serialized and returned as a REST API response further on. For this method, the response dictionary has the following format:
        response =
            {
                env_variable_1: [
                    {
                        timestamp_1: <str>,
                        value_1: <str>
                    },
                    {
                        timestamp_2: <str>.
                        value_2: <str>
                    },
                    ...,
                    {
                        timestamp_N: <str>,
                        value_N: <str>
                    }
                ],
                env_variable_2: [
                    {
                        timestamp_1: <str>,
                        value_1: <str>
                    },
                    {
                        timestamp_2: <str>.
                        value_2: <str>
                    },
                    ...,
                    {
                        timestamp_N: <str>,
                        value_N: <str>
                    }
                ],
                ...
                env_variable_N: [
                    {
                        timestamp_1: <str>,
                        value_1: <str>
                    },
                    {
                        timestamp_2: <str>.
                        value_2: <str>
                    },
                    ...,
                    {
                        timestamp_N: <str>,
                        value_N: <str>
                    }
                ]
            }
    """
    log = ambi_logger.get_logger(__name__)

    # Validate inputs

    # Check if at least one element from the pair asset_name/asset_id was provided
    if not asset_name and not asset_id:
        error_msg = "Missing both asset name and asset id from the input parameters. Cannot continue until at least one of these is provided."
        log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    if asset_name:
        utils.validate_input_type(asset_name, str)

    if asset_id:
        utils.validate_id(entity_id=asset_id)

    utils.validate_input_type(base_date, datetime.datetime)
    utils.validate_input_type(time_interval, datetime.timedelta)

    if base_date > datetime.datetime.now():
        error_msg = "The base date provided: {0} is invalid! Please provide a past date to continue...".format(str(base_date))
        log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    if base_date - time_interval >= datetime.datetime.now():
        error_msg = "The time interval provided: {0} is invalid! Please provide a positive value for this parameter to continue...".format(str(time_interval))
        log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    utils.validate_input_type(variable_list, list)
    for i in range(0, len(variable_list)):
        # Check inf the element is indeed a str as expected
        utils.validate_input_type(variable_list[i], str)
        # Take the change to normalize it to all lowercase characters
        variable_list[i] = variable_list[i].lower()

        # And check if it is indeed a valid element
        if variable_list[i] not in proj_config.ontology_names:
            log.warning("Attention: the environmental variable name provided: {0} is not among the ones supported:\n{1}\nRemoving it from the variable list...".format(
                str(variable_list[i]),
                str(proj_config.ontology_names)
            ))
            variable_list.remove(variable_list[i])

    # Check if the last operation didn't emptied the whole environmental variable list
    if len(variable_list) == 0:
        error_msg = "The variable list is empty! Cannot continue until at least one valid environmental variable is provided"
        log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # The asset_id is one of the most important parameters in this case. Use the provided arguments to either obtain it or make sure the one provided is a valid one. If both parameters were provided (asset_id and asset_name)
    if asset_id:
        # If an asset id was provided, use it to obtain the associated name
        asset_name_db = retrieve_asset_name(asset_id=asset_id)

        # Check if any names were obtained above and, if so, check if it matches any asset name also provided
        if asset_name:
            if asset_name != asset_name_db:
                log.warning("The asset name obtained from {0}.{1}: {2} does not matches the one provided: {3}. Defaulting to {2}...".format(
                    str(user_config.access_info['mysql_database']['database']),
                    str(proj_config.mysql_db_tables['tenant_assets']),
                    str(asset_name_db),
                    str(asset_name)
                ))
                asset_name = asset_name_db

    if not asset_id and asset_name:
        # Another case: only the asset name was provided but no associated id. Use the respective method to retrieve the asset id from the name
        asset_id = retrieve_asset_id(asset_name=asset_name)

        # Check if a valid id was indeed returned (not None)
        if not asset_id:
            error_msg = "Invalid asset id returned from {0}.{1} using asset_name = {2}. Cannot continue...".format(
                str(user_config.access_info['mysql_database']['database']),
                str(proj_config.mysql_db_tables['tenant_assets']),
                str(asset_name)
            )
            log.error(msg=error_msg)
            raise utils.InputValidationException(message=error_msg)

    utils.validate_input_type(filter_nones, bool)

    # Initial input validation cleared. Before moving any further, implement the database access objects and use them to retrieve a unique, single name/id pair for the asset in question
    database_name = user_config.access_info['mysql_database']['database']
    asset_device_table_name = proj_config.mysql_db_tables['asset_devices']
    device_data_table_name = proj_config.mysql_db_tables['device_data']

    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)

    # All ready for data retrieval. First, retrieve the device_id for every device associated to the given asset
    sql_select = """SELECT toId, toName FROM """ + str(asset_device_table_name) + """ WHERE fromEntityType = %s AND fromId = %s AND toEntityType = %s;"""

    select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=('ASSET', asset_id, 'DEVICE'))

    # Analyse the execution results
    if select_cursor.rowcount is 0:
        error_msg = "Asset (asset_name = {0}, asset_id = {1}) has no devices associated to it! Cannot continue...".format(str(asset_name), str(asset_id))
        log.error(msg=error_msg)
        select_cursor.close()
        cnx.close()
        raise mysql_utils.MySQLDatabaseException(message=error_msg)
    else:
        log.info("Asset (asset_name = {0}, asset_id = {1}) has {2} devices associated.".format(str(asset_name), str(asset_id), str(select_cursor.rowcount)))

    # Extract the devices id's to a list for easier iteration later on
    record = select_cursor.fetchone()
    device_id_list = []

    while record:
        device_id_list.append(record[0])

        # Grab another one
        record = select_cursor.fetchone()

    # Prepare a mash up of all device_id retrieved so far separated by OR statements to replace the last element in the SQL SELECT statement to execute later on
    device_id_string = []

    for _ in device_id_list:
        device_id_string.append("deviceId = %s")

    # And now connect them all into a single string stitched together with 'OR's
    device_where_str = """ OR """.join(device_id_string)

    # Store the full results in this dictionary
    result_dict = {}

    # Prepare the SQL SELECT to retrieve data from
    for i in range(0, len(variable_list)):
        # And the partial results in this one
        sql_select = """SELECT timestamp, value FROM """ + str(device_data_table_name) + """ WHERE ontologyId = %s AND (""" + str(device_where_str) + """) AND (timestamp >= %s AND timestamp <= %s);"""

        # Prepare the data tuple by joining together the current ontologyId with all the deviceIds retrieved from before
        data_tuple = tuple([variable_list[i]] + device_id_list + [base_date - time_interval] + [base_date])

        select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=data_tuple)

        # Analyse the execution outcome
        if select_cursor.rowcount > 0:
            # Results came back for this particular ontologyId. For this method, the information of the device that made the measurement is irrelevant. Create a dictionary entry for the ontologyId parameter and populate the list of dictionaries
            # with the data retrieved
            result_dict[variable_list[i]] = []

            # Process the database records
            record = select_cursor.fetchone()

            while record:
                # Check if the filtering flag is set
                if filter_nones:
                    # And if so, check if the current record has a None as its value
                    if record[1] is None:
                        # If so, grab the next record and skip the rest of this cycle
                        record = select_cursor.fetchone()
                        continue

                result_dict[variable_list[i]].append(
                    {
                        "timestamp": str(int(record[0].timestamp())),
                        "value": str(record[1])
                    }
                )

                # Grab the next record in line
                record = select_cursor.fetchone()

    # All done it seems. Close down the database access elements and return the results so far
    select_cursor.close()
    cnx.close()
    return result_dict


def retrieve_asset_id(asset_name):
    """
    This method receives the name of an asset and infers the associated id from it by consulting the respective database table.
    :param asset_name: (str) The name of the asset to retrieve from ambiosensing_thingsboard.tb_tenant_assets. This method can only implement the limited searching capabilities provided by the MySQL database. If these are not enough to retrieve an
    unique record associated to the asset name provided, the method 'fails' (even though there might be a matching record in the database but with some different uppercase/lowercase combination than the one provided) and returns 'None' in that case.
    :raise utils.InputValidationException: If the input argument fails the data type validation.
    :raise mysql_utils.MySQLDatabaseException: If any errors occur when accessing the database.
    :return asset_id: (str) If a unique match was found to the provided asset_name. None otherwise.
    """
    log = ambi_logger.get_logger(__name__)

    # Validate the input
    utils.validate_input_type(asset_name, str)

    # Prepare the database access elements
    database_name = user_config.access_info['mysql_database']['database']
    table_name = proj_config.mysql_db_tables['tenant_assets']

    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)

    sql_select = """SELECT entityType, id FROM """ + str(table_name) + """ WHERE name = %s;"""

    select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=(asset_name,))

    # Analyse the execution
    if select_cursor.rowcount is 0:
        log.warning("No records returned from {0}.{1} using asset_name = {2}".format(str(database_name), str(table_name), str(asset_name)))
        select_cursor.close()
        cnx.close()
        return None
    elif select_cursor.rowcount > 1:
        log.warning("{0}.{1} returned {2} records for asset_name = {3}. Cannot continue...".format(
            str(database_name),
            str(table_name),
            str(select_cursor.rowcount),
            str(asset_name)
        ))
        select_cursor.close()
        cnx.close()
        return None
    else:
        # Got a single result back. Check if the entityType matches the expected one
        record = select_cursor.fetchone()
        if record[0] != 'ASSET':
            error_msg = "The record returned from {0}.{1} using asset_name = {2} has a wrong entityType. Got a {3}, expected an 'ASSET'".format(
                str(database_name),
                str(table_name),
                str(asset_name),
                str(record[0])
            )
            log.error(msg=error_msg)
            select_cursor.close()
            cnx.close()
            return None
        else:
            # All is well. Return the retrieved id after validation
            asset_id = record[1]
            utils.validate_id(entity_id=asset_id)

            # If the parameter returned survived the last battery of validations, all seems OK. Return the result
            select_cursor.close()
            cnx.close()
            return asset_id


def retrieve_asset_name(asset_id):
    """
    This method mirrors the last one in the sense that it receives an asset_id and returns the associated name, if any.
    :param asset_id: (str) A 32-byte hexadecimal string in the expected xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx format. This element is configured in the database as the primary key, which means that this method should never receive multiple records.
    :raise utils.InputValidationException: If the the input argument fails the initial data type validation
    :raise mysql_utils.MySQLDatabaseException: If any errors occur when consulting the database.
    :return asset_name: (str) If an unique match was found, None otherwise
    """
    log = ambi_logger.get_logger(__name__)

    # Validate the input
    utils.validate_id(entity_id=asset_id)

    # Prepare the database access elements
    database_name = user_config.access_info['mysql_database']['database']
    table_name = proj_config.mysql_db_tables['tenant_assets']

    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)

    sql_select = """SELECT entityType, name FROM """ + str(table_name) + """ WHERE id = %s;"""
    select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=(asset_id,))

    # Analyse the execution
    if select_cursor.rowcount is 0:
        log.warning("No records returned from {0}.{1} using asset_id = {2}".format(str(database_name), str(table_name), str(asset_id)))
        select_cursor.close()
        cnx.close()
        return None
    elif select_cursor.rowcount > 1:
        log.warning("{0}.{1} returned {2} records using asset_id = {3}. Cannot continue...".format(
            str(database_name),
            str(table_name),
            str(select_cursor.rowcount),
            str(asset_id)
        ))
        select_cursor.close()
        cnx.close()
        return None
    else:
        # A single return came back. Process it then
        record = select_cursor.fetchone()
        if record[0] != 'ASSET':
            error_msg = "The record returned from {0}.{1} using asset id = {2} has a wrong entityType. Got a {3}, expected an 'ASSET'".format(
                str(database_name),
                str(table_name),
                str(select_cursor.rowcount),
                str(record[0])
            )
            log.error(msg=error_msg)
            select_cursor.close()
            cnx.close()
            return None
        else:
            # All is good so far. Check if the name returned is indeed a str and return it if so
            asset_name = record[1]
            utils.validate_input_type(asset_name, str)
            select_cursor.close()
            cnx.close()
            return asset_name


def update_tenant_assets_table():
    """
    Method to populate the database table with all the ASSETS belonging to a given tenant. I'm still trying to figure out the actual logic behind this call since the API service that I call to retrieve the desired information uses a
    'customer_user' type credential pair but the results returned are related to the Tenant that is associated to Customer identified by those credentials (why not use the 'tenant_admin' credentials instead? Makes more sense in my honest opinion.
    In fact, using those credentials yields a HTTP 403 - access denied - response from the remote server... go figure...) so the relation with a Tenant is tenuous, at best. Anyhow, what matters is that all configured assets in the ThingsBoard
    platform seem to be returned at once by the tb side method, so now its just a matter of putting them into a proper database table
    :raise mysql_utils.MySQLDatabaseException: For errors with the database operation
    :raise utils.ServiceEndpointException: For errors with the remote API service execution
    :raise utils.AuthenticationException: For errors related with the authentication credentials used.
    """

    # Key to return the actual database name from proj_config.mysql_db_tables dictionary
    module_table_key = 'tenant_assets'
    # A generous limit number to retrieve all results in the remote API side
    limit = 50

    # Grab the response from the remote API then
    response = tb_asset_controller.getTenantAssets(limit=limit)

    # Translate the response got and convert it to the expected dictionary
    response_dict = eval(utils.translate_postgres_to_python(response.text))

    # And retrieve the core of the stuff I'm interested into
    asset_list = response_dict['data']

    # Process the returned assets one by one
    for asset in asset_list:
        # Suppress the 'tenantId' sub-dictionary by replacing it by its 'id' parameter with a new key that matches a column name now. A tenantId already implies a TENANT entityType, so the later is redundant and can go out
        asset['tenantId'] = asset['tenantId']['id']

        # The same goes for the CustomerId
        asset['customerId'] = asset['customerId']['id']

        # As always, expand the asset dictionary into a one level dictionary
        asset = utils.extract_all_key_value_pairs_from_dictionary(input_dictionary=asset)

        # And replace any retarded POSIX timestamps for nice DATETIME compliant objects
        try:
            asset['createdTime'] = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=asset['createdTime'])
        except KeyError:
            pass

        # All set. Invoke the database updater then
        database_table_updater.add_table_data(asset, proj_config.mysql_db_tables[module_table_key])
