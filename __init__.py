from mysql_database.python_database_modules import mysql_auth_controller as mac


def __main__():
    print("Getting new authorization tokens for all users...")
    mac.populate_auth_table()
    print("Done!")


if __name__ == "__main__":
    __main__()
