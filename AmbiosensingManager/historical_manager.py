from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing
from DAOAmbiosensing.device_history import DeviceHistory
from DAOAmbiosensing.profile_history import ProfileHistory
import datetime

class Historical_Manager:
    dao = None

    def __init__(self,connection):
        self.dao = DAO_ambiosensing().getInstance()

    #  return hist_device_list avaiable from a time period
    def get_hist_device_by_date(self, start_date, end_date):
      list_avai=[]
      list=self.dao.load_device_history(self, start_date, end_date)
      for hist in list:
          if hist.avaiability_state==True :
             list_avai.append(hist)
      return list_avai

      #  return all hist_device_list from a time period

    def get_all_hist_device_by_date(self, start_date, end_date):
        list = self.dao.load_device_history(self, start_date, end_date)
        return list

    #  return all hist_profile_list from a time period
    def get_all_hist_profile_by_date(self, start_date, end_date):
        list = self.dao.load_profile_history(self, start_date, end_date)
        return list

    #  return all hist_profile_list from a time period

    def profile_to_historical(self, profile):
        profile_hist= ProfileHistory(datetime=datetime.datetime.now(), id_profile=profile.id_profile)
        self.dao.save_profileHistory(profile_hist)

    def device_to_historical(self, device,operation_state):
        device_hist = DeviceHistory(datetime=datetime.datetime.now(), id_thingsboard=device.id_thingsboard,
                                    operation_state=operation_state,avaiability_state=True )
        self.dao.save_profileHistory(device_hist)