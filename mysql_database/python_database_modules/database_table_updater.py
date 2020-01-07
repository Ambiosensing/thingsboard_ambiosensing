"""The process of writing data to a database table can be abstracted and generalized in a way that supplying a data dictionary and the table in question should be enough to trigger the logic that either going to add new records,
updated existing ones or do nothing in case the data received is identical to an existing record
"""

import config
import utils
from mysql_database.python_database_modules import mysql_utils
import ambi_logger


def insert_table_data(data_dict, table_name, data_validated=False):
    """This is a method that is going to operate in parallel, of sorts, with an update one, that is going to be central to the underlining logic of this module.
    This particular method starts by using the 'id' key value, the primary key used in all tables to uniquely identify records and also the common field to all elements used so far in the ThingsBoard interface (id is a string composed of
    8char-4char-4char-4char-12char, i.e., a 32-long string of hexadecimal characters divided in 5 '-' separated segments of 8, 4, 4, 4, and 12 characters each.) to do a simple SELECT to the corresponding database table and, from there,
    decide what to do:
    1. If the SELECT comes back empty, the device doesn't exist yet in the table. Proceed with the INSERT.
    2. The SELECT returns something back. From there do some more verifications to determine if:
        2.1 - There's already a record under that id value but the data in the dictionary doesn't match the one retrieved from the database (all it needs a single bit mismatch in a single field to trigger this) - call the UPDATE method instead
        with the same dictionary data.
        2.2 - There's a record already in the database and is has the same exact data has the dictionary provided. Any operation from this module is going to be redundant so, do nothing (exit).
    @:param data_dict (dict) - A dictionary with the data retrieved from the remote API.
    @:param table_name (str) - The name of the table where to write the data from data dict.
    @:param data_validated (bool) - Parameter used to optimize the method's execution. Since the INSERT method can call the UPDATE method and vice-versa, there's no point in repeating the validation step if the data was already validated in the
    previous run. Use this flag to bypass this process when the method call comes from the 'other' method.
    @:raise utils.InputValidationException - If the data type of any of the inputs doesn't match the expected type
    @:raise mysql_utils.MySQLDatabaseException - If error occur during the database access.
    """
    insert_log = ambi_logger.get_logger(__name__)
    if not data_validated:
        # Proceed with the validation of the data sets
        validate_data_dictionary(data_dict, table_name)

        # One last snag before going further: the mysql-connector that I'm about to use is quite smart in replacing Python exclusive terms (like 'None', 'True' and 'False') and replacing them with the types expected by the MySQL database ('NULL',
        # 'true' and 'false' respectively) but it does stumble when it gets a weirder than normal field, such as the POSIX timestamp that the ThingsBoard API likes to return in its datetime fields. The problem is not with the timestamp itself but
        # the stupid in-between format adopted by the PostGres ThingsBoard database: the standard POSIX timestamp is a 10 digit integer with a 5 or 6 more digits after a decimal point '.' denoting the microseconds value of that datetime value. The
        # garbage returned from the ThingsBoard interface has 13 digits and, worse of all, the decimal point is omitted! Fortunately it didn't took me long to write a method to unravel this mess but that means that I have to convert that value
        # explicitly at this point
        try:
            # Do this verification in a try-except clause to prevent the method from crashing if the dictionary doesn't have this field
            if type(data_dict['createdTime']) == int:
                # Use the proper method to convert this silly value into something meaningful
                data_dict['createdTime'] = mysql_utils.convert_timestamp_tb_to_datetime(int(data_dict['createdTime']))
        except KeyError:
            # Log a simple warning and move on. There no reason to crash this over just this key
            insert_log.warning("The current data dictionary does not have a 'createdTime' key. Moving on...")

    # Get a database connection
    cnx = mysql_utils.connect_db(config.mysql_db_access['database'])

    # And grab a cursor object, this one to be used for SELECTs (There's no reason why I couldn't use to do INSERT/UPDATEs with it too, but experience with this connector tells me that this approach is way more secure towards avoiding nasty bugs
    # at the expense of very little memory cost
    # Set the buffered option to True to avoid memory issues when doing SELECTs over a large number of records (Again, experience...)
    select_cursor = cnx.cursor(buffered=True)

    # Prepare the SELECT statement
    sql_select = """SELECT * FROM """ + str(table_name) + """ WHERE id = %s;"""
    try:
        # All dictionaries from the ThingsBoard API have this structure in common: the actual id that I'm looking for comes in a sub-dictionary with also an 'id' key. But since I haven't personally verified every possible data dictionary
        # returnable from this API, better put this retrieval inside a try-except clause just in case
        data_tuple = (data_dict['id']['id'],)
    except KeyError as ke:
        error_msg = "The current data dictionary is missing the expected data_dict['id']['id'] entry!"
        insert_log.error(error_msg)
        select_cursor.close()
        cnx.close()
        raise ke

    # Run the SELECT statement then
    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, data_tuple)
    # And fetch the first result (should be just one result in the buffer at best)
    result = select_cursor.fetchone()

    # Grab the list of values in the data dictionary too. I'm going to need that plenty going forward. The function writen for that effect mimics the key extractor one in the sense that it uses recursivity to process multi-level dictionaries and
    # returns the data in the same order in which is written, a fundamental assumption in these method since I'm not verifying that at any point (not sure if its even possible though)
    data_value_list = utils.extract_all_values_from_dictionary(data_dict, [])

    # The simplest (and expected) of cases: there's nothing yet in the database with this id string
    if not result:
        # Start preparing the INSERT operation then
        column_list = mysql_utils.get_table_columns(config.mysql_db_access['database'], table_name)
        # Get the skeleton for this INSERT statement from the respective function
        sql_insert = mysql_utils.create_insert_sql_statement(column_list, table_name)
        # The sql_insert statement has everything but the values to be inserted. For this case its just a matter of casting the list of values that I've retrieved already
        data_tuple = tuple(data_value_list)

        # Get a new cursor for this operation
        change_cursor = cnx.cursor(buffered=True)

        # And run the statement finally
        change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_insert, data_tuple)

        # Check if the operation was successful (the cursor's rowcount value should be set to not zero if so)
        if change_cursor.rowcount == 0:
            error_msg = "Tried to execute the SQL INSERT statement '{0}' with data '{1}' but the operation was not successful!".format(str(sql_insert), str(data_tuple))
            insert_log.error(error_msg)
            select_cursor.close()
            change_cursor.close()
            cnx.close()
            raise mysql_utils.MySQLDatabaseException(message=error_msg)
        else:
            # Operation successful! Cool. Commit the changes to the database
            cnx.commit()
            # Close all open connections and cursors
            select_cursor.close()
            change_cursor.close()
            cnx.close()
            # Give an heads up to the user
            insert_log.info("Inserted a new record with data '{0}' into {1}.{2} successfully!".format(str(data_tuple), str(config.mysql_db_access['database']), str(table_name)))

    # If I got here, my SELECT yielded something. Lets find out what exactly
    else:
        # The data in the result variable is still in MySQL-speak while the data dictionary is already translated to Python-speak (please make sure this is done before calling this method since it is way easier to do that when this data is still
        # in a string format than after it has been casted to a dictionary. In fact, casting some data structure straight from the ThingsBoard API, where it was retrieved from a PostGres database, into a Python dictionary is going to throw all
        # sort of NameError Exceptions when it tries to make sense of non-quoted terms such as NULL, true and false, which are not recognizable by Python. To bring both data structures to the same format I need to "translate" my value list into
        # Python-esque first
        result = utils.translate_mysql_to_python(result)

        # Compare both sets using the proper function (details of why I need to do this through a function instead of a simple equality comparison are explained in that function's man entry)
        if utils.compare_sets(data_value_list, list(result)):
            # If the comparison comes back as True
            insert_log.warning("The record (id = {0}) provided already exists in the database! Nothing to do but to exit...".format(str(data_dict['id']['id'])))
            # Close the open cursor and connection
            select_cursor.close()
            cnx.close()
            # And get out of this method
            return True
        # Okay, I've ruled out two scenarios out of three possible ones. By exclusion of parts, I have something in the database with this id but the data isn't a complete match. The only course of action at this point to to go for an UPDATE then
        else:
            insert_log.warning("The data dictionary provided already exists in {0}.{1} but with different data. Running an UPDATE instead...".format(str(config.mysql_db_access['database']), str(table_name)))
            # Close all the open stuff
            select_cursor.close()
            cnx.close()
            # Call the sister method then, signaling that the basic validations are already completed
            update_table_data(data_dict, table_name, data_validated=True)


