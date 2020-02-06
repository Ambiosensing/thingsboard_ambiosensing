""" Place holder for general-purposed methods and classes that interact with Ambiosensing internal MySQL database """

import utils
import ambi_logger
import user_config
import psycopg2
import psycopg2.extensions
import datetime


# ---------------------------------------------- DATABASE RELATED CUSTOM EXCEPTION ----------------------------------------------------------------------------------------------------------------------------------------------------
class PostgresDatabaseException(Exception):
    # The main message delivered with the original Exception
    message = None
    # An associated error code, if any
    error_code = None
    # A Diagnostics object, a feature returned from the Postgres-Python connector (psycopg2) that can be used to get further information about the error
    diag = None

    def __init__(self, message=None, error_code=None, diag=None):
        """The standard Exception constructor. This exception is tailored after the typical elements that are returned in a SQL related error. Also, due to the intense logging actions undertaken so far in this project,
        its a good idea to use Exceptions that easily expose their error messages (something that is not trivial with BaseException or your run-of-the-mill Exception) so that they can be captured and logged by the logger object
        @:param message (str) - A short description of the reason behind the raising of this Exception
        @:param error_code (int) - The error_code associated with this exception, if any
        @:param diag (Diagnostics) - A Diagnostics type object that can be used to retrieve further information about the error being raised
        @:raise utils.InputValidationException - If this Exception is formed using illegal argument types"""

        self.message = message
        self.error_code = error_code
        self.diag = diag


# ---------------------------------------------- GENERAL PURPOSE METHODS ----------------------------------------------------------------------------------------------------------------------------------------------------
def connect_db(database_name):
    """Basic method that return a connection object upon a successful connection attempt to a database whose connection data is present in the configuration file, as a dictionary with the database name as its key
    NOTE: This method assumes a single server instance for the installation of all database data (a single triplet hostname, username and password). For databases that spawn over multiple servers or to support more than one user in this
    regard, please change this method accordingly
    @:param database_name (str) - The name of the database to connect to.
    @:raise util.InputValidationException - If the input arguments provided are invalid
    @:raise Exception - For any other occurring errors
    @:return cnx (mysql.connector.connection.MySQLConnection) - An active connection to the database"""
    connect_log = ambi_logger.get_logger(__name__)

    try:
        utils.validate_input_type(database_name, str)
        connection_dict = user_config.access_info['postgres_database']
    except utils.InputValidationException as ive:
        connect_log.error(ive.message)
        raise ive
    except KeyError as ke:
        error_msg = "Missing '{0}' key from the user_config.postgres_db_access dictionary!".format(str(database_name))
        connect_log.error(error_msg)
        raise ke

    try:
        cnx = psycopg2.connect(user=connection_dict['username'],
                               password=connection_dict['password'],
                               database=connection_dict['database'],
                               host=connection_dict['host'],
                               port=connection_dict['port'])
    except psycopg2.Error as err:
        connect_log.error("Got a code {0} error with message: {1} when connecting to {2}:{3}.{4}".format(
            str(err.pgcode),
            str(err.pgerror),
            str(connection_dict['host']),
            str(connection_dict['port']),
            str(connection_dict['database'])))
        # Catch any errors under a generic 'Error' exception and pass it upwards under a more specific MySQLDatabaseException
        raise PostgresDatabaseException(message=err.pgerror, error_code=err.pgcode, diag=err.diag)

    return cnx


