from mysql_database.python_database_modules import mysql_auth_controller as mac
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.profile import Profile


def __main__():
    print("Getting new authorization tokens for all users...")
    #mac.populate_auth_table()
    building = Building(name="patio",id_building=4)
    space = Space("sala1",53,"aulas", building)
    profile = Profile("verao",)
    dao = DAO_ambiosensing()
    #dao.create_building(building)
    #dao.create_space(space)
    print("Done!")



if __name__ == "__main__":
    __main__()
