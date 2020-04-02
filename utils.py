import requests
import ast
import user_config
import traceback
import ambi_logger
import logging
import proj_config


# -------------------------------------------------------------------- CUSTOM EXCEPTIONS -----------------------------------------------------------------------
class AuthenticationException(Exception):
    """ This is a template for an exception created on purpose to deal with authentication issues """

    # Message attached to the exception (for displaying when the exception occurs/is raised)
    message = None
    # A simple error_code of little consequence at this stage but that can be quite important later on. For now the simplest convention is error_code=0: all
    # went well, error_code=1: something wrong happened (duh...)
    error_code = 0
    # The program stack (which contains the line number of the instruction responsible for raising this exception, along with other useful debugging info). Its
    # filled automatically by the exception constructor (bellow).
    stack = None

    def __init__(self, message, error_code=0):
        """ Constructor for the AuthenticationException class
         @:param message - The message to be attached to this object, for later displaying
         @:param error_code - Can be used to define different stages in which this exception might be raised.
         @:return an AuthenticationException object (from the class Exception) with the custom message and error_code and the stack image when the exception was
         thrown
         """
        self.message = message
        self.error_code = error_code
        # The program stack is added automatically by the constructor using the respective module (traceback)
        self.stack = traceback.format_exc()


class InputValidationException(Exception):
    """An extension of the basic Extension class that is going to be used to signal problems with the validation of input arguments to method calls."""
    message = None
    error_code = None
    stack_trace = None

    def __init__(self, message=None, error_code=None):
        """The basic constructor of this class
        @:param message (str) - The message to be displayed when throwing this Exception
        @:param error_code (int) - A value that is useful for some cases
        @:raise Exception - For errors related with the validation of inputs
        """
        if not message:
            self.message = "An Exception was raised but there is no additional info over it."
            # Fill out the stack trace in this particular case
            self.stack_trace = traceback.format_exc()
        else:
            # Validate the argument against its expected data type
            if type(message) != str:
                raise Exception("ERROR: The exception message provided ({0}) has the wrong data type (not a str). type(message) = {1}."
                                .format(str(message), str(type(message))))

            self.message = message

        if not error_code:
            # The default error code in this case
            self.error_code = -1
        else:
            if type(error_code) != int:
                # Do the same verification for the error code too
                raise Exception("ERROR: The error code provided ({0}) has the wrong data type (not an int). type(error_code) = {1}."
                                .format(str(error_code), str(type(error_code))))
            self.error_code = error_code


class ServiceEndpointException(InputValidationException):
    """Another custom Exception, this time based on a custom exception. This one is going to be used to signal problems with the calls to the remote API
    services."""
    message = None
    error_code = None
    stack_trace = None

    def __init__(self, message=None, error_code=None):
        """The basic constructor in this class
        @:param message (str) - The message to be displayed when throwing this Exception
        @:param error_code (int) - The error code to be returned
        @:raise Exception - For errors related with the validation of inputs"""

        if not message:
            self.message = "An Exception was raised but there is no additional info over it."
            # Fill out the stack trace in this particular case
            self.stack_trace = traceback.format_exc()
        else:
            # Validate the argument against its expected data type
            if type(message) != str:
                raise Exception("ERROR: The exception message provided ({0}) has the wrong data type (not a str). type(message) = {1}."
                                .format(str(message), str(type(message))))

            # Set the argument message then
            self.message = message

        if not error_code:
            # The default error code if nothing is passed as argument
            self.error_code = -1
        else:
            if type(error_code) != int:
                # Do the same verification for the error code too
                raise Exception("ERROR: The error code provided ({0}) has the wrong data type (not an int). type(error_code) = {1}."
                                .format(str(error_code), str(type(error_code))))

            self.error_code = error_code


# ----------------------------------------------------------------- AUTHENTICATION METHODS ---------------------------------------------------------------------
# The endpoints of the authentication API are not all exposed in the ThingsBoard interface. As such they are getting explicit here.
authentication_API_paths = {
    "token": "/api/auth/login",
    "refreshToken": "/api/auth/token"
}


