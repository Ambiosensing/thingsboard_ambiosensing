""" Use this module as a project initializer, namely, as a simple and direct way to populate the auxiliary tables that most of the modules in this project depend on."""
import datetime
from mysql_database.python_database_modules import mysql_auth_controller
from mysql_database.python_database_modules import mysql_tenant_controller
from mysql_database.python_database_modules import mysql_customer_controller
from mysql_database.python_database_modules import mysql_asset_controller
from mysql_database.python_database_modules import mysql_device_controller
from mysql_database.python_database_modules import mysql_telemetry_controller
from mysql_database.python_database_modules import mysql_utils
from mysql_database.python_database_modules import mysql_entity_relation_controller
import proj_config
import user_config
import utils


def __main__():
    # First of all, refresh the access tokens by invoking the authentication table refresher
    mysql_auth_controller.populate_auth_table()

    # Start by updating the customer, tenant and asset tables. These are the "fundamental" ones
    mysql_customer_controller.update_customer_table()
    mysql_tenant_controller.update_tenants_table()
    mysql_asset_controller.update_tenant_assets_table()

    # And finish with the device table since this operation requires data from the previous tables
    mysql_device_controller.update_devices_table()

    mysql_entity_relation_controller.update_asset_devices_table()


def reset_context():
    """
    Use this one to clear all the database table records without destroying them.
    """
    database_table_list = list(proj_config.mysql_db_tables.values())
    database_name = user_config.access_info['mysql_database']['database']

    for table_name in database_table_list:
        print("Deleting records from {0}.{1}...".format(str(database_name), str(table_name)))
        mysql_utils.reset_table(table_name=table_name)
        print("Done!\n")


def gather_latest_data(collection_interval, device_name_list=None):
    """
    This method abstracts the periodic collection of environmental data from all configured devices
    :param collection_interval (datetime.timedelta) - A time window for data collection. Only records with a timestamp between the current datetime and the other end of the time window defined this way are considered
    :param device_name_list (list of str) - Provide a list of device names in this argument if you wish that the data update to be limited to them. Leave it as None to update all devices currently in the tb_devices table.
    :raise utils.InputValidationException - If any inputs fail initial validation
    :raise mysql_utils.MySQLDatabaseException - If any problems are encountered when dealing with the database
    """
    utils.validate_input_type(collection_interval, datetime.timedelta)
    utils.validate_input_type(device_name_list, list)
    for device_name in device_name_list:
        utils.validate_input_type(device_name, str)

    mysql_telemetry_controller.populate_device_data_table(collection_time_limit=collection_interval, device_name_list=device_name_list)


if __name__ == "__main__":
    __main__()
    # reset_context()
    device_name_list = ['Rasp_00038', 'Rasp_00039', 'Rasp_00040', 'Rasp_00042', 'Rasp_00043']
    collection_interval = datetime.timedelta(hours=24)

    gather_latest_data(
        collection_interval=collection_interval,
        device_name_list=device_name_list
    )
