# TODO: Find a way to find out the ids of the devices in the system by following relationships between entities. I discovered that the getAssetTypes service
#  call might be an interesting entry point given that it lists and returns every registered tenant, along with his id (a rare find given that most services
#  require an id or specific token of some kind to return any meaningful data). Use it to navigate until getting deviceId values via API calls instead of using
#  the ThingsBoard web interface

auth_ctrl = True


def __main__():
    if auth_ctrl:
        from mysql_database.python_database_modules import mysql_auth_controller as mac

        mac.populate_auth_table()


if __name__ == "__main__":
    __main__()