# DEPRECATED: use mysql_database.python_database_modules.mysql_auth_controller.get_auth_token() or ThingsBoard_REST_API.tb_auth_controller.get_session_tokens() instead
def _get_new_session_token(connection_dict):
    """ Lets start with the basics. This method receives a dictionary object such as the one set in the config.py
     file, extracts the necessary connection parameters and, if all is OK, sends an HTTP request for a valid session
     token
     @:param connection_dict - a dictionary containing the host, port, username and password to connect successfully to a thingsboard instance
     @:return if successful, returns a string with an authentication token
     @:raise InvalidAuthenticationData if not successful (needs to be properly catch somewhere above) """

    new_session_log = ambi_logger.get_logger(__name__)

    # Validate the provided connection dictionary before anything else
    validate_connection_dict(connection_dict)

    # Build the elements of the POST command to request the authentication token. All of the remaining data, headers and
    # such, are defined by default from the standard curl command to retrieve the authentication tokes
    con_url = str(connection_dict["host"]) + ":" + str(connection_dict["port"]) + authentication_API_paths["token"]
    con_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    # NOTE: The syntax for the authentication POST request is a
    con_data = '{"username": "' + str(connection_dict["username"]) + '", "password": "' + str(connection_dict["password"]) + '"}'

    # And here's the main call to the remote server, this time using the 'requests' package instead of curl or other
    # utility. The structure of the command is slightly different but in the end it yields to the same.
    new_session_log.info("Requesting {0}...".format(str(con_url)))
    try:
        response = requests.post(url=con_url, data=con_data, headers=con_headers)
    except (requests.ConnectionError, requests.ConnectTimeout):
        error_msg = "Unable to establish a connection with {0}. Exiting...".format(str(str(user_config.thingsboard_host) + ":" + str(user_config.thingsboard_port)))
        new_session_log.error(error_msg)
        raise AuthenticationException(error_msg)

    # If a non OK response is returned, treat it as something abnormal, i.e, throw an AuthenticationException with its
    # data populated with the returned response data
    if response.status_code != 200:
        new_session_log.error(response.text)
        raise AuthenticationException(message=response.text, error_code=response.status_code)

    # The required token is returned initially in a text (string) form, but its actually a dictionary
    # casted into a string. So, for simplicity sake, return the returned string to its dictionary form and return it
    return ast.literal_eval(response.text)


# DEPRECATED: use mysql_database.python_database_modules.mysql_auth_controller.get_auth_token() or ThingsBoard_REST_API.tb_auth_controller.refresh_session_tokens() instead
def _refresh_authorization_tokens(admin=False):
    """ This method simply does a call to the get_new_session_token to get a new set of fresh authorization and refresh tokens from the server.
     This is just to abstract the following code a bit more since I've realised that I'm calling the aforementioned method all the time
     @:param admin - a boolean indicating if the tokens to be refreshed are for an admin profile (admin=True) or a regular profile(admin=False). Default option is always 'regular user' (admin=False)
     @:raise AuthenticationException - if the admin argument is empty or not a boolean
     @:return a dictionary with a fresh set of authorization and refresh tokens
     {
        'token': string,
        'refreshToken': string
     }
     """
    refresh_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(admin, bool)
    except InputValidationException as ive:
        refresh_log.error(ive.message)
        raise ive

    if admin:
        return _get_new_session_token(user_config.access_info['sys_admin'])
    else:
        return _get_new_session_token(user_config.access_info['tenant_admin'])


def validate_connection_dict(connection_dict):
    """ This method receives a dictionary with connection credentials and checks if the structure is sound
    @:param connection_dict - a dictionary containing access credentials
    @:raise AuthenticationException - in case that the dictionary provided does not has the expected structure
    @:return True - if the provided dictionary is well formed"""

    validate_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(connection_dict, dict)
    except InputValidationException as ive:
        validate_log.error(ive.message)
        raise ive

    error_msg = None
    error_code = 0

    # Validate the various aspects expected from the connection dictionary
    if len(connection_dict) != 4:
        error_msg = "Wrong number of elements in the authentication dicitionary: {0}".format(str(len(connection_dict)))
    # Try to get a host from the provided dictionary. If it return None, throw the exception. The rest falls alike
    elif not connection_dict.get("host"):
        error_msg = "Please provide a valid host key in the authentication dictionary"
    elif not connection_dict.get("port"):
        error_msg = "Please provide a valid port key in the authentication dictionary"
    elif not connection_dict.get("username"):
        error_msg = "Please provide a valid username key in the authentication dictionary"
    elif not connection_dict.get("password"):
        error_msg = "Please provide a valid password key in the authentication dictionary"

    if error_msg:
        # If the error message was set, log its contents as ERROR
        validate_log.error(error_msg)
        # If not, then at this point I should have the error message that disqualified the dictionary in the first place
        raise AuthenticationException(error_msg, error_code)