def get_table_columns(database_name, table_name):
    """This method does a simple SELECT query to the database for just the columns names in a given table. This is particular useful for building INSERT and UPDATE statements that require a specification of these elements on the
    statements
    @:param database (str) - The name of the database to connect to
    @:param table_name (str) - The name of the table from the database to connect to
    @:raise utils.InputValidationException - If any of the inputs is not valid
    @:raise PostgresDatabaseException - for database related exceptions
    @:return column_list (list of str) - A list with all the names of the columns, in order, extracted from the database.table_name
    """
    get_table_log = ambi_logger.get_logger(__name__)

    try:
        utils.validate_input_type(database_name, str)
        utils.validate_input_type(table_name, str)

        cnx = connect_db(database_name=database_name)
        select_cursor = cnx.cursor()

        sql_select = """SELECT column_name FROM information_schema.columns WHERE table_name = %s;"""
        data_tuple = (table_name,)

        select_cursor = run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=data_tuple)

        if not select_cursor.rowcount:
            error_msg = "Did not retrieve any column information from {0}.{1}. Cannot continue!".format(str(database_name), str(table_name))
            get_table_log.error(error_msg)
            raise PostgresDatabaseException(message=error_msg)

        # The last statement, if well executed, returns a list of one element tuples (because the SELECT statement only specified one field in this case). To transform this into a proper list I have to go through all elements of the list as get
        # them out of the tuple, basically...
        # Grab the full list first
        result_list = select_cursor.fetchall()

        return_list = []
        # And do the deed then
        for result in result_list:
            return_list.append(result[0])

        # Done. Send it back then
        return return_list

    except psycopg2.Error as err:
        get_table_log.error("Got a code {0} error with message: {1} when connecting to {2}.{3}".format(
            str(err.pgcode),
            str(err.pgerror),
            str(database_name),
            str(table_name)))
        raise PostgresDatabaseException(message=err.pgerror, error_code=err.pgcode, diag=err.diag)


def create_update_sql_statement(column_list, table_name, trigger_column):
    """This method automatized the build if standard SQL UPDATE statements. NOTE: This method produces the simplest of SQL UPDATE statements, that is, "UPDATE table_name SET (column_name = %s) WHERE (trigger_column = %s);",
    in which the %s elements are to be replaced by providing the adequate tuple of update values in the statement execution. This means that only one record can be updated given that the trigger condition is an equality. This method is
    not suitable for more complex SQL UPDATE statements
    @:param column_list (list of str) - a list with the names of the Postgres database columns whose information is to be added to
    @:param table_name (str) - The name of the table where the Update statement is going to take effect
    @:param trigger_column (str) - The column that is going to be used to identify the record to be updated (i.e., the WHERE column_name condition part of the statement)
    @:return sql_update (str) - The statement string to be executed with '%s' elements instead of the actual values in the statement (considered a more secure approach to run these statements from external applications such as this one).
    The actual values are to be replaced shortly before the execution of the statement, already in the database side of things
    @:raise utils.InputValidation Exception - if error occur during the validation of inputs
    @:raise Exception - for any other error types
    """

    # The following method validates all inputs at once
    validate_sql_input_lists(column_list, table_name, trigger_column)

    # If I'm still here (no Exceptions raised during the last command)
    sql_update = """UPDATE """ + str(table_name) + """ SET """
    for i in range(0, len(column_list)):
        sql_update += str(column_list[i]) + """ = %s, """

    # The last for loop add an extra ', ' at the end of the list as a consequence of it running all the way up to the last element on the list. So I need to drop these two extra characters before continuing the statement build
    sql_update = sql_update[0:-2] + """ WHERE """ + str(trigger_column) + " = %s;"

    # Statement completed. Send it back to the user.
    return sql_update


def create_insert_sql_statement(column_list, table_name):
    """Method to automatize the building of simple SQL INSERT statements: INSERT INTO table_name (expanded, comma separated, column list names) VALUES (as many '%s' as column_list elements);
    @:param column_list (list of str) - A list with the names of the MySQL database columns
    @:param  table_name (str) - The name of the table where the INSERT statement is going to take effect
    @:return sql_insert (str) - The state,ent string to be executed with '%s' instead of actual values. These need to be replaced when executed in the database side (the python mysql connector deals with it quite nicely)
    @:raise utils.InputValidationException - If any errors occur during the input validation"""

    # Validate all inputs at once
    validate_sql_input_lists(column_list, table_name)

    values_to_replace = []
    for i in range(0, len(column_list)):
        values_to_replace.append('%s')

    sql_insert = """INSERT INTO """ + str(table_name) + """ ("""
    sql_insert += """,""".join(column_list)
    sql_insert += """) VALUES ("""
    sql_insert += """, """.join(values_to_replace)
    sql_insert += """);"""

    # Done. Send it back for execution
    return sql_insert


