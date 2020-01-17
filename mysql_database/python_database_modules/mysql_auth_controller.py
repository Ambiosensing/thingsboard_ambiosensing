""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group auth-controller, as well as the authorization token
management methods"""

# TODO - Create a get_all_auth_tokens method that reads the access dictionary in the user_config.access_info and populates the proper database table accordingly
# TODO - Create a database table to store the provided authorization tokens, as well as the information associated to it (user type, access type, etc..)
# TODO - Create a refresh tokens method that can be set to run automatically through an independent process/thread or called upon when needed to get valid tokens
