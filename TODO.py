# Use this file to keep items that need processing
# NOTE: I've used a .py file for this purpose because Git provides a basic support for _TODO items management
# TODO 1 - Finish asset_controller interface (tb and mysql sides)
# TODO 2 - Try the device-api-controller.replyToCommand and device-api-controller.subscribeToCommands services to implement a basic actuator interface (turn a relay/LED on/off through the service API interface, for example)
# TODO 3 - The getTimeSeriesKeys can return multiple keys after all! If the device is a multi-sensor one (as its the case right now with the Sines installation), the getTimeSeriesKey returns an array with all the supported timeSeriesKeys. Change
#  this service to prepare it for this scenario
# TODO 4 - How to store the info from _TODO 3? A single database field with a comma-separated string or one field per timeSeriesKey? The first approach is simpler but not elegant at all (though its trivial to prepare the Python end to read a
#  single database field and automatically parse the string into a list/tuple of elements). The second approach functionally makes more sense but since technically there's no limit for how many sensors can be connected to a single device and we need
#  to prepare the database a priori, this approach requires to create a series of uniquely identified columns that are going to be filled with a single timeSeriesKey (timeSeriesKey1, timeSeriesKey2, timeSeriesKey3...). But how many of these should
#  we create? And in the end we need to develop a similar parsing logic from the Python side to deal with this too... choices, choices, choices...
# TODO 5 - There's a difference in some API calls, By some reason, some remote API calls use '{' and '}' in the endpoints and these are returning HTTP 400 - Bad request... check this please
