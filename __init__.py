from mysql_database.python_database_modules import mysql_auth_controller as mac
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.building import Building
from DAOAmbiosensing.space import Space


def __main__():
    dao = DAO_ambiosensing()
    l1=dao.select_data_from_table("profile")
    print(l1)
    list = dao.load_profiles()
    for profile in list:
        print(profile.toString())
    print("Done!")


if __name__ == "__main__":
    __main__()
