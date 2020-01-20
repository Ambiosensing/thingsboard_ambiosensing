""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group auth-controller, as well as the authorization token
management methods"""
import ambi_logger
import utils
import user_config
import proj_config
import datetime
from mysql_database.python_database_modules import mysql_utils
from ThingsBoard_REST_API import tb_auth_controller

# TODO - Create a get_all_auth_tokens method that reads the access dictionary in the user_config.access_info and populates the proper database table accordingly
# TODO - Create a database table to store the provided authorization tokens, as well as the information associated to it (user type, access type, etc..)
# TODO - Create a refresh tokens method that can be set to run automatically through an independent process/thread or called upon when needed to get valid tokens


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

    # Grab the full column list from the database for indexing purposes
    column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)

    # Lets see if there's any token already in the database
    sql_select = """SELECT token FROM """ + str(table_name) + """ WHERE user_type = %s;"""

    select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (user_type,))

    # Check if any results came back
    if select_cursor.rowcount > 0:
        # I got a valid token back. Check if it is not yet expired. Grab the token retrieved by grabbing the only element returned in the response tuple.
        auth_token = select_cursor.fetchone()[0]

        # And call the getUser service providing the retrieved token to see if a) the token is still valid and b) the user_type provided matches what the remote API sends back
        token_status_response = tb_auth_controller.getUser(auth_token=auth_token)

        # And convert the response body into the expected dictionary for easier access after this point
        token_status_dict = eval(token_status_response.text)

        if token_status_response.status_code != 200:
            # TODO: Take care of the expired token and invalid credential cases (wrong username/password pair) here
            pass
        # Check if the response returned has the user type (which would be under the 'authority' key in the response dictionary), matches the user_type provided (it would be quite weird if doesn't, but check it anyways)
        elif token_status_dict['authority'].lower() != user_type:
            auth_token_log.warning("Attention: the authorization token retrieved from {0}.{1} for user type '{2}' provided is actually associated with a '{3}' user type! Resetting..."\
                .format(str(database_name), str(table_name), str(user_type), str(token_status_dict['authority'])))

            # TODO: From here, update the database user_type to the correct entry returned by the last API call
            # TODO: Request a new pair of authorization/refresh tokens for the user type in the arguments and save them to the database

        # The HTTP status code is a nice 200 OK. Nothing to do but to return the valid token
        else:
            auth_token_log.info("Got a still valid authorization token for user type {0} from {1}.{2}.".format(str(user_type), str(database_name), str(table_name)))
            # Close the database structures before returning the token
            select_cursor.close()
            cnx.close()
            return auth_token
    # Otherwise it means that the database entry for this particular user wasn't filled in yet
    else:
        # TODO:
        pass