def create_delete_sql_statement(database_name, trigger_column, table_name):
    """Method to automatize the building of SQL DELETE statements. These are generally simpler than UPDATE or INSERT ones
    @:database_name (str) - The name of the database in which this statement is going to be used. Needed for the validation of inputs
    @:param trigger_column (str) - The name of the column that is going to be used in the DELETE statement (The WHERE trigger_column condition part goes). As with the UPDATE method, the DELETE statements produced through here are quite
    simple, i.e., the triggering condition is an equality and hence only one record at a time can be deleted via this method
    @:param table_name (str) - The name of the table where the DELETE statement is going to take effect
    @:return sql_delete (str) - The statement string to be executed with '%s' instead of values. These need to replaced afterwards in the parent function
    @:raise utils.InputValidationException - If the input arguments are invalid"""

    utils.validate_input_type(database_name, str)
    utils.validate_input_type(table_name, str)

    # Though this method doesn't require a full column list (the DELETE statement doesn't requires it), its going to be useful to get it anyway at this point so that I can use my validate_sql_input_lists() method to validate the whole
    # set of arguments in one sitting
    column_list = get_table_columns(database_name, table_name)

    # Got the full column list. I can now run the sql validation method
    validate_sql_input_lists(column_list, table_name, trigger_column)

    # So far so good. Carry on with the statement build
    sql_delete = """DELETE FROM """ + str(table_name) + """ WHERE """ + str(trigger_column) + """ = %s;"""

    return sql_delete


def validate_sql_input_lists(column_list, table_name, trigger_column=False):
    """Since I need to repeat a series of validation steps for several SQL statement building methods that I'm writing, I might as well abstract the whole thing in a method to save precious hours of typing the same thing over and over
    again.
    @:param column_list (list of str) - a list with the names of the MySQL database columns whose information is to be added to
    @:param table_name (str) - The name of the table where the SQL statement is going to be executed
    @:param trigger_column (str) - An optional parameter given than only the UPDATE and DELETE statements use it (the WHERE trigger_column condition part of the statement goes in)
    @:return True (bool) - if the data is able to pass all validations
    @:raise utils.InputValidationException - If the input arguments are invalid
    @:raise Exception - For any other error types"""
    validate_sql_log = ambi_logger.get_logger(__name__)

    try:
        utils.validate_input_type(column_list, list)
        utils.validate_input_type(table_name, str)
        if trigger_column:
            utils.validate_input_type(trigger_column, str)
        for column in column_list:
            utils.validate_input_type(column, str)
    except utils.InputValidationException as ive:
        validate_sql_log.error(ive.message)
        raise ive

    if len(column_list) <= 0:
        error_msg = "The column list is empty!"
        validate_sql_log.error(error_msg)
        raise PostgresDatabaseException(message=error_msg)

    # If a trigger_column was provided, check if it is among the full list elements
    if trigger_column and trigger_column not in column_list:
        error_msg = "The trigger column provided ({0}) was not found in table {1}".format(str(trigger_column), str(table_name))
        validate_sql_log.error(error_msg)
        raise PostgresDatabaseException(message=error_msg)

    # Finally, use the get_table_column methods to return the list of columns for that table in question from the default database as check if all elements in the column list provided are indeed in the list returned from the database
    database_name = user_config.postgres_db_access['database']
    full_column_list = get_table_columns(database_name=database_name, table_name=table_name)

    for column in column_list:
        if column not in full_column_list:
            error_msg = "The column '{0}' provided in the argument list is not among the columns for {1}.{2}. Cannot continue!".format(str(column), str(database_name), str(table_name))
            validate_sql_log.error(error_msg)
            raise PostgresDatabaseException(message=error_msg)
    # All is good with my data. Send back an OK
    return True