def update_table_data(data_dict, table_name, data_validated=False):
    """This is the counterpart method to the INSERT one written above. The underlining logic is pretty much the same, except this method determines that the INSERT operation is the one to call, it does just that and only updates a record if,
    like the previous method, detects an existing record with the same id but with different data than the one provided by the input dictionary.
    @:param data_dict (dict) - A dictionary with the data retrieved from the remote API.
    @:param table_name (str) - The name of the table where to write the data from data dict.
    @:param data_validated (bool) - Parameter used to optimize the method's execution. Since the UPDATE method can call the INSERT method and vice-versa, there's no point in repeating the validation step if the data was already validated in the
    previous run. Use this flag to bypass this process when the method call comes from the 'other' method.
    @:raise utils.InputValidationException - If the data type of any of the inputs doesn't match the expected type.
    @:raise Exception - For any other errors
    """
    update_log = ambi_logger.get_logger(__name__)

    if not data_validated:
        validate_data_dictionary(data_dict, table_name)

        # Replace any datetime stuff first for something that MySQL databases can understand
        try:
            if type(data_dict['createdTime']) == int:
                data_dict['createdTime'] = mysql_utils.convert_timestamp_tb_to_datetime(int(data_dict['createdTime']))
        except KeyError:
            # Log a simple warning and move on. There no reason to crash this over just this key
            update_log.warning("The current data dictionary does not have a 'createdTime' key. Moving on...")

    # Create the database connection and a cursor to run the base SELECT
    cnx = mysql_utils.connect_db(table_name)
    select_cursor = cnx.cursor(buffered=True)

    # Prepare the SELECT statement
    sql_select = """SELECT * FROM """ + str(table_name) + """ WHERE id = %s;"""

    try:
        data_tuple = (data_dict['id']['id'],)
    except KeyError as ke:
        error_msg = "The current data dictionary is missing the expected data_dict['id']['id'] entry!"
        update_log.error(error_msg)
        select_cursor.close()
        cnx.close()
        raise ke

    # Run the statement
    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, data_tuple)
    # And grab the first result
    result = select_cursor.fetchone()

    # Test for the simplest of the three possible scenarios: if result came back as None, there's still no record in the database under that id. If that is the case, run an INSERT instead
    if not result:
        update_log.warning("No prior records detected in the database for id = {0}. Running an INSERT operation instead...".format(str(data_tuple[0])))
        # Close the cursor and connection first
        select_cursor.close()
        cnx.close()
        # And call the sister method afterwards
        insert_table_data(data_dict, table_name, data_validated=True)

    # Okay, I got something back from the previous SELECT but I need to see if the UPDATE is really necessary or if it is going to be redundant
    else:
        # Retrieve the value list from the data dictionary.
        value_list = utils.extract_all_values_from_dictionary(data_dict, [])

        # Translate the results from the previous SELECT from MySQL-speak to Python-speak
        result = utils.translate_mysql_to_python(result)

        # And compare the two sets (they both need to be in the list format, so I need to cast the result into one fist)
        if utils.compare_sets(value_list, list(result)):
            # If this comes back as True
            update_log.warning("There is an identical record in the database already with this id ({0}). UPDATE is redundant. Nothing to do but exit...".format(str(data_dict['id']['id'])))
            # Close any open stuff
            select_cursor.close()
            cnx.close()
            # And get out of this
            return True
        # If scenario 1 and 2 are invalidated, this means that an UPDATE is now in order
        else:
            # Get the column list
            column_list = mysql_utils.get_table_columns(config.mysql_db_access['database'], table_name)
            # And prepare the UPDATE statement skeleton from the automatic function (this one takes an extra argument for the trigger column, i.e., what to put in the 'WHERE <column_name> is' part
            sql_update = mysql_utils.create_update_sql_statement(column_list, table_name, 'id')
            # My data tuple for this statement is the value list that I've extracted from the input dictionary already, in a tuple form, but I need to add one extra element to be replaced in the 'WHERE <column_name> is' part goes
            # NOTE: Don't need to do the next attribution inside a try-except anymore since I've done it before in this same method. If it didn't raise an Exception before, sure as hell is not going to do it now
            value_list.append(data_dict['id']['id'])

            # Create a new cursor for the next operation
            change_cursor = cnx.cursor(buffered=True)

            # And run the statement
            change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_update, tuple(value_list))

            # Check if the statement was executed properly
            if change_cursor == 0:
                error_msg = "The SQL UPDATE statement '{0}' was submitted with data '{1}' but it wasn't successful!".format(str(sql_update), str(tuple(value_list)))
                update_log.error(error_msg)
                select_cursor.close()
                change_cursor.close()
                cnx.close()
                raise mysql_utils.MySQLDatabaseException(message=error_msg)
            else:
                update_log.info("SQL UPDATE of record with id = {0} in {1}.{2} successful.".format(str(data_dict['id']['id']), str(config.mysql_db_access['database']), str(table_name)))
                # Don't forget to commit the data to the database (#1 in most annoying database related bugs)
                cnx.commit()
                # Close all stuff still open
                select_cursor.close()
                change_cursor.close()
                cnx.close()


