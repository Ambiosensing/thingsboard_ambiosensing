""" Place holder for methods related to the ThingsBoard REST API - admin-controller methods """
import requests
import ambi_logger
import utils
import ast
from mysql_database.python_database_modules import mysql_auth_controller as mac


# --------------------------------------------------------------------- CUSTOM CLASSES -------------------------------------------------------------------------
class SecuritySettings:
    """ This class encapsulates the dictionary that the POST method to set admin security settings expects
     I've created a simple constructor where a bunch of base values are defined by default"""
    settings = {
        "maxFailedLoginAttempts": 0,
        "passwordPolicy": {
            "minimumDigits": 0,
            "minimumLength": 0,
            "minimumLowercaseLetters": 0,
            "minimumSpecialCharacters": 0,
            "minimumUppercaseLetters": 0,
            "passwordExpirationPeriodDays": 0,
            "passwordReuseFrequencyDays": 0
        },
        "userLockoutNotificationEmail": "string"
    }

    def __init__(self,userLockoutNotificationEmail,
                 maxFailedLoginAttempts=0,
                 minimumDigits=0,
                 minimumLenght=0,
                 minimumLowercaseLetters=0,
                 minimumSpecialCharacters=0,
                 minimumUppercaseLetters=0,
                 passwordExpirationPeriodDays=0,
                 passwordReuseFrequencyDays=0
                 ):
        """ A quick explanation on this constructor method:
         - If it is called without any arguments (e.g. sec_sett = utils.SecuritySettings()), the dictionary 'settings'
         is initialized with the default arguments indicated in the __init__ method signature

         - If it is called with some arguments without specifying them (e.g. sec_sett = utils.SecuritySettings(1, 2, 3)
         the constructor attributes the values passed in the argument list in order to its 'settings' dictionary, i.e,
         maxFailedLoginAttempts = 1,
         passwordPolicy.minimumDigits = 2,
         passwordPolicy.minimumLength = 3 but
         passwordPolicy.minimumLowercaseLetters = 0, as well as the remaining values.
         Thus, the constructor ignores the dictionary structure (which in this particular case has a dictionary inside
         a dictionary), and sets the values as long it has them while the remaining keys are set to their default values.

         - To set specific keys, you need to explicit them in the constructor call.
         E.g., sec_sett = utils.SecuritySettings(minimumDigits=10, minimumUppercaseLetters=12,
         userLockoutNotificationEmail='rdlalmeida@gmail.com') would set the indicated keys to the values passed as
         arguments while the remaining keys are set to their default values
         """

        self.settings["maxFailedLoginAttempts"] = maxFailedLoginAttempts
        self.settings["passwordPolicy"]["minimumDigits"] = minimumDigits
        self.settings["passwordPolicy"]["minimumLength"] = minimumLenght
        self.settings["passwordPolicy"]["minimumLowercaseLetters"] = minimumLowercaseLetters
        self.settings["passwordPolicy"]["minimumSpecialCharacters"] = minimumSpecialCharacters
        self.settings["passwordPolicy"]["minimumUppercaseLetters"] = minimumUppercaseLetters
        self.settings["passwordPolicy"]["passwordExpirationPeriodDays"] = passwordExpirationPeriodDays
        self.settings["passwordPolicy"]["passwordReuseFrequencyDays"] = passwordReuseFrequencyDays
        self.settings["userLockoutNotificationEmail"] = userLockoutNotificationEmail


def getSecuritySettings():
    """ Simple GET method to retrieve the current administration security settings. These can be also consulted in the ThingsBoard Admin dashboard under 'System Settings' -> 'Security Settings'
    @:type user_types allowed for this service: SYS_ADMIN (NOTE: This service is NOT AVAILABLE in the ThingsBoard remote installation at 62.48.174.118)
    @:param auth_token - A valid admin authorization token
    @:return
                {
                    "maxFailedLoginAttempts": 0,
                    "passwordPolicy":
                        {
                            "minimumDigits": 0,
                            "minimumLength": 0,
                            "minimumLowercaseLetters": 0,
                            "minimumSpecialCharacters": 0,
                            "minimumUppercaseLetters": 0,
                            "passwordExpirationPeriodDays": 0,
                            "passwordReuseFrequencyDays": 0
                        },
                    "userLockoutNotificationEmail": "string"
                }
"""
    security_set_log = ambi_logger.get_logger(__name__)

    service_endpoint = "/api/admin/securitySettings"
    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='sys_admin'), service_endpoint)

    response = requests.get(url=service_dict["url"], headers=service_dict["headers"])

    # There's a possibility that a non-admin authorization token can be used at this point. If that's the case, the request will return the appropriate response
    if response.status_code == 403 and ast.literal_eval(response.text)["errorCode"] == 20:
        # Throw the relevant exception if that is the case
        error_msg = "The authorization token provided does not have admin privileges!"
        security_set_log.error(error_msg)
        raise utils.AuthenticationException(message=error_msg, error_code=20)

    return response


def checkUpdates():
    """ GET method to retrieve any available updates to the system
    @:type user_types allowed for this service: SYS_ADMIN
    @:return
                {
                  "message": "string",
                  "updateAvailable": true
                }
    """
    service_endpoint = "/api/admin/updates"

    service_dict = utils.build_service_calling_info(mac.get_auth_token(user_type='sys_admin'), service_endpoint)

    response = requests.get(url=service_dict["url"], headers=service_dict["headers"])

    return response
