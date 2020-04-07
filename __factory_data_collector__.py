"""
This method is used to periodically update the environmental data associated to the set of devices that are currently monitoring the surf board factory
"""
import datetime
from mysql_database.python_database_modules import mysql_telemetry_controller


def __main__():
    # Use this parameter to fetch the last hour of data
    collection_interval = datetime.timedelta(hours=1)

    # Set with the device names of all the remote prototypes that are currently monitoring the factory
    device_name_list = [
        'Rasp_00038',
        'Rasp_00039',
        'Rasp_00040',
        'Rasp_00042',
        'Rasp_00043'
    ]

    mysql_telemetry_controller.populate_device_data_table(
        collection_time_limit=collection_interval,
        device_name_list=device_name_list
    )


if __name__ == "__main__":
    __main__()
