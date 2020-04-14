""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group tenant-controller """

import utils
from mysql_database.python_database_modules import database_table_updater
from mysql_database.python_database_modules import mysql_utils
from ThingsBoard_REST_API import tb_tenant_controller
import proj_config
import ambi_logger


def update_tenants_table():
    """This method is the database version, of sorts, of the tenant_controller functions, namely the getTenants() one. This method uses the later function to get data about the current tenants in the corresponding database table, checks the
     existing tenant data and acts accordingly: new tenants are inserted as a new record in the database, missing tenants are deleted and modified tenants get their records updated. This methods does all this through sub methods that add,
     delete and update tenant records (so that, later on, one does not become restricted to this only method to alter the tenants table. Any of the other, more atomized methods can be used for more precise operation in the database"""

    # Fetch the data from the remote API. Set a high value for the limit argument. If it still are results left to return, this method call prints a warning log about it. Change this value accordingly if that happens
    # The eval command casts the results to the base dictionary returned
    # Get the response object from the API side method

    # The key that I need to use to retrieve the correct table name for where I need to insert the tenant data
    module_table_key = 'tenants'
    limit = 50
    response = tb_tenant_controller.getTenants(limit=limit)
    response_dict = eval(utils.translate_postgres_to_python(response.text))

    # Before processing the results, check if all of them were returned in the last call and warn the user otherwise
    if response_dict['hasNext']:
        # Create the logger first. Since I only needed for this single instance, in this particular case the logger is going to be circumscribed to this little if clause
        update_tenants_log = ambi_logger.get_logger(__name__)
        update_tenants_log.warning("Not all results from the remote API were returned on the last call (limit = {0}). Raise the limit parameter to retrieve more".format(str(limit)))
    # Extract just the part that I'm concerned with
    tenant_list = response_dict['data']

    # Each element in the tenant list is a tenant. Process them one by one then using the insert and update functions. Actually, the way I wrote these functions, you can call either of them since their internal logic decides,
    # based on what's already present in the database, what is the best course of action (INSERT or UPDATE)
    for tenant in tenant_list:
        # Two things that need to be done before sending the data to the database: expand any sub-level in the current tenant dictionary
        tenant = utils.extract_all_key_value_pairs_from_dictionary(input_dictionary=tenant)

        # And replace any POSIX-type timestamps for the MySQL friendly DATETIME type
        try:
            tenant['createdTime'] = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=tenant['createdTime'])
        except KeyError:
            # Ignore if this key doesn't exist in the tenant dictionary
            pass

        database_table_updater.add_table_data(tenant, proj_config.mysql_db_tables[module_table_key])