def check_auth_dict(auth_dict):
    """ Simple method to double check if the dictionary that its possible to obtain by parsing the auth_token file is consistent with what is expected,
     i.e., that it is a dictionary, it has two and only two entries and that those entries are 'auth_token' and 'refresh_token' respectively
     @:param auth_dict - the dictionary containing the expected authorization and refresh tokens for both the admin and regular user profiles
     @:raise AuthenticationException - if the dictionary is deemed invalid/not well formed
     @:return True - if the dictionary provided is well formed"""

    check_log = ambi_logger.get_logger(__name__)

    # Check if the structure is in the right form. It should be a dictionary of dictionaries
    try:
        validate_input_type(auth_dict, dict)
    except InputValidationException as ive:
        check_log.error(ive.message)
        raise ive

    # Check if it has the right number of elements
    if len(auth_dict) != 2:
        error_msg = "The dictionary has a wrong number of elements (not 2): current dictionary length: " + str(len(auth_dict))
        check_log.error(error_msg)
        raise AuthenticationException(message=error_msg, error_code=1)

    # At this level, I might as well check if the 'admin' and 'regular' keys are the ones in the dictionary obtained from the auth_token file. I've already
    # checked if it has 2 and only 2 elements, therefore the next verification
    # is going to ensure that the two elements detected are indeed the ones expected
    try:
        auth_dict['admin']
    except KeyError:
        error_msg = "Missing the 'admin' key from the authorization dictionary - level 1"
        check_log.error(error_msg)
        raise AuthenticationException(message=error_msg, error_code=1)

    try:
        auth_dict['regular']
    except KeyError:
        error_msg = "Missing the 'regular' key from the authorization dictionary - level 1"
        check_log.error(error_msg)
        raise AuthenticationException(message=error_msg, error_code=1)

    # Given that the main structure is a dictionary (the previous if raises an exception if not), lets proceed and check if both of its entries do
    # have 2 and only 2 key-values and if the keys are what is expected
    # First, get all the keys in the first level of the input dictionary in a nice list:
    key_list = list(auth_dict.keys())

    # And now, for each of these keys, check the level 2 dictionaries for number of elements and formatting of the keys
    for key_elem in key_list:
        # Repeat the validations from before. First check if each entry is indeed a dictionary
        try:
            validate_input_type(auth_dict[key_elem], dict)
        except InputValidationException as ive:
            check_log.error(ive.message)
            raise ive

        # And now check if there are two and only two key-values in each
        if len(auth_dict[key_elem]) != 2:
            error_msg = "The dictionary under the key {0} has a wrong number of elements (not 2): detected dictionary length: {1}".format(str(key_elem), str(len(auth_dict[key_elem])))
            check_log.error(error_msg)
            raise AuthenticationException(message=error_msg, error_code=1)

        # Finally, check if each of the entries(keys) are the 'token' and 'refreshToken' that the API expects
        try:
            auth_dict[key_elem]["token"]
        except KeyError:
            error_msg = "Missing the 'auth_token' key from the dictionary[{0}] - level 2.".format(str(key_elem))
            check_log.error(error_msg)
            raise AuthenticationException(message=error_msg, error_code=1)

        try:
            auth_dict[key_elem]["refreshToken"]
        except KeyError:
            error_msg = "Missing the 'refresh_token' key from the dictionary[{0}] - level 2.".format(str(key_elem))
            check_log.error(error_msg)
            raise AuthenticationException(message=error_msg, error_code=1)

    # If the structure is well formed, return an OK
    return True