def convert_timestamp_tb_to_datetime(timestamp):
    """This method converts a specific timestamp from a ThingsBoard remote API request (which has one of the weirdest formats that I've seen around) and returns a datetime object that can be interpreted by the DATETIME data format,
    which way more human readable that the POSIX timestamp that is being used in the ThingsBoard Postgres database.
    databases, i.e., YYYY-MM-DD hh:mm:ss, which also corresponds to the native datetime.datetime format from python
    @:param timestamp (int) - This is one of the trickiest elements that I've found so far. The ThingsBoard internal data is stored in a Postgres database. I'm assuming that is the one behind the data format returned by the remote API. Whatever
    it may be, it returns a 13 digit integer as the timestamp. A quick analysis suggests that this is a regular POSIX timestamp, i.e., the number of seconds from 1970-01-01 00:00:00 until whenever that data was inserted in the database.
    There are literally loads of different and straightforward ways to convert this value into a human-readable datetime. Yet none of them seemed to work with this particular value. In fact, none of the timestamps returned from the remote
    API was able to be converted into a datetime. And the reason is stupid as hell! It seems that, if you bother to count all seconds from 1970 until today, you get a number with 10 digits... and you have been getting that for quite some
    time given how long has to pass to add a new digit to this value. A bit more of investigation showed that, as well with regular datetime elements, POSIX timestamps also indicate the number of microseconds elapsed, but normally that is
    expressed as a 17 digit float in which the last 5 are the decimal part, i.e., the microseconds, but there's an obvious decimal point w«in those cases where the POSIX timestamp also has the number of microseconds. The only reasonable
    explanation (though somewhat weird in its own way) is that the value returned by the remote API contains 3 decimal digits and, for whatever reason behind it, the decimal point is omitted. It turns out that this is exactly what is going
    on! So I need to do extra flexing with this one... The method expects the 13 digit integer that comes straight from the remote API call and then itself does whatever needs to return a meaningful datetime
    @:return data_datetime (datetime.datetime) - A regular datetime object that can be sent directly to a MySQL database expecting a DATETIME field (YYYY-MM-DD hh:mm:ss)
    @:raise utils.InputValidationException - If there is something wrong with the validation of inputs
    """
    times2date_log = ambi_logger.get_logger(__name__)

    utils.validate_input_type(timestamp, int)

    # Given how weird are the datetime values returned by the ThingsBoard API, I'm going to extra anal with this one
    if len(str(timestamp)) != 13:
        error_msg = "Please provide the full value for the timestamp returned by the remote API (expecting a 13 digit int, got {0} digits.)".format(str(len(str(timestamp))))
        times2date_log.error(error_msg)
        raise Exception(error_msg)

    # All appears to be in good order so far. From here I could simply divide the timestamp value by 1000 to get it to 10 integer digits (+3 decimal) but I'm not particularly concerned about microseconds, really. So, might as well drop the
    # last 3 digits of the timestamp and call it a day (forcing a int cast after dividing the timestamp by 1000 effectively truncates the integer part of it, thus achieving the desired outcome)
    timestamp = int(timestamp/1000)

    # The rest is trivial
    return datetime.datetime.fromtimestamp(timestamp)


def convert_datetime_to_timestamp_tb(data_datetime):
    """This method is the literal inverse of the previous one: it receives a regular datetime object in the format YYYY-MM-DD hh:mm:ss.xxxx (I'm allowing microseconds in this one, if needed be) and returns the 13 digit timestamp that
    ThingsBoard's Postgres database expects
    @:param data_datetime (datetime.datetime) - A YYYY-MM-DD hh:mm:ss.xxxx representation of a date and a time, consistent with the datetime.datetime class
    @:return timestamp (int) - a 13 digit integer that its actually a 10 digit integer + 3 decimal digits with the decimal period omitted.
    @:raise utils.InputValidationException - For errors with the method's input arguments
    @:raise Exception - For all other errors
    """

    utils.validate_input_type(data_datetime, datetime.datetime)

    # The conversion between datetime.datetime to timestamp is direct but this operation yields a number between 15 and 16 digits, depending on the time of the date that originated it. In any case, the integer part is always fixed (at
    # least for the next couple of decades or so) and it has 10 digits only. So the easiest approach is to multiply the resulting timestamp by 1000 and then re-cast it to integer to drop the remaining digits that I'm not interested,
    # regardless of exactly how many they were in the beginning
    return int(data_datetime.timestamp()*1000)


