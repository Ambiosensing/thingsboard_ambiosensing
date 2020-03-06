from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing

class Historical_Manager:
    __dao = None

    def __init__(self,connection):
        self.__dao = DAO_ambiosensing().getInstance()


    def get_hist_device_by_date(self, date_ini,date_end):
      #  return hist_device_list avaiable

    def get_all_hist_device_by_date(self, date_ini, date_end):
    #return hist_device_list

    def get_hist_env_variable_by_date(self, date_ini, date_end):

    # return hist_device_list avaiable

    def get_all_hist_env_variable_by_date(self, date_ini, date_end):
    # return hist_device_list