from mysql_database.python_database_modules import mysql_auth_controller as mac


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

class car:
    matricula = None
    __cor = None
    idade = 0

    def __init__(self, matricula, idade, cor="Branco"):
        self.matricula = matricula
        self.idade = idade
        self.cor = cor

    def start(self):
        print("Started")


class camiao(car):
    pass

if __name__ == "__main__":
    __main__()