# ----------------------------------------------------------------- GENERAL PURPOSE METHODS --------------------------------------------------------------------
def print_dictionary(dictionary, tabs=1):
    """ A method to print out the contents of a dictionary. Useful for debugging since it uses plenty of newlines
    to make the dictionary contents more readable
    @:param dictionary - The dictionary object to print
    @:param tabs - default parameter used to control the tabulation level between recursive calls to this function. Setting it to a value other than 1,
    the default, simply shifts the printed result by those many tabs to the right
    @:return None"""

    print_log = ambi_logger.get_logger(__name__)
    # Quick check for consistency
    try:
        validate_input_type(dictionary, dict)
    except InputValidationException as ive:
        print_log.error(ive.message)
        raise ive

    # Start by getting all the keys in the dictionary in a handy list
    dict_keys = list(dictionary.keys())

    for t in range(0, tabs - 1):
        print("\t", end='')

    print("{")

    for i in range(0, len(dict_keys) - 1):
        # Deal with dictionaries inside of dictionaries in a recursive fashion
        if type(dictionary[dict_keys[i]]) == dict:
            for t in range(0, tabs):
                print("\t", end='')
            print(str(dict_keys[i]) + ": ", end='')
            print_dictionary(dictionary[dict_keys[i]], tabs=tabs + 1)
            continue

        for t in range(0, tabs):
            print("\t", end='')

        print(str(dict_keys[i]) + ": " + str(dictionary[dict_keys[i]]) + ",")

    for t in range(0, tabs):
        print("\t", end='')

    print(str(dict_keys[len(dict_keys) - 1]) + ": " + str(dictionary[dict_keys[len(dict_keys) - 1]]))

    for t in range(0, tabs):
        print("\t", end='')

    print("}")


def build_service_calling_info(auth_token, service_endpoint):
    """ Basic method to automatize the headers and url parts of GET and POST requests. This step is common to all services, therefore it makes sense to abstract
    it. NOTE: This method returns only url and headers information. The 'data' parameter is usually specific to each service and thus needs to be build in
    the service call
    @:param auth_token - a valid authorization token for the service
    @:param endpoint - Service endpoint
    @:return
                {
                    "headers":
                        {
                            "Content-Type" : string,
                            "Accept": string,
                            "X-Authorization": string
                        },
                    "url": string
                }
    """

    # As usual, check the input data first
    build_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(auth_token, str)
        validate_input_type(service_endpoint, str)
    except InputValidationException as ive:
        build_log.error(ive.message)
        raise ive

    # If its all good, return a dictionary with the standard data filled in
    return {
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Authorization": "Bearer " + str(auth_token)
        },
        "url": str(user_config.access_info['host']) + ":" + str(user_config.access_info['port']) + service_endpoint
    }


def validate_input_type(value, valid_type, another_valid_type=None):
    """This method abstracts quite heavily the code to validate input arguments against their expected type. Because python does not impose rigid data types
    as other high level programming languages, I find myself constantly starting each new method with loads of input validations in this sense. To save time
    and typing, those data type validations were abstracted into this method
    @:param value - The value whose type I want to validate
    @:param valid_type (type) - The data type expected in the value argument, i.e., the data type on which value is going to be compared against (E.g. int,
    float, datetime.datetime, custom classes, etc..)
    @:param another_valid_type (type) - In some rare cases, it is possible that a valid argument may be passed under one of two possible valid types (int and
    float are the best example of this case) without it being necessarily invalid. This multi-type validation gets triggered only if another_valid_type !=
    None
    @:raise InputValidationException - If somehow the call for validating inputs also was fed invalid inputs
    @:return True (bool) - If the data type of value matched the type provided
    """
    error_msg = None

    if type(valid_type) != type:
        error_msg = "The validation type ({0}) provided has the wrong data type (not a python's native data type). type(valid_type) = {1}."\
            .format(str(valid_type), str(type(valid_type)))

    if another_valid_type:
        if type(another_valid_type) != type:
            error_msg = "The second validation type ({0}) provided has the wrong data type (not a data type). type(another_valid_type) = {1}."\
                .format(str(another_valid_type), str(type(another_valid_type)))
        else:
            # Deal with the multi-type case here
            if type(value) != valid_type and type(value) != another_valid_type:
                error_msg = "The input provided ({0}) has the wrong data type (not a {1} nor a {2}). type({3}) = {4}."\
                    .format(str(value), str(valid_type), str(another_valid_type), str(value), str(type(value)))

    elif type(value) != valid_type:
        error_msg = "The input provided ({0}) has the wrong data type expected (not a {1}). type({2}) = {3}.".\
            format(str(value), str(valid_type), str(value), str(type(value)))

    # In this point, either one of the previous validation was triggered, which means that error_msg != None, or the data is valid (error_msg = None).

    # If the error message was set
    if error_msg:
        # Raise the custom Exception with it
        raise InputValidationException(error_msg)
    # Otherwise, the data is valid and I'm good to go
    else:
        return True


