from mysql_database.python_database_modules import mysql_auth_controller as mac
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.building import Building
from DAOAmbiosensing.space import Space
from DAOAmbiosensing.activation_strategy import Activation_strategy, Strategy_temporal, Strategy_occupation


def __main__():
    dao = DAO_ambiosensing()
    building=Building("EdificioE20")
    index = dao.save_building(building)
    space=Space(name='sala9',area='3',occupation_type='aulas',building=building)
    index=dao.save_space(space)
    profile=Profile(profile_name='perfil7',state=0,space=space)
    id_profile=dao.save_profile(profile)
    #st=Strategy_occupation(name='st1',min=0,max=50)
    st = Strategy_temporal(name='st2',list_weekdays= [1,1,1,1,1,0,0],list_seasons=[1,1,0,0])
    id=dao.save_activationSt_temporal(st,profile)
    print("Done!")


if __name__ == "__main__":
    __main__()
