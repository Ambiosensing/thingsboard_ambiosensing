""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group device-controller"""

import ambi_logger
import proj_config
import utils
from mysql_database.python_database_modules import database_table_updater
from ThingsBoard_REST_API import tb_device_controller
from ThingsBoard_REST_API import tb_telemetry_controller


def update_devices_table(customer_name=False):
    """The logic behind this module is quite similar to the one employed in the update_tenant_table(): it gets a similar data structure in (with all the same annoying problems), has to do the same kind of processing and so on. As with the other
    method, I'm going to write a insert and an update methods that can call each other depending on the context: both methods detect what is going on in the database and then act accordingly.
    @:param customer_name (str) - OPTIONAL parameter. There are essentially multiple ways to retrieve device dictionary data from the remote API. So far, I've created support for retrieving device data from the getTenantsDevices method,
    using just tenants data, and the getCustomerDevices, using customer data instead. Overall, the data returned comes in the same format in both cases, hence why I want to use just one method to process the device data. The difference is,
    using tenant data only retrieves devices that are associated to a tenant, as well as using customer data only returns devices associated to a customer. So, ideally, I should use both methods and merge the resulting list before running the
    table_updater method. The problem is that the customer based method requires a customer_id that is retrieved using a more memorable customer_name (and also because I've implemented a more flexible way to retrieve this data when the complete
    customer_name is not completely known), so I can only get the additional result sets if the customer_name is passed on to this method. So, if this argument is omitted, this method uses just the tenant data. If not, both data sets are retrieved.
    @:raise utils.InputValidationException - If the inputs fail validation
    @:raise Exception - If other errors occur.
    """
    module_table_key = 'devices'
    # Use the same limit value for both calls
    limit = 50
    update_devices_log = ambi_logger.get_logger(__name__)

    # Get the base response using just tenant data
    tenant_response = tb_device_controller.getTenantDevices(limit=limit)

    # Translate the stuff that comes from the ThingsBoard API as PostGres-speak to Python-speak before forwarding the data
    tenant_response_dict = eval(utils.translate_postgres_to_python(tenant_response.text))

    # Test if all results came back with the current limit setting
    if tenant_response_dict['hasNext']:
        update_devices_log.warning("Not all results from the remote API were returned on the last call using tenant data (limit = {0}). Raise the limit parameter to retrieve more of them.".format(str(limit)))

    # Extract the device data to a list
    tenant_device_list = tenant_response_dict['data']

    customer_device_list = None
    # Check if its possible to use the customer data too to retrieve customer associated devices
    if customer_name:
        # Validate it first
        try:
            utils.validate_input_type(customer_name, str)
        except utils.InputValidationException as ive:
            update_devices_log.error(ive.message)
            raise ive

        # Input validated. Proceed to query the API using the same limit
        customer_response = tb_device_controller.getCustomerDevices(customer_name=customer_name, limit=limit)

        # Translate it to Python and cast the response to a dictionary
        customer_response_dict = eval(utils.translate_postgres_to_python(customer_response.text))

        # Test if the customer bound results were truncated by the limit value
        if customer_response_dict['hasNext']:
            update_devices_log.warning("Not all results from the remote API were returned on the last call using customer data (limit = {0}). Raise the limit parameter to retrieve more of them.".format(str(limit)))

        # Extract the records into a list
        customer_device_list = customer_response_dict['data']

    # And then try to add it, one by one, to the database table. The lazy way to do this is to add records indiscriminately to the database and let it, along with the database_table_updater module that is called to do just that,
    # to sort through possible repeated records (devices can be associated to customers and to tenants simultaneously) with their internal tools. But fortunately I've detected that both device data retrieval methods use the exact same data
    # structure to format these results, hence a quick comparison should be enough to be able to collate a list with only one record per device in it

    # Start by picking the tenant device list as the default
    device_list = tenant_device_list

    # If another list was retrieved from the customer data too
    if customer_device_list:
        # Go through all the customer associated devices
        for customer_device in customer_device_list:
            # And if a record is deemed repeated
            if customer_device in device_list:
                # Ignore it and move to the next one in line
                continue
            # Otherwise
            else:
                # Add it to the main list
                device_list.append(customer_device)

    # The rest of the code should work with either just a tenant based device list or one with also customer based devices
    for device in device_list:
        # Unlike the tenant processing method, the devices data has a couple of redundant fields that I decide to remove for sake of simplicity. Namely, the result dictionary for each device entry returns two keys: tenantId and CustomerId which
        # are sub-dictionaries with the format {'entityType': string, 'id': string}. I'm only interested in the id field (because I can use it later to do JOIN statements using the id field and main correlation). The entityType associated value
        # for those case is 'TENANT' and 'CUSTOMER', which is a bit redundant given that it is already implicit in the parent key. As such, I decided to create database columns named respectively tenantId and customerId but are set to VARCHAR type
        # to store just the id string. So, for this to work later on I need to replace these sub-dictionaries by just the id strings. Otherwise the list of values is not going to match the number of database columns
        device['tenantId'] = device['tenantId']['id']
        device['customerId'] = device['customerId']['id']

        # I still have one more customization to do in this service. Subsequent calls for device data from the ThingsBoard remote API require 5 specific and mandatory elements: the entityType, entityId, timeseriesKey,
        # startTimestamp and endTimestamp. The first 2 are covered by the device_controller.getTenantDevices method and the last 2 are set by the user (not method dependent). So I'm only missing the timeseriesKey at this point to be able to do
        # bulk requests for device data. To obtain that, I need to place a specific call to a remote API service, namely the telemetry_controller.getTimeseriesKey method. This method requires the device's entityKey and entityId that were just
        # returned from the previous API call. This method, if correctly call, returns a single string with the name that the PostGres database from the API side is using to store the device data. It is not optimal to create a single table with
        # just a column with this data (or even with two additional entityType and entityId) when I can simply add a new one to the existing thingsboard_devices_table and place a call at this point to the other API service that returns just that
        # and concatenate it to the existing data dictionary. The thingsboard_devices_table already has an 'extra' column names timeseriesKey at the end to include this element so now its just a matter of putting it into the dictionary to return.
        # Humm... it seems that there are sensors that can provide readings from multiple sources (the device can be a multi-sensor array that uses a single interface to communicate
        # The return from the next statement is always a list with as many elements as the number of supported timeSeriesKeys by the device identified (one per supported reading/sensor)
        timeseries_keys = tb_telemetry_controller.getTimeseriesKeys(device['id']['entityType'], device['id']['id'])

        # The database entry needs to contain all elements returned in the list in timeseries_keys variable
        # Add an extra entry to the device dictionary to be used on the database population operation. The str.join() operation is going to concatenate all elements in the timeseries_keys using a comma to separate them in a single string.
        # Also, this approach has the advantage that if an API request is built from this data (retrieved from the database of course), this format allows for a direct call - no post processing required at all. This is because of how these types
        # of remote API requests are constructed: the endpoint request takes a query for multiple timeseries keys from one single device as comma-separated strings with no spaces.
        # For example, querying for the timeseries values from a device with 4 sensors attached that can produce 4 types of different readings implies the following endpoint to be sent in a URL to the remote service:
        # http://localhost:8080/api/plugins/telemetry/DEVICE/3f0e8760-3874-11ea-8da5-2fbefd4cb87e/values/timeseries?limit=3&agg=NONE&keys=humidity,temperature,pressure,lux&startTs=1579189110790&endTs=1579193100786
        # The 'keys' part of the last string shows how this request must be constructed and that implies all parameters in a single string, separated by commas and without any spaces in between.
        device['timeseriesKeys'] = ",".join(timeseries_keys)
        # Done. Carry on with the database stuff
        database_table_updater.insert_table_data(device, proj_config.mysql_db_tables[module_table_key])
