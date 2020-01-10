"""Base module to obtain logging.Logger objects. All the necessary configurations are abstracted in the methods in this file"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import proj_config
import utils
import os


def get_console_handler():
    """The logger module can output its info either into a file or as a stream of data to a console. This method adds the necessary handler to divert the
    log output to a system console to a Logger object
    @:return console_handler (logging.StreamHandler) - An object pointing the data stream to the system's console (sys.stdout)
    """

    # Get an instance of the class and point it to the standard output channel (console)
    console_handler = logging.StreamHandler(sys.stdout)
    # And force the data to be formatted according to the rules in the string FORMATTER (in the config file)
    console_handler.setFormatter(proj_config.LOG_FORMATTER)

    return console_handler


def get_file_handler(file_location=None):
    """This method is analogous to the previous but this one sends the logging data towards the file indicated in the file_location argument or,
    in case this is not supplied, the path defined in the LOG_FILE_LOCATION in the config file. A file handler is smart enough to deal with various file
    handlers simultaneously, as long as they are created locally in the methods that need to call them, as well as to detect if a log file already exists or
    not. If it does, the file_handler picks it up and starts appending from its end. Otherwise it creates the log file if doesn't exists.
    @:param file_location (str) - A valid system path, including the log file name, where these logs should be written to
    @:return file_handler (logging.handlers.TimedRotatingFileHandler) - Sends a file handler of the type TimedRotatingFileHandler that, as the name implies,
    rotates around a specific time indicated in its properties.
    @:raise FileNotFoundError - If the file location provided has problems (missing directories and/or files)
    """
    if file_location:
        file_handler = TimedRotatingFileHandler(file_location, when="midnight", interval=1, backupCount=5)
    else:
        file_handler = TimedRotatingFileHandler(proj_config.LOG_FILE_LOCATION, when="midnight", interval=1, backupCount=5)

    # Set the standard format to the log messages
    file_handler.setFormatter(proj_config.LOG_FORMATTER)

    return file_handler


def get_logger(logger_name, file_location=None):
    """This method aggregates the get_console_handler() and the get_file_handler() methods to return a complete logger that, once invoked, sends the log
    messages both to the stdout and the defined log file, with the format defined in the string FORMATTER. NOTE: By providing a new name to this function,
    a new logger object is returned. If the name corresponds to an already existing logger object in memory, its handler is returned instead.
    @:param logger_name (str) - A name that is going to be associated with logger object (different from the variable that holds the object)
    @:param file_location (optional str) - A valid system path, including the log file name, where these logs should be written to
    @:raise util.InputValidationException - If there's a problem with the input arguments
    @:return logging.Logger - The Logger object if the operation was successful
    """

    try:
        utils.validate_input_type(logger_name, str)
        if file_location:
            # First validate the file location against it most basic data type
            utils.validate_input_type(file_location, str)
            # Then check if the path in question is a valid one too
            try:
                # Try to open the file indicated in the file location argument. If there's something wrong with it, catch the expected exception
                temp_f = open(file_location)
                # Close the file if nothing wrong happens when trying to open it
                temp_f.close()
            except FileNotFoundError as fnf:
                print("The file location provided ({0}) is not correct!".format(str(file_location)))
                raise fnf
    except utils.InputValidationException as ive:
        # At this level, there isn't much I can do about this... send the Exception to the caller
        raise ive

    # Get a basic, un-configured Logger object first
    logger = logging.getLogger(logger_name)

    # Set the logger level to a low one. These loggers operate on six possible logging.Levels that have a numeric value associated, namely:
    # NOTSET (0)
    # DEBUG (10)
    # INFO (20)
    # WARN (30)
    # ERROR (40)
    # CRITICAL (50)
    # The numeric value is just a shorthand for the name of the level itself (setting setLevel(logging.DEBUG) or setLevel(10) is the same thing
    # The way this works is, the base level determines what gets logged or not, based on the log level of the message. Setting this logger to DEBUG level
    # means that all messages with the same level or above are logged but not the ones with lower levels. In this case, a logger.error(message) logs the
    # message because it is logged with a ERROR (40) level but not a NOTSET leveled message.
    logger.setLevel(logging.DEBUG)

    # Add the handlers to the base logger. But before, since this function is going to be repeatedly called along this project, sometimes (depending on the module structure and where exactly the logger is called from)
    # an existing logger is returned instead of a 'fresh' one. This means that it already has some handlers associated to it (assuming it was initially generated from this same module using the get_logger() method that
    # also associates a file and stream handler to it) and then it gets a new pair every time a logger is created upon an existing one. The result? Every time a logger logs anything (on the console or/and on the log file)
    # it prints the same line for every repeated handler that it has. That when you start seeing multiple repetitions of the same log line, down to the timestamp, on the console and file. The next couple of instructions
    # simplify the logger creation by wiping out any existing handlers before adding the only two ones needed
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(file_location))

    # The logger is now configured and ready to work. Return it
    return logger

