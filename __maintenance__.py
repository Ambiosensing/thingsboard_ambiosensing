""" Use this module as a project initializer, namely, as a simple and direct way to populate the auxiliary tables that most of the modules in this project depend on."""
from mysql_database.python_database_modules import mysql_auth_controller
from mysql_database.python_database_modules import mysql_tenant_controller
from mysql_database.python_database_modules import mysql_customer_controller
from mysql_database.python_database_modules import mysql_asset_controller
from mysql_database.python_database_modules import mysql_device_controller


def __main__():
    # First of all, refresh the access tokens by invoking the authentication table refresher
    mysql_auth_controller.populate_auth_table()

    # Start by updating the customer, tenant and asset tables. These are the "fundamental" ones
    mysql_customer_controller.update_customer_table()
    mysql_tenant_controller.update_tenants_table()
    mysql_asset_controller.update_tenant_assets_table()

    # And finish with the device table since this operation requires data from the previous tables
    mysql_device_controller.update_devices_table()


if __name__ == "__main__":
    __main__()