def extract_all_keys_from_dictionary(input_dictionary, current_key_list, extract_key_logger=None):
    """This method receives a dictionary that can be complex, i.e., some (or even all) of its values maybe other dictionaries. Linear dictionaries i.e., with only one key-value level, are trivial to operate using just the basic functions
    provided by the dict class. But multi-level dictionaries are a new beast in that regard. For example, running a dict.keys() method on a multi-level dictionary yields just the keys in the first level: there's no way to be sure that one
    of those keys doesn't have another dictionary (another level) as its value. To overcome this I need to employ some recursivity in order to explore every level of the dictionary (I need this because the ThingsBoard API loves to return
    data like that: dictionaries inside dictionaries, while the MySQL databases expand those by putting all data into a single level, so at some point I always need a list with all of the dictionary keys, regardless of the level of which
    they were gotten from)
    @:param input_dictionary (dict) - The dictionary whose keys I want to extract
    @:param current_key_list (list of str) - The list of keys so far. Since I'm calling this method recursively, I need to provide the state of the process to the next iteration of the method. The current_key list is going to be use
    for just that.
    @:param extract_key_logger (logging.logger) - The main logger for this method. To avoid having to create a new one every time this method calls itself, I'm setting it by default to None for the first run of the method, so that it can be
    created but only on the first iteration. Subsequent iterations send this object on the recursive call.
    @:return current_key_list (list) - A list with all the keys obtained in this analysis (can be returned for good or sent to another iteration of this method to gather more elements from a deeper level dictionary)
    @:raise utils.InputValidationException - If an input argument fails its data type validation
    @:raise Exception - For any other errors"""

    # Check if the logger exists, i.e., if the current run is the first one or a recursive call
    if not extract_key_logger:
        # If the logger is still None, create it
        extract_key_logger = ambi_logger.get_logger(__name__)
    else:
        # Otherwise, validate its type (the only reason I've been doing this validations inside a try-except clause so far is to capture the exception message before the Exception does its thing. Once I got hold of the Exception message, I
        # can then log it before raising the Exception again to stop the execution of the method. Since I'm expecting this project to be run unattended for long periods of time, having a log file that registers everything that goes wrong
        # with the project's internal logic is quite important, hence the this strategy. But when the input to be validated is the log object itself, catching any potential Exception becomes pointless since I don't have a valid logger that
        # I can use to log the message about what's wrong... with that same logger...)
        validate_input_type(extract_key_logger, logging.Logger)

    # Validate the input dict and the current_key_list then
    try:
        validate_input_type(input_dictionary, dict)
        validate_input_type(current_key_list, list)
    except InputValidationException as ive:
        extract_key_logger.error(ive.message)
        raise ive

    # Extract all the keys of the current level to a temporary list
    current_level_key_list = list(input_dictionary.keys())

    for key in current_level_key_list:
        # Before anything, I need to deal with what may be the most retarded and stupid issue that I've encountered so far... So, the tenant data dictionary that is returned from the remote API has a key named 'additionalInfo'. The problem arises
        # because this element is optional during the construction of a tenant identity in the ThingsBoard interface and, depending on if it gets filled or not, what comes back in HTTP GET response can mess up even the most careful of codes. If
        # the 'additionalInfo' is left blank (which happens 99% of the cases), the result dictionary comes back with that entry as 'additionalInfo': NULL. No problems there since I'm already dealing with the whole NULL-None issue in a separate
        # method. But if there's something written into that field, the dictionary entry becomes 'additionalInfo': {'description': some string}! That is a big mess because now I have a sub-dictionary that can or cannot be returned in the original
        # dictionary! This messes up the MySQL table construction, the data analysis that I've been doing so far and creates a really nasty and hard to find bug in the code... And there's absolutely no reason why this field should come as a
        # sub-dictionary as its value. Why not just set 'additionalInfo': some string? So, instead of writing a elegant function that uses recursivity to extract the key and values from multi-level dictionaries, I now have to "hack" it by
        # inserting "custom" verifications just because the "genius" that conceived the ThingsBoard internal data model found it funny to send back an optional dictionary...
        # Fortunately this issue only occurs when I need to extract the keys from multi-level dictionaries: if a dictionary entry has another dictionary as value, the parent dictionary key is ignored and only the child dictionary keys make it to
        # the final list. A tenant data dictionary with 'additionalInfo': Null extracts the 'additionalInfo' key to the final list but if that key-value comes as 'additionalInfo': {'description': some string}, then the logic ignores the parent and
        # only 'description' goes in the final list. As such, this means that two sets of tenant data, obtained from the same database, can yield different sets of keys in the data dictionaries, which is ridiculous. When I employ this same logic
        # but to extract only the values instead, in this case I either get a 'NULL' that gets translated to None later on or whatever string is in the 'description' key, and thus, this issue gets avoided at all.
        if key == 'additionalInfo':
            # Bypass any further analysis of this entry and force it to use the same string that is currently being used in the database column naming.
            current_key_list.append("description")
            # If a given key of the current level has another dictionary as its value
        elif type(input_dictionary[key]) == dict:
            # Call this function again but with the next level dictionary
            extract_all_keys_from_dictionary(input_dictionary[key], current_key_list, extract_key_logger)
        else:
            # Otherwise, add a new key to the current list
            current_key_list.append(key)

    # Once I'm done either with the whole run or just the current dictionary level, return what I have gathered so far
    return current_key_list


