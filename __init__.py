from mysql_database.python_database_modules import mysql_auth_controller as mac
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.building import Building
from DAOAmbiosensing.space import Space


def __main__():
    dao = DAO_ambiosensing()
    building=Building("EdificioE")
    dao.create_building(building)
    space=Space(name='sala1',area='3',occupation_type='aulas',building=building)
    dao.create_space(space)
    l1=dao.select_data_from_table("profile")
    print(l1)
    list = dao.load_profiles()
    for profile in list:
        print(profile.toString())
    profile.profile_name="inverno"
    dao.update_profile(profile)
    print("Done!")


if __name__ == "__main__":
    __main__()
