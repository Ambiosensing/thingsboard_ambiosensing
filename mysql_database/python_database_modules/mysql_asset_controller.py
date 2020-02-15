""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group asset-controller"""

import proj_config
import utils
from ThingsBoard_REST_API import tb_asset_controller
from mysql_database.python_database_modules import database_table_updater


def update_tenant_assets_table():
    """Method to populate the database table with all the ASSETS belonging to a given tenant. I'm still trying to figure out the actual logic behind this call since the API service that I call to retrieve the desired information uses a
    'customer_user' type credential pair but the results returned are related to the Tenant that is associated to Customer identified by those credentials (why not use the 'tenant_admin' credentials instead? Makes more sense in my honest opinion.
    In fact, using those credentials yields a HTTP 403 - access denied - response from the remote server... go figure...) so the relation with a Tenant is tenuous, at best. Anyhow, what matters is that all configured assets in the ThingsBoard
    platform seem to be returned at once by the tb side method, so now its just a matter of putting them into a proper database table
    @:raise mysql_utils.MySQLDatabaseException - For errors with the database operation
    @:raise utils.ServiceEndpointException - For errors with the remote API service execution
    @:raise utils.AuthenticationException - For errors related with the authentication credentials used.
    """

    # Key to return the actual database name from proj_config.mysql_db_tables dictionary
    module_table_key = 'tenant_assets'
    # A generous limit number to retrieve all results in the remote API side
    limit = 50

    # Grab the response from the remote API then
    response = tb_asset_controller.getTenantAssets(limit=limit)

    # Translate the response got and convert it to the expected dictionary
    response_dict = eval(utils.translate_postgres_to_python(response.text))

    # And retrieve the core of the stuff I'm interested into
    asset_list = response_dict['data']

    # Process the returned assets one by one
    for asset in asset_list:
        # Suppress the 'tenantId' sub-dictionary by replacing it by its 'id' parameter with a new key that matches a column name now. A tenantId already implies a TENANT entityType, so the later is redundant and can go out
        asset['tenantId'] = asset['tenantId']['id']

        # The same goes for the CustomerId
        asset['customerId'] = asset['customerId']['id']

        # All set. Invoke the database updater then
        database_table_updater.insert_table_data(asset, proj_config.mysql_db_tables[module_table_key])