def extract_all_key_value_pairs_from_dictionary(input_dictionary, current_value_dict=None):
    """This method is but the counterpart of the extract_all_keys_from_dictionary one. Same principle, same reason and almost same logic: I need an expanded list of all the values in a given dictionary which, in the considered case,
    can have multiple levels, i.e., values that are dictionaries. The most efficient way to get all values of a dictionary into a linear data type, such as a list, is by employing recursivity to explore all dictionary levels. But in this case,
    the return element is going to be a list of tuples, in the format (key, value), because this method is going to be used to populate database tables where the keys of the input dictionary were used to name the database columns verbatim
    @:param input_dictionary (dict) - The dictionary whose keys values pair I want to extract
    @:param current_value_list (list) - The list of values gathered so far. Since I'm calling this method recursively, I need to provide the state of the process to the next iteration of the method. The current_value_list list is going to be use for
    just that
    @:return current_value_dict (dict) - The dictionary that is going to contain the partial results for when this method is executed recursively
    @:raise utils.InputValidationException - If an input argument fails its data type validation
    """

    if current_value_dict is None:
        current_value_dict = {}

    extract_val_logger = ambi_logger.get_logger(__name__)

    # Validate the input dict and the current_value list then
    try:
        validate_input_type(input_dictionary, dict)
        validate_input_type(current_value_dict, dict)
    except InputValidationException as ive:
        extract_val_logger.error(ive.message)
        raise ive

    # I need to iterate through all keys, so I need them in a list for now (the current level of them anyhow)
    current_level_key_list = list(input_dictionary.keys())

    for key in current_level_key_list:
        # If a sub dictionary is detected
        if type(input_dictionary[key]) == dict:
            # Call this function again with the sub dictionary instead
            extract_all_key_value_pairs_from_dictionary(input_dictionary=input_dictionary[key], current_value_dict=current_value_dict)
        # Otherwise, just keep appending values to the current_value_list
        else:
            current_value_dict[key] = input_dictionary[key]

    # Once the for is done, I'm also too. Send the list back
    return current_value_dict


def translate_postgres_to_python(response_text):
    """This method deals with the idiosyncrasies between the 'things' expected by python against what it is expected from the databases (both MySQL and PostGres) that can potentially cause really annoying bugs. So far,
    I've identified the following potential problems:
    Python used None to denote empty values while the databases use NULL
    Python's booleans are 'True' and 'False' while PostGres uses 'true' and 'false'
    These differences, though subtle, can raise Exceptions. As such, this method receives the response from the API side in str form and used this advantage to use the str.replace(old, new) to correct these problems. Since I have to do this for
    every API interacting method, I might as well right a method about it.
    @:param response_text (str) - The text parameter from the response obtained, as it, from the HTTP request to the remote API
    @:return response (str) - The same response with the offending terms replaced (so that eval and other parsing functions can be used at will)
    @:raise InputValidationException - If the input fails validation
    """
    trans_postgres_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(response_text, str)
    except InputValidationException as ive:
        trans_postgres_log.error(ive.message)
        raise ive

    # The rest is easy
    return response_text.replace('null', 'None').replace('true', 'True').replace('false', 'False')


