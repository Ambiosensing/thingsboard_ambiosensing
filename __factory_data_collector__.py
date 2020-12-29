"""
This method is used to periodically update the environmental data associated to the set of devices that are currently monitoring the surf board factory
"""
import datetime
from mysql_database.python_database_modules import mysql_telemetry_controller
from mysql_database.python_database_modules import mysql_device_controller

def __main__():
    # Use this parameter to fetch the last hour of data
    # collection_interval = datetime.timedelta(hours=5110)
    # collection_interval = datetime.timedelta(minutes=2)
    collection_interval = datetime.timedelta(hours=1)

    #use this parameter to fetch since the beginning
    #collection_interval = datetime.datetime(year=2020, month=5, day=1, hour=0, minute=0, second=0)

    mysql_device_controller.update_devices_table(customer_name=False)

    # Set with the device names of all the remote prototypes that are currently monitoring the factory
    device_name_list = [
        'Raspberry-00038',
        'Raspberry-00039',
        'Raspberry-00040',
        'Raspberry-00041',      # fictitious device (testing new TB instance)
        'Raspberry-00042'
    ]

    mysql_telemetry_controller.populate_device_data_table(
        collection_time_limit=collection_interval,
        device_name_list=device_name_list
    )


"""
def __main__():
    # Use this parameter to fetch the last hour of data
    collection_interval = datetime.timedelta(hours=1)

    #  mysql_device_controller.update_devices_table(False) # use only when new devices are added

    # Set with the device names of all the remote prototypes that are currently monitoring the factory
    device_name_list = [
        # 'Rasp_00038',
        'Rasp_00070'  # devices arts center
    ]

    """
"""
    device_name_list = [
        'Rasp_00038',  # devices factory
        'Rasp_00039',
        'Rasp_00040',
        'Rasp_00042',
        'Rasp_00043',
        'Rasp_00070',  # devices arts center
        'Rasp_00071',
        'Rasp_00072',
        'Rasp_00073',
        'Rasp_00074',
        'Rasp_00075',
        'Rasp_00076',
        'Rasp_00077',
        'Rasp_00078',
        'Rasp_00079',
        'Rasp_00080',
        'Rasp_00081',
        'Rasp_00082',
        'Rasp_00083',
        'Rasp_00084',
        'Rasp_00085',
        'Rasp_00086',
        'Rasp_00087',
        'Rasp_00088',
        'Rasp_00089',
        # 'Rasp_00052',  # actuators arts center
        'Rasp_00053'
        # 'Rasp_00054'
    ]
    """
"""
    mysql_telemetry_controller.populate_device_data_table(
        collection_time_limit=collection_interval,
        device_name_list=device_name_list
    )
"""

"""
        'Rasp_00038',          # devices factory
        'Rasp_00039',
        'Rasp_00040',
        'Rasp_00042',
        'Rasp_00043',
        'Rasp_00055',           # actuator factory
        'Rasp_00070',           # devices arts center
        'Rasp_00071',
        'Rasp_00072',
        'Rasp_00073',
        'Rasp_00074',
        'Rasp_00075',
        'Rasp_00076',
        'Rasp_00077',
        'Rasp_00078',
        'Rasp_00079',
        'Rasp_00080',
        'Rasp_00081',
        'Rasp_00082',
        'Rasp_00083',
        'Rasp_00084',
        'Rasp_00085',
        'Rasp_00086',
        'Rasp_00087',
        'Rasp_00088',
        'Rasp_00089',
        'Rasp_00052',  # actuators arts center
        'Rasp_00053',
        'Rasp_00054'
        """

if __name__ == "__main__":
    __main__()
