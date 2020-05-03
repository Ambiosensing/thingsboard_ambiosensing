"""The process of writing data to a database table can be abstracted and generalized in a way that supplying a data dictionary and the table in question should be enough to trigger the logic that either going to add new records,
updated existing ones or do nothing in case the data received is identical to an existing record
"""

import user_config
import proj_config
import utils
from mysql_database.python_database_modules import mysql_utils
import ambi_logger


def add_table_data(data_dict, table_name):
    """
    Method that abstracts the insertion of data into the provided database table. The method maps the provided data dictionary to any available column in the table identified in table name. The method uses the table data as main reference, i.e.,
    it only writes data whose key in the data dictionary has a direct correspondence to a table column in the database. If more the data dictionary has more keys/items than available columns, an log warning is issued about it but the method
    carries on writing in all available data.
    @:param data_dict (dict) - A dict structure, i.e., a key-value arrangement with the data to be added/updated into the database table. IMPORTANT: The table columns name were prepared such that there's a one-to-one equivalence between them and
    the expected keys in the data dictionary.
    @:param table_name (str) - The name of the database where the data dict has to be written into.
    @:raise utils.InputValidationException - If any of the inputs fails initial validation.
    @:raise mysql_utils.MySQLDatabaseException - If any issues occur with the database accesses.
    @:return result (bool) - If the database addition/update was performed successfully, this method returns True. Otherwise, the appropriate exception is raised with the details on why it was raised in the first place.
    """
    log = ambi_logger.get_logger(__name__)

    # Validate inputs
    utils.validate_input_type(data_dict, dict)
    utils.validate_input_type(table_name, str)

    # Prepare the database access objects
    database_name = user_config.access_info['mysql_database']['database']
    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)
    change_cursor = cnx.cursor(buffered=True)

    # First, check if the table exists
    sql_select = """SHOW tables FROM """ + str(database_name) + """;"""

    select_cursor = mysql_utils.run_sql_statement(cursor=select_cursor, sql_statement=sql_select, data_tuple=())

    records = select_cursor.fetchall()

    # The result of the previous fetchall command is a list of one element tuples, hence why I'm putting the name that I want to verify its existence in such list as a one element tuple. The alternative was to format the previous list into a
    # single string list element, but it is way more simple this way
    if (table_name,) not in records:
        error_msg = "The table name provided: {0} doesn't exist yet in database {1}. Cannot continue.".format(str(table_name), str(database_name))
        log.error(error_msg)
        raise utils.InputValidationException(message=error_msg)

    # Okay, the table exists in the database. Get all its columns into a list
    column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)

    # And create the standard INSERT statement from it
    sql_insert = mysql_utils.create_insert_sql_statement(column_list=column_list, table_name=table_name)

    # Build the respective data tuple by going through all column names and checking if there is a corresponding key in the data dictionary
    data_list = []

    for i in range(0, len(column_list)):
        try:
            # First, try to retrieve a value into the data list by doing a direct retrieval from the data dictionary using the column name as key
            data_list.append(data_dict[column_list[i]])

        # If the current column name doesn't have a matching key in the data dictionary, catch the expected Exception
        except KeyError:
            # And replace the missing value with a None since, by default, all table columns were created in a way where they hold such value
            # But warn the user first
            log.warning("Didn't find any '{0}' keys in the data dictionary provided. Setting the {0} column in {1}.{2} to NULL"
                        .format(str(column_list[0]), str(database_name), str(table_name)))
            # And set the value then
            data_list.append(None)

    # Done. Proceed with the INSERT
    try:
        change_cursor = mysql_utils.run_sql_statement(cursor=change_cursor, sql_statement=sql_insert, data_tuple=tuple(data_list))

        # Check the outcome of the previous execution. If no columns were changed in the previous statement, raise a 'Duplicate entry' Exception to trigger an UPDATE instead
        if change_cursor.rowcount is 0:
            # No changes to the database table detected. Trigger an UPDATE then
            raise mysql_utils.MySQLDatabaseException(message=proj_config.double_record_msg)
        elif change_cursor.rowcount == 1:
            # In this case, all went well. Close the database access objects, commit the changes to the database, inform the user of this and move on
            log.info("Successfully added a new record to {0}.{1}".format(str(database_name), str(table_name)))
            cnx.commit()
            select_cursor.close()
            change_cursor.close()
            cnx.close()
            return True

    # Watch out for the typical "Duplicate entry" exception
    except mysql_utils.MySQLDatabaseException as mse:
        if proj_config.double_record_msg in mse.message:
            trigger_column_list = mysql_utils.get_trigger_columns(table_name=table_name)

            # Cool. Use this data to get the respective UPDATE statement
            sql_update = mysql_utils.create_update_sql_statement(column_list=column_list, table_name=table_name, trigger_column_list=trigger_column_list)

            # And complete the existing data list by appending to it the values corresponding to the elements in the trigger list
            for trigger_column_name in trigger_column_list:
                try:
                    data_list.append(data_dict[trigger_column_name])
                except KeyError:
                    error_msg = "The value for the trigger column '{0}' cannot be found among the data dictionary elements! Cannot continue!".format(str(trigger_column_name))
                    log.error(error_msg)
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()
                    raise mysql_utils.MySQLDatabaseException(message=error_msg)

            # Done. Run the UPDATE statement, still looking for duplicate records
            try:
                change_cursor = mysql_utils.run_sql_statement(cursor=change_cursor, sql_statement=sql_update, data_tuple=tuple(data_list))

                # Check the UPDATE execution status
                if change_cursor.rowcount is 0:
                    # If nothing happened, the record already exists in the database. Give a bit of heads up and move on
                    log.warning("A record with data:\n{0}\n already exists in {1}.{2}. Nothing more to do...".format(str(data_list), str(database_name), str(table_name)))
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()
                    return False
                # Else, if more than one records were modified
                if change_cursor.rowcount != 1:
                    error_msg = "Could not execute\n{0}\nin {1}.{2}. Cannot continue..".format(str(change_cursor.statement), str(database_name), str(table_name))
                    log.error(error_msg)
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()
                    raise mysql_utils.MySQLDatabaseException(message=error_msg)
                else:
                    info_msg = "Updated record with  successfully in {0}.{1}".format(str(database_name), str(table_name))
                    log.info(info_msg)
                    cnx.commit()
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()
                    return True
            except mysql_utils.MySQLDatabaseException as mse:
                # If a duplicate result was still found with the last UPDATE execution
                if proj_config.double_record_msg in mse.message:
                    # Inform the user with a warning message
                    warn_msg = "The record with "
                    for i in range(0, len(trigger_column_list) - 1):
                        warn_msg += str(trigger_column_list[i]) + " = " + str(data_dict[trigger_column_list[i]]) + ", "

                    warn_msg += str(trigger_column_list[-1]) + " = " + str(data_dict[trigger_column_list[-1]]) + " already exists in {0}.{1}. Nothing to do then..." \
                        .format(str(database_name), str(table_name))

                    log.warning(warn_msg)

                    # Close out all database access objects
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()

                    # Nothing else that can be done here. Move out
                    return True
                else:
                    # Some other Exception was raised then
                    select_cursor.close()
                    change_cursor.close()
                    cnx.close()

                    # Forward the Exception then
                    raise mse
        else:
            select_cursor.close()
            change_cursor.close()
            cnx.close()
            # Something else must have happened then. Keep on raising the Exception
            raise mse