def translate_mysql_to_python(data_tuple):
    """So, it seems that I also need to take care in converting whatever I read from the MySQL databases into Python-speak too. Interestingly enough, I don't need to worry about the inverse apparently: the mysql.connector already deals with it.
    Given that this module is a python to mysql interface of sorts, it seems only logic that it also concerns itself with the different nomenclatures used between the two platforms. I've been passing Nones, Trues and Falses in SQL strings to be
    executed, by this adapter, in the database side and so far none of these issues have popped up. Also, when checking the data that was inserted in the database through this statements, I can verify that the Nones were properly replaced by NULL
    and so on.
    This method does the translation between MySQL-esque to Python-speak. Given that results from the MySQL databases are obtained through operations with the mysql-python connector, it means that these results are returned in a tuple. Python
    doesn't allow tuple data to be edited, only list data. Fortunately the transition between data types is trivial
    @:param data_tuple (tuple) - A tuple with as many results as the columns in the returned record
    @:return translated_data_tuple(tuple) - The input tuple with all the offending parameters replaced by Python-speak equivalents (NULL -> None, true -> True and false -> False)
    @:raise InputValidationException - if errors appear during the validation of inputs"""

    trans_mysql_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(data_tuple, tuple)
    except InputValidationException as ive:
        trans_mysql_log.error(ive.message)
        raise ive

    # Start by switching to an editable list
    data_list = list(data_tuple)

    for i in range(0, len(data_list)):
        # Standardize the comparisons by casting the element to a string and then switch to lower case. This should take of the cases where a 'NULL' comes as a 'null', 'Null' or any other upper-lower case combination.
        if str(data_list[i]).lower() == 'null':
            data_list[i] = None
        elif str(data_list[i]).lower() == 'true':
            data_list[i] = True
        elif str(data_list[i]).lower() == 'false':
            data_list[i] = False

    # Cast the list back to a tuple when returning it
    return tuple(data_list)


def compare_sets(set1, set2):
    """I needed to create this method to deal with the myriad of problems that I've encountered when comparing datasets from different sources (different databases in this case) while trying to assert their equality. Python does offer some
    powerful tool in that matter (perhaps too powerful given this case) but they turned out to be too 'strict' in some cases, resulting in unexpected False comparisons when the de-facto elements were the same. The problem arises when one of the
    databases decides to return an int number cast as a string while the other sends the same number, from the same record and under the same column, but as an int type instead of a string. In python 123 != '123' and so that is enough to
    invalidate the whole operation. Given the impositions of Python, I reckon that the best approach is to do a item by item comparison with both items cast to str (string) before. This is because a str cast on an string doesn't do anything (as
    expected) but any other data type do has a str 'version'. In other words, every datatype in Python can be cast as a string but not every string can be casted as something else (doing int('123Ricardo456') raises an ValueError Exception)
    @:param set1 (list) - One of the sets of results to be compared
    @:param set2 (list) - The other set to be compared with set1
    @:return True/False (bool) - depending on how the comparison goes. If all elements of set1 are functionally equal to set2 (regardless if they are casted into str or not), return True, otherwise, once a mismatch is detected, return False
    @:raise utils.InputValidationException - If the input sets are not lists"""

    compare_log = ambi_logger.get_logger(__name__)

    try:
        validate_input_type(set1, list)
        validate_input_type(set2, list)
    except InputValidationException as ive:
        compare_log.error(ive.message)
        raise ive

    # It only makes sense to compare the lists if they are, at least, of the same size
    error_msg = None
    if len(set1) <= 0 or len(set2) <= 0:
        error_msg = "One of the sets provided is empty! Set1 size: {0} elements. Set2 size: {1} elements.".format(str(len(set1)), str(len(set2)))
    elif len(set1) != len(set2):
        error_msg = "The sets provided for comparison have different number of elements! Set1: {0} items while Set2: {1} items.".format(str(len(set1)), str(len(set2)))

    if error_msg:
        compare_log.error(error_msg)
        raise InputValidationException(message=error_msg)

    for i in range(0, len(set1)):
        # Cast both elements of the sets to compare to string
        if str(set1[i]) != str(set2[i]):
            # And if a single mismatch is found, finish the method by returning False
            return False

    # If I made it to the end of the for loop, the sets are identical. Return True instead then
    return True


