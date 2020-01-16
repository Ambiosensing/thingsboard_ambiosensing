from mysql_database.python_database_modules import mysql_device_controller as mdc
from ThingsBoard_REST_API import tb_device_controller as tdc
import utils


def __main__():
    print("Updating customer table...")
    mdc.update_devices_table(customer_name=False)
    print("Done.")


if __name__ == "__main__":
    __main__()