def run_sql_statement(cursor, sql_statement, data_tuple=()):
    """The way python runs SQL statements is a bit convoluted, with plenty of moving parts and things that can go wrong. Since I'm going to run plenty of these along this project, it is a good idea to abstract this operation as much as
    possible
    @:param cursor (psycopg2.extensions.cursor) - A cursor object, obtained from an active database connection, that its used by python to run SQL statements as well as to process the results.
    @:param sql_statement (str) - THe SQL statement string to be executed, with its values not explicit but replaced by '%s' characters instead. This method takes care of this replacements.
    @:param data_tuple (tuple) - A tuple with as many elements as the ones to be replaced in the SQL string. The command that effectively runs the SQL statement takes two arguments: the original SQL string statement with '%s' elements
    instead of its values and a data tuple where those values are indicated in the expected order. The command then sends both elements across to be executed database side in a way that protects their content and integrity (supposedly, it
    wards against SQL injection attacks.
    @:raise utils.InputValidationException - If the input arguments fail their validations
    @:raise PostgresDatabaseException - For errors related to database operations
    @:raise Exception - For any other error that may occur.
    """
    run_sql_log = ambi_logger.get_logger(__name__)

    utils.validate_input_type(sql_statement, str)
    utils.validate_input_type(data_tuple, tuple)
    utils.validate_input_type(cursor, psycopg2.extensions.cursor)

    # Count the number of '%s' in the sql statement string and see if they match with the number of elements in the tuple
    if len(data_tuple) != sql_statement.count('%s'):
        error_msg = "Mismatch between the number of data tuple elements ({0}) and the number of replaceable '%s' in the sql statement string ({1})!".format(str(len(data_tuple)), str(sql_statement.count('%s')))
        run_sql_log.error(error_msg)
        raise PostgresDatabaseException(message=error_msg)

    # Done with the validations.
    try:
        cursor.execute(sql_statement, data_tuple)
    except psycopg2.Error as err:
        run_sql_log.error(err.pgerror)
        raise PostgresDatabaseException(message=err.pgerror, error_code=err.pgcode, diag=err.diag)

    return cursor


def validate_database_table_name(table_name):
    """This simple method receives a name of a table and validates it by executing a SQL statement in the default database to retrieve all of its tables and then checks if the table name in the input does match any of the returned values.
    @:param table_name (str) - The name of the database table whose existence is to be verified
    @:raise utils.InputValidationException - If the inputs fail initial validation
    @:raise PostgresDatabaseException - If any error occur while executing database bounded operations or if the table name was not found among the list of database tables retrieved
    @:return True (bool) - If table_name is among the database tables list"""

    validate_db_table_log = ambi_logger.get_logger(__name__)

    # Validate the input
    utils.validate_input_type(table_name, str)

    # Get the default database name
    database_name = user_config.mysql_db_access['database']
    # Create the database interface elements
    cnx = connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)

    # Prepare the SQL statement
    sql_select = """SELECT tables.table_name FROM information_schema.TABLES;"""

    # And execute it
    select_cursor = run_sql_statement(select_cursor, sql_select, ())

    # Check the data integrity first
    if not select_cursor.rowcount:
        error_msg = "The SQL statement '{0}' didn't return any results! Exiting...".format(str(select_cursor.query))
        validate_db_table_log.error(error_msg)
        select_cursor.close()
        cnx.close()
        raise PostgresDatabaseException(message=error_msg)
    # If results were gotten
    else:
        # Grab the first one
        result = select_cursor.fetchone()

        # And run the next loop until all results were checked (result would be set to None once all the data retrieved from the database is exhausted)
        while result:
            # If a match is found
            if result[0] == table_name:
                # Return the response immediately
                return True
            # Otherwise
            else:
                # Grab the next one and run another iteration of this
                result = select_cursor.fetchone()

        # If I got here it means none of the results matched the table_name provided. Nothing more to do than to inform that the table name is not valid
        raise PostgresDatabaseException(message="The table provided '{0}' is not among the current database tables!".format(str(table_name)))