def validate_data_dictionary(data_dict, table_name):
    """This method receives a data dictionary and the name of the table where that data is supposed to be inserted into and validates it by comparing the keys of the dictionary with the column names from the table. As I mentioned before,
    the MySQL tables were created using the dictionary keys from the data that is supposed to be added to them as the names of the columns to simplify the construction of the necessary SQL statements.
    @:param data_dict (dict) - A dictionary with the data to be inserted in the database
    @:param table_name (str) - The name of the table in the MySQL database where the data_dict is going to be added/updated
    @:return True (bool) - If the data_dict keys matches the table columns names. Raise the proper Exception otherwise (deal with the errors as soon as it detects them instead of returning false and losing the Exception data in the process)
    @:raise utils.InputValidationException - If the input elements don't have the expected data types
    @:raise Exception - For any other occurring error or failed validations
    """
    validate_log = ambi_logger.get_logger(__name__)

    # Start by validating the inputs (seems a bit redundant but anyhow..)
    try:
        utils.validate_input_type(data_dict, dict)
        utils.validate_input_type(table_name, str)
    except utils.InputValidationException as ive:
        validate_log.error(ive.message)
        raise ive

    # Inputs are good so far. Extract the dictionary keys using the recursive method created for that into a list
    data_dict_keys = utils.extract_all_keys_from_dictionary(data_dict, [])

    # And now for the other list of stuff to compare to
    column_list = mysql_utils.get_table_columns(config.mysql_db_access['database'], table_name)

    # Do a one to many comparison (because either the INSERT and/or UPDATE statements do not require all columns to be explicit given that all them have default values, at this point I just want to make sure that the set data_dict_keys is,
    # at least, a subset of the column_list. If an element from the data_dict_key is not in the column_list set, the resulting INSERT and/or UPDATE statement is going to crash)
    for data_key in data_dict_keys:
        if data_key not in column_list:
            error_msg = "The key '{0}' from the input dictionary doesn't have a corresponding column in table {1}.{2}.".format(str(data_key), str(config.mysql_db_access['database']), str(table_name))
            validate_log.error(error_msg)
            raise Exception(error_msg)

    # If the dictionary survived the previous for loop, all is good
    return True