def validate_id(entity_id):
    """This method receives a ThingsBoard issued id and validates it against the expected format, which in this case is a 32 byte string in a 8-4-4-4-12 format, each block denoting how many hexadecimal characters are in there
    @:param entity_id (str) - String element containing the dash '-' separated 32 byte identification string
    @:raise InputValidationException - If the input fails the data type validation
    @:return True (bool) - True if the string provided is in the expected format, otherwise an Exception is raised with the details on why the validation failed"""

    validate_input_type(entity_id, str)

    if len(entity_id) != 36:
        raise InputValidationException(message="Expected a 36 character string (32 bytes of data + 4 separator dashes). Got {0} instead...".format(str(len(entity_id))))

    # Tokenize the element using the '-' as separator and check the number and lenght of each token element
    id_tokens = entity_id.split('-')

    if len(id_tokens) != 5:
        raise InputValidationException(message="Expected 5 dash separated groups. Got {0} instead from {1}...".format(str(len(id_tokens)), str(entity_id)))

    # Check if the 8-4-4-4-12 format is respected
    if len(id_tokens[0]) != 8:
        raise InputValidationException(message="Expected 8 characters in id group 1, got {0} instead from {1}...".format(str(len(id_tokens[0])), str(entity_id)))
    elif len(id_tokens[1]) != 4:
        raise InputValidationException(message="Expected 4 characters in id group 2, got {0} instead from {1}...".format(str(len(id_tokens[1])), str(entity_id)))
    elif len(id_tokens[2]) != 4:
        raise InputValidationException(message="Expected 4 characters in id group 3, got {0} instead from {1}...".format(str(len(id_tokens[2])), str(entity_id)))
    elif len(id_tokens[3]) != 4:
        raise InputValidationException(message="Expected 4 characters in id group 4, got {0} instead from {1}...".format(str(len(id_tokens[3])), str(entity_id)))
    elif len(id_tokens[4]) != 12:
        raise InputValidationException(message="Expected 12 characters in id group 5, got {0} instead from {1}...".format(str(len(id_tokens[4])), str(entity_id)))

    # Finally, check if all characters in the id are hexadecimal ones using a clever Python trick
    # First, go through all the id elements
    for i in range(0, len(id_tokens)):
        try:
            # And try to cast them to an int using an hexadecimal base!
            int(id_tokens[i], 16)
        # If a ValueError exception gets raised, it means that there's a non hex character somewhere in that block! Clever!
        except ValueError:
            # If a non hex block is detected, simply output it to the user, assuming the moron knows what constitutes an hexadecimal character
            raise InputValidationException(message="Detected a non hexadecimal character in the following id block: {0}. All id characters need to be between 0-f!".format(str(id_tokens[i])))

    # Done. If the code reaches this point than it means that the id string was able to jump through all the loops before
    return True


def validate_entity_type(entity_type):
    """
    Use this method to make sure that a provided entity_type is valid, i.e., is among the ones supported by the ThingsBoard, which are specified in proj_config.valid_entity_types
    :param entity_type (str) - The entity type str that needs to be verified.
    :raise utils.InputValidationException - If the input provided doesn't have the expected data type
    :return result (bool) - If the verification is successful, this method returns True. Otherwise an Exception is raised detailing why the verification failed.
    """
    validate_input_type(entity_type, str)

    # All supported entityTypes are all uppercase characters. Convert the argument provided to it before comparing things
    entity_type = entity_type.upper()

    # And check if the entity_type provided is among the supported ones
    if entity_type not in proj_config.valid_entity_types:
        raise InputValidationException(message="The entity type provided: {0} is not among the ones supported by the ThingsBoard platform".format(str(entity_type)))
    else:
        return True