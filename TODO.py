# Use this file to keep items that need processing
# NOTE: I've used a .py file for this purpose because Git provides a basic support for _TODO items management
# DONE_TODO 1 - Finish asset_controller interface (tb and mysql sides)

# DONE_TODO 2 - Try the device-api-controller.replyToCommand and device-api-controller.subscribeToCommands services to implement a basic actuator interface (turn a relay/LED on/off through the service API interface, for example) - Need a prototype
# with
#  some sort of actuator device (relay, LED, etc..) to test this first

# DONE_TODO 3 - The getTimeSeriesKeys can return multiple keys after all! If the device is a multi-sensor one (as its the case right now with the Sines installation), the getTimeSeriesKey returns an array with all the supported timeSeriesKeys. Change
#  this service to prepare it for this scenario - Relevant methods were changed already (need further testing though, just in case)

# DONE_TODO 4 - How to store the info from _TODO 3? A single database field with a comma-separated string or one field per timeSeriesKey? The first approach is simpler but not elegant at all (though its trivial to prepare the Python end to read a
#  single database field and automatically parse the string into a list/tuple of elements). The second approach functionally makes more sense but since technically there's no limit for how many sensors can be connected to a single device and we need
#  to prepare the database a priori, this approach requires to create a series of uniquely identified columns that are going to be filled with a single timeSeriesKey (timeSeriesKey1, timeSeriesKey2, timeSeriesKey3...). But how many of these should
#  we create? And in the end we need to develop a similar parsing logic from the Python side to deal with this too... choices, choices, choices... - Opted for a comma separated string (with no spaces between elements) stored in a single
#  timeSeriesKeys

# TODO 5 - There's a difference in some API calls, By some reason, some remote API calls use '{' and '}' in the endpoints and these are returning HTTP 400 - Bad request... check this please

# DONE_TODO 6 - The auth token management method is not completely OK... The biggest issue is the fact that there are actually 3 types of authorization tokens: SYS_ADMIN, TENANT_ADMIN and CUSTOMER_USER. Each type of authorization token grants
# access to
#  specific sets of services and currently some methods are freaking out on this given the fact that I'm supporting two of these so far. This need to be reviewed ASAP

# DONE_TODO 7 - Move the proj_config.mysql_database_access dictionary to the user_config.py file so that each project contributor can configure this dictionary according to the access credentials to its local installation of the MySQL database -
# Finished.

# DONE_TODO 8 - Create the interface for the auth_controller service category and change the way that the authorization token is processed using the services in this set, which as way more appropriate for this effect has the current strategy. USE THE
#  DAMN database to store the tokens instead of a text file!

# DONE_TODO 9 (big maybe) - Can I create a method that automatically detects which type of token a given remote service requires and changes this also automatically without bothering the user? Tricky but possible I think, just like I like it...
# Challenge
#  accepted!

# TODO 10 - Eventually we need to find a way to store the access credentials (and also pass them to services) in a protected way, i.e., without using plain text strings as of now... Python probably already has some clever way to do this...
#  investigate.

# TODO 11 - Change the log creation to remove the annoying 'ambiosensing_log' missing folder...

# TODO 12 - Deal with the 'NaN' returns...
