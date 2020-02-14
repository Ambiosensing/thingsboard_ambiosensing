""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group auth-controller, as well as the authorization token
management methods"""
import ambi_logger
import utils
import user_config
import proj_config
import datetime
from mysql_database.python_database_modules import mysql_utils
from ThingsBoard_REST_API import tb_auth_controller


def populate_auth_table():
    """Use this method to request a new set of valid authorization tokens for all defined user types and to write them into the database. By default, this method starts by cleaning out any records currently in the authorization table in the
    database since this method is supposed to be called at the start of a new session
    @:raise mysql_utils.MySQLDatabaseException - If there are problems with the access to the database
    @:raise utils.AuthenticationException - If the access credentials in the user_config file are not valid
    @:raise utils.ServiceEndpointException - For problems with the remote API access"""
    populate_auth_log = ambi_logger.get_logger(__name__)

    # Start by cleaning out the authorization table
    database_name = user_config.mysql_db_access['database']
    table_name = proj_config.mysql_db_tables['authentication']
    cnx = mysql_utils.connect_db(database_name=database_name)
    column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)
    change_cursor = cnx.cursor(buffered=True)

    populate_auth_log.info("Cleaning out {0}.{1}...".format(str(database_name), str(table_name)))

    # Prepare the DELETE statement by deleting all records older than a datetime argument
    sql_delete = """DELETE FROM """ + str(table_name) + """ WHERE token_timestamp < %s;"""

    # And execute it providing the current datetime as argument, thus effectively deleting all records in the database (unless some have future timestamps, which makes no sense whatsoever)
    change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_delete, (datetime.datetime.now().replace(microsecond=0),))

    if not change_cursor.rowcount:
        populate_auth_log.info("{0}.{1} was already empty. Populating it now...".format(str(database_name), str(table_name)))
    else:
        populate_auth_log.info("Deleted {0} records from {1}.{2}. Populating new records now...".format(str(change_cursor.rowcount), str(database_name), str(table_name)))

    cnx.commit()

    # Grab a new authorization dictionary
    auth_dict = tb_auth_controller.get_session_tokens(sys_admin=True, tenant_admin=True, customer_user=True)

    # And populate the database accordingly
    for user_type in auth_dict:
        sql_insert = mysql_utils.create_insert_sql_statement(column_list=column_list, table_name=table_name)

        # Add the values to insert in the order in which they are expected, namely:
        # user_type, token, token_timestamp, refreshToken and refreshToken_timestamp
        data_tuple = (user_type, auth_dict[user_type]['token'], datetime.datetime.now().replace(microsecond=0), auth_dict[user_type]['refreshToken'], datetime.datetime.now().replace(microsecond=0))

        # And execute the INSERT
        change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_insert, data_tuple)

        # Check if the execution was successful
        if not change_cursor.rowcount:
            error_msg = "Unable to execute '{0}' in {1}.{2}. Exiting...".format(str(change_cursor.statement), str(database_name), str(table_name))
            populate_auth_log.error(error_msg)
            change_cursor.close()
            cnx.close()
            raise mysql_utils.MySQLDatabaseException(message=error_msg)
        else:
            cnx.commit()
            populate_auth_log.info("Added a pair of authorization tokens for {0} in {1}.{2} successfully!".format(str(user_type), str(database_name), str(table_name)))

    # Done. Inform the user and exit
    populate_auth_log.info("{0}.{1} populated successfully!".format(str(database_name), str(table_name)))


def get_auth_token(user_type):
    """This is going to be the go-to method in this module. This method receives one of the supported user types ('SYS_ADMIN', 'TENANANT_ADMIN' or 'CUSTOMER_USER') and fetches the respective authorization token. What this method does to get it is
    abstracted from the user. This method automatically checks the usual suspects first: database table. If there's any token in there for the provided user type, it then tests it to see if it is still valid. If not, it then tries to use the
    refresh token to issue a valid one and, if that is also not possible, request a new pair of authentication and refresh tokens.
    This method should be integrated into basic service calls to save the user to deal with the whole authorization token logistics
    @:param user_type (str) - One of the following supported user types: sys_admin, tenant_admin, customer_user (the case type of this argument is irrelevant because I will take care of it later on)
    @:raise utils.InputValidationException - If an invalid argument is provided
    @:raise utils.AuthenticationException - If the authentication credentials are not correct
    @:raise utils.ServiceEndpointException - If the call to the remote service fails
    @:raise mysql_utils.MySQLDatabaseException - If problems arise when dealing with the database
    @:return token (str) - A valid authorization token that can be used to authenticate a remote service call"""

    auth_token_log = ambi_logger.get_logger(__name__)

    # Validate the input as a data type and as one of the expected user types
    utils.validate_input_type(user_type, str)

    # Set the user type string to all lower case characters to simplify comparisons from this point on
    user_type = user_type.lower()
    supported_user_types = ['sys_admin', 'tenant_admin', 'customer_user']

    if user_type not in supported_user_types:
        raise utils.InputValidationException("Invalid user type provided: '{0}'. Please provided one of these: {1}".format(str(user_type), str(supported_user_types)))

    # All seems good so far. Lets check the database first
    database_name = user_config.mysql_db_access['database']
    table_name = proj_config.mysql_db_tables['authentication']

    cnx = mysql_utils.connect_db(database_name=database_name)
    select_cursor = cnx.cursor(buffered=True)
    change_cursor = cnx.cursor(buffered=True)

    # Use the next dictionary to store the reply for when a new authorization token needs to be requested (which can happen for a number of different reasons) and check for it after the sets of if-else following the database check. This avoids
    # repeating code by enabling the INSERT operation to be run in a single instance (if the new_auth_dict is not None(«)
    new_auth_dict = None

    # Grab the full column list from the database for indexing purposes
    column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)

    # Lets see if there's any token already in the database
    sql_select = """SELECT token, refreshToken FROM """ + str(table_name) + """ WHERE user_type = %s;"""

    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (user_type,))

    # Check if any results came back
    if select_cursor.rowcount > 0:
        # I got a valid token pair back. Extract the authorization from it
        auth_token = select_cursor.fetchone()[0]

        # And call the getUser service providing the retrieved token to see if a) the token is still valid and b) the user_type provided matches what the remote API sends back
        token_status_response = tb_auth_controller.getUser(auth_token=auth_token)

        # And convert the response body into the expected dictionary for easier access after this point.
        # NOTE: Interesting development in this case: it turns out that I can authorize a user using a authorization token that was issued from a different ThingsBoard installation!!! In other words, I can get a authorization token issued from my
        # local ThingsBoard installation and use it to get a "valid" authentication in the remote ThingsBoard installation. When I say "valid" I mean, the interface accepts the token without any kind of feedback regarding its actual validity. Yet,
        # when I execute a service with it, guess what? I do get a HTTP 200 response but without any data!! This doesn't make any sense and is going to complicate my code a lot! So I need to deal with this retarded cases too...
        # Attempt to do the following only if something was returned back in the text parameter of the response
        token_status_dict = None

        if token_status_response.text != "":
            token_status_dict = eval(utils.translate_postgres_to_python(token_status_response.text))

        # This particular annoying case in which a valid authorization token from a different installation is used in this case. In this case, the installation accepts the token, since it has the expected format, but internally it gets rejected
        # because the credential pair that originated it obviously doesn't match! But somehow the API fails to mention this! Instead, the damn thing accepts the token and even returns HTTP 200 responses to my requests but these come back all
        # empty, presumably because the internal authentication failed... because the tokens are wrong. Gee, what an unnecessary mess... If a case such as that is detected, simply get a new pair of tokens back. Most of these cases are solved by
        # forcing a token refresh
        if token_status_response.status_code != 200 or token_status_response.text == "":
            # Check the most usual case for a non-HTTP 200 return: HTTP 401 with sub-errorCode (its embedded in the response text) 11 - the authorization token has expired
            if token_status_response.status_code == 401 and eval(token_status_response.text)['errorCode'] == 11:
                # Inform the user first
                auth_token_log.warning("The authorization token for user type = {0} retrieved from {1}.{2} is expired. Requesting new one...".format(str(user_type), str(database_name), str(table_name)))
            elif token_status_response.text == "":
                auth_token_log.warning("The authorization provided was issued from a different ThingsBoard installation than this one! Need to issued a new pair...")

            # Use the refresh token to retrieve a new authorization dictionary into the proper variable. No need to provide the refresh token: the tb_auth_controller.refresh_session_token method already takes care of retrieving it from the
            # database. Create a dictionary to call this method by setting all user_types to False except the one that I want
            new_auth_dict = {'sys_admin': False, 'tenant_admin': False, 'customer_user': False, user_type: True}

            # If I caught that annoying case in which a valid authorization token from a different ThingsBoard installation
            if token_status_response.text == "":
                new_auth_dict = tb_auth_controller.get_session_tokens(
                    sys_admin=new_auth_dict['sys_admin'],
                    tenant_admin=new_auth_dict['tenant_admin'],
                    customer_user=new_auth_dict['customer_user']
                )
                auth_token_log.info("Got a new pair of authorization tokens for the {0} ThingsBoard installation.".format(str(user_config.access_info['host'])))
            # Otherwise, its an expired token case. Deal with it properly then
            # NOTE: The call to the refresh_session_token method already verifies and deals with expired refreshTokens too.
            else:
                new_auth_dict = tb_auth_controller.refresh_session_token(
                    sys_admin=new_auth_dict['sys_admin'],
                    tenant_admin=new_auth_dict['tenant_admin'],
                    customer_user=new_auth_dict['customer_user']
                )
                auth_token_log.info("Refreshed the authorization tokens for the {0} ThingsBoard installation.".format(str(user_config.access_info['host'])))

            # From this point on, the process is the same for both cases considered above

            # If I got to this point, then my new_auth_dict has a fresh pair of authorization and refresh tokens under the user_type key entry (the previous call raises an Exception otherwise)
            # In this case, I have the tokens in the database expired. Update these entries before returning the valid authorization token
            sql_update = mysql_utils.create_update_sql_statement(column_list=column_list, table_name=table_name, trigger_column='user_type')

            # Prepare the data tuple for the UPDATE operation respecting the expected order: user_type, token, token_timestamp, refreshToken, refreshToken_timestamp and user_type again (because of the WHERE clause in the UPDATE)
            update_data_tuple = (user_type, new_auth_dict[user_type]['token'], datetime.datetime.now().replace(microsecond=0), new_auth_dict[user_type]['refreshToken'], datetime.datetime.now().replace(microsecond=0), user_type)

            # Execute the statement
            change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_update, update_data_tuple)

            # And check the execution results
            if not change_cursor.rowcount:
                error_msg = "Could not update {0}.{1} with '{2}' statement...".format(str(database_name), str(table_name), str(change_cursor.statement))
                auth_token_log.error(error_msg)
                change_cursor.close()
                select_cursor.close()
                cnx.close()
                raise mysql_utils.MySQLDatabaseException(message=error_msg)
            else:
                auth_token_log.info("Token database information for user_type = '{0}' updated successfully in {1}.{2}!".format(str(user_type), str(database_name), str(table_name)))
                cnx.commit()
                # Close the database access objects and return the valid token then
                change_cursor.close()
                select_cursor.close()
                cnx.close()
                return new_auth_dict[user_type]['token']
        # Check if the response returned has the user type (which would be under the 'authority' key in the response dictionary), matches the user_type provided (it would be quite weird if doesn't, but check it anyways)
        elif token_status_dict is not None and token_status_dict['authority'].lower() != user_type:
            auth_token_log.warning("Attention: the authorization token retrieved from {0}.{1} for user type '{2}' provided is actually associated with a '{3}' user type! Resetting...".
                                   format(str(database_name), str(table_name), str(user_type), str(token_status_dict['authority'])))
            # Mismatch detected. Assuming that the ThingsBoard API only accepts user types from the set defined and since I've validated the user type provided as argument also, this means that my mismatch is at the MySQL database level,
            # that somehow has a valid authentication token submitted under a valid user type, just not the correct one
            # First, update the user_type in the database for the correct one (the one retrieved from the remote API)
            remote_user_type = token_status_dict['authority']
            # Request an UPDATE SQL template to replace the current user type by the correct remote_user_type
            sql_update = mysql_utils.create_update_sql_statement(['user_type'], table_name, 'user_type')
            data_tuple = (remote_user_type, user_type)

            # Execute the statement
            change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_update, data_tuple)

            # Check if something was done
            if not change_cursor.rowcount:
                error_msg = "Update operation '{0}' in {1}.{2} not successful!".format(str(change_cursor.statement), str(database_name), str(table_name))
                auth_token_log.error(error_msg)
                change_cursor.close()
                select_cursor.close()
                cnx.close()
                raise mysql_utils.MySQLDatabaseException(message=error_msg)
            else:
                # Commit the changes, warn the user, request a new authentication token for the original user_type requested, save it in the database (in a new entry given that the last one was changed) and return the valid authorization token
                # back, which should always be what this method does before exiting (either this or raise an Exception)
                cnx.commit()

                auth_token_log.warning("Successfully updated user_type = {0} entry to {1} in {2}.{3}. Requesting new authorization token to {0}...".format(str(user_type), str(remote_user_type), str(database_name), str(table_name)))

                # Set out the flags for the new session token request, setting all user_types to False at first but then switching on to True only the one matching the provided user_type
                new_auth_dict = {'sys_admin': False, 'tenant_admin': False, 'customer_user': False, user_type: True}

                # And now I can request a new session token for only the user_type that I need without having to explicit a different call signature for each possible case. Clever!
                new_auth_dict = tb_auth_controller.get_session_tokens(
                    sys_admin=new_auth_dict['sys_admin'],
                    tenant_admin=new_auth_dict['tenant_admin'],
                    customer_user=new_auth_dict['customer_user']
                )

                # If I got here, it means that I have a new authorization dictionary with all entries set to None except the one corresponding to the requested user_type. Update the database and return the token back to the user. Since the
                # new_auth_dict is properly filled, I can now ignore the rest of this if-else jungle. The fact that new_auth_dict is not None anymore is going to trigger an INSERT operation with its data into the database
                pass

        # The HTTP status code is a nice 200 OK. Nothing to do but to return the valid token
        else:
            auth_token_log.info("Got a still valid authorization token for user type {0} from {1}.{2}.".format(str(user_type), str(database_name), str(table_name)))
            # Close the database structures before returning the token
            select_cursor.close()
            change_cursor.close()
            cnx.close()
            return auth_token

    else:
        # If I get to this point it means that no valid authorization token was found so far in the database. Yet, there is a possibility that some other token request may have be been placed in the logic above and now it needs the data retrieved to
        # be sent to the database. I can detect this by looking at the new_auth_dict variable. If its None, it means that I need to request a new pair of tokens for this user_type.
        # Create a base for the new authorization dictionary by setting all user_types to False initially and then triggering just the one that needs new authorization tokens to True
        new_auth_dict = {'sys_admin': False, 'tenant_admin': False, 'customer_user': False, user_type: True}

        # And use this to request a new pair of authorization tokens from the remote API
        new_auth_dict = tb_auth_controller.get_session_tokens(
            sys_admin=new_auth_dict['sys_admin'],
            tenant_admin=new_auth_dict['tenant_admin'],
            customer_user=new_auth_dict['customer_user']
        )

    # In any case, I should have a new_auth_dict dictionary here with one entry filled in with a valid authorization token. Time to add it to the database
    sql_insert = mysql_utils.create_insert_sql_statement(column_list=column_list, table_name=table_name)

    # And create the data tuple by replacing the members in the column_list retrieved before by the corresponding values
    column_list[column_list.index('user_type')] = user_type
    column_list[column_list.index('token')] = new_auth_dict[user_type]['token']
    column_list[column_list.index('token_timestamp')] = datetime.datetime.now().replace(microsecond=0)
    column_list[column_list.index('refreshToken')] = new_auth_dict[user_type]['refreshToken']
    column_list[column_list.index('refreshToken_timestamp')] = datetime.datetime.now().replace(microsecond=0)

    # Execute the statement
    change_cursor = mysql_utils.run_sql_statement(change_cursor, sql_insert, tuple(column_list))

    if not change_cursor.rowcount:
        error_msg = "Failed to execute '{0}' in {1}.{2}. Exiting...".format(str(change_cursor.statement), str(database_name), str(table_name))
        auth_token_log.error(error_msg)
        change_cursor.close()
        select_cursor.close()
        cnx.close()
        raise mysql_utils.MySQLDatabaseException(message=error_msg)
    else:
        cnx.commit()
        auth_token_log.info("Added authorization token from user_type = {0} to {1}.{2} successfully!".format(str(user_type), str(database_name), str(table_name)))
        # Return the token then
        select_cursor.close()
        change_cursor.close()
        cnx.close()
        return new_auth_dict[user_type]['token']
