import user_config
from DAOAmbiosensing.device import Device
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.schedule import Schedule
from DAOAmbiosensing.space import Space
from DAOAmbiosensing.building import Building
from DAOAmbiosensing.device_configuration import Device_configuration
from DAOAmbiosensing.environmental_variable import Environmental_variable
from DAOAmbiosensing.env_variable_configuration import Env_variable_configuration
from DAOAmbiosensing.activation_strategy import Activation_strategy, Strategy_occupation, Strategy_temporal
import mysql.connector as mysqlc
from mysql_database.python_database_modules.mysql_utils import MySQLDatabaseException

class DAO_ambiosensing:
    cnx=None #connection to database
    def __init__(self):
        database_name = user_config.mysql_db_accessUni['database']
        connection_dict = user_config.mysql_db_accessUni
        try:
            self.cnx = mysqlc.connect(user=connection_dict['username'],
                                 password=connection_dict['password'],
                                 host=connection_dict['host'],
                                 database=connection_dict['database'])
        except:
            print("error connection")


    def __del__(self):
        if self.cnx!=None:
            self.cnx.close()


    def save_profile(self, profile):
        dict_column_list=['profile_name','state','space_id']
        value_list=[profile.profile_name,profile.state,profile.space.id_space]
        index=self.__insert_data_in_table(dict_column_list,value_list,'profile')
        profile.id_profile=index
        return index

    def update_profile(self,profile):
        id = profile.id_profile
        dict_column_list = ['profile_name', 'state', 'space_id']
        value_list = [profile.profile_name,profile.state, profile.space.id_space]
        self.__update_data_in_table(dict_column_list, value_list, 'idprofile',id, 'profile')

    def save_building(self, building):
        dict_column_list = ['name']
        value_list = [building.name]
        index=self.__insert_data_in_table(dict_column_list, value_list, 'building')
        building.id_building=index
        return index

    def save_space(self, space):
        dict_column_list = ['name','area','occupation_type','building_id']
        value_list = [space.name,space.area,space.occupation_type,space.building.id_building]
        index=self.__insert_data_in_table(dict_column_list, value_list, 'space')
        space.id_space=index
        return index

    def __create_activationST(self, strategy,profile):
         dict_column_list = ['name', 'profile_idprofile']
         value_list = [strategy.name, profile.id_profile]
         id = self.__insert_data_in_table(dict_column_list, value_list, 'activation_strategy')
         return id

    def save_activationSt_occupation(self,strategy_occupation,profile):
        id=self.__create_activationST(strategy_occupation,profile)
        dict_column_list = ['min', 'max', 'activation_strategy_id_activation_strategy']
        value_list = [strategy_occupation.min, strategy_occupation.max, id]
        index=self.__insert_data_in_table(dict_column_list, value_list, 'strategy_occupation')
        return index

    def save_activationSt_temporal(self, strategy_temporal, profile):
        id = self.__create_activationST(strategy_temporal, profile)
        dict_column_list = ['monday','tuesday','wednesday','thursday','friday',
                            'saturday','sunday','spring','summer','autumn','winter',
                            'activation_strategy_id_activation_strategy']
        value_list = strategy_temporal.list_weekdays +  strategy_temporal.list_seasons + [id]
        index = self.__insert_data_in_table(dict_column_list, value_list, 'strategy_temporal')
        return index

    def save_schedule(self, schedule, profile):
        dict_column_list = ['start', 'end','profile_idprofile']
        value_list = [schedule.start, schedule.end,profile.id_profile]
        id = self.__insert_data_in_table(dict_column_list, value_list, 'schedule')
        schedule.id=id;#update id with the index returned
        return id

    def save_device_configuration(self, device_configuration,schedule, device):
        dict_column_list = ['state', 'operation_value', 'device_id', 'schedule_idshedule']

        value_list = [device_configuration.state, device_configuration.operation_value,
                      device.id_device,schedule.id]
        id = self.__insert_data_in_table(dict_column_list, value_list, 'device_configuration')
        device_configuration.id = id;  # update id with the index returned
        return id

    def save_env_variable_configuration(self, env_variable_configuration,environmental_variable,schedule):
        dict_column_list = ['min', 'max', 'environmental_variables_id', 'schedule_idshedule']

        value_list = [env_variable_configuration.min,env_variable_configuration.max,
                      environmental_variable.id,schedule.id]
        id = self.__insert_data_in_table(dict_column_list, value_list, 'env_variable_configuration')
        env_variable_configuration.id = id;  # update id with the index returned
        return id



    def remove_profile(self, id_profile):
        # to replace by update/delete to database
        print("removing profile.....")
        print(id_profile)

    def load_device(self, id):
        # to replace by a query to database
        result = self.__select_data_from_table("device", "id", id)
        if len(result) > 0:
            row = result[0]
            device = Device(id=row[0], name=row[1], type=row[2], id_thingsboard=row[3])
            return device
        else:
            return None

    def load_environmental_variable(self, id):
        # to replace by a query to database
        result = self.__select_data_from_table("environmental_variables", "id", id)
        if len(result) > 0:
            row = result[0]
            ev = Environmental_variable(id=row[0], name=row[1], value=row[2], unit_type=row[3])
            return ev
        else:
            return None

    def load_environmental_variable_by_space(self, space):
        # to replace by a query to database
        result = self.__select_data_from_table("environmental_variables", "space_id", space.id_space)
        if len(result) > 0:
            row = result[0]
            ev = Environmental_variable(id=row[0], name=row[1], value=row[2], unit_type=row[3])
            return ev
        else:
            return None

    def load_env_variable_configuration_bySchedule(self,schedule):
        result = self.__select_data_from_table("env_variable_configuration", "schedule_idschedule")
        list = []
        for row in result:
            ev_config = Env_variable_configuration(id=row[0], min=row[1], max=row[2])
            list.append(ev_config)
        return list

    def load_allEnvironmentVariables(self):
        result = self.__select_data_from_table("environmental_variables")
        list = []
        for row in result:
            ev = Environmental_variable(id=row[0], name=row[1], value=row[2], unit_type=row[3])
            list.append(ev)
        return list

    def load_devicesFromSpace(self, space):
        # load all devices from a specific space
        result = self.__select_data_from_table("device", "space_id", space.id_space)
        if len(result) > 0:
            row = result[0]
            device = Device(id=row[0], name=row[1], type=row[2], id_thingsboard=row[3])
            return device
        else:
            return None

    def load_allDevices(self):
        result = self.__select_data_from_table("device")
        list = []
        for row in result:
            device = Device(id_device=row[0], name=row[1], type=row[2], id_thingsboard=row[3])
            list.append(device)
        return list

def load_building(self,id_building):
        result = self.__select_data_from_table("building", "id", id_building)
        if len(result) > 0:
            row = result[0]
            building = Building(id=row[0], name=row[1])
            return building
        else:
            return None

    def load_space(self,id_space):
        result = self.__select_data_from_table("space", "id", id_space)
        if len(result) >0 :
            row= result[0]
            building = self.load_building(row[4])
            space= Space(id_space=row[0],name=row[1],area=row[2],occupation_type=row[3],
                         building=building)
            return space
        else :
            return  None

    def load_profiles(self):
        # to replace by a query to database
        result= self.__select_data_from_table("profile")
        list=[]
        for row in result:
            space = self.load_space(id_space=row[3])
            profile = Profile(id_profile=row[0],profile_name=row[1],state=row[2],space=space)
            list.append(profile)
        return list

    def load_profile(self, id):
        result = self.__select_data_from_table("profile",column='idprofile',value=id)
        if len(result) > 0:
            row=result[0]
            space = self.load_space(id_space=row[3])
            profile = Profile(id_profile=row[0], profile_name=row[1], state=row[2], space=space)
            return profile
        else:
            return None

    def __select_data_from_table(self,table_name,column="",value=""):
        if column == "":
            sql_select = self.__create_all_sql_statement(table_name)
        else:
            sql_select = self.__create_value_sql_statement(value=value, col=column,table_name=table_name)
        change_cursor = self.cnx.cursor(buffered=True)
        result = self.__run_sql_select_statement(change_cursor, sql_select)
        change_cursor.close()
        return result;

    def __insert_data_in_table(self,dict_column_list, value_list, table_name):
        sql_insert = self.__create_insert_sql_statement(dict_column_list, table_name)
        print(sql_insert)
        change_cursor = self.cnx.cursor(buffered=True)
        self.__run_sql_exec_statement(change_cursor, sql_insert, tuple(value_list))
        self.cnx.commit()
        change_cursor.close()
        change_cursor = self.cnx.cursor(buffered=True)
        index=self.__sql_getLastIndex(change_cursor)
        change_cursor.close()
        return index



    def __update_data_in_table(self, dict_column_list, value_list, column,value, table_name):
        sql_update = self.__create_update_sql_statement(column_list=dict_column_list,
                                                      column=column, value=value,table_name=table_name)
        print(sql_update)
        change_cursor = self.cnx.cursor(buffered=True)
        self.__run_sq_exec_statement(change_cursor, sql_update, tuple(value_list))
        self.cnx.commit()
        change_cursor.close()

    def __sql_getLastIndex(self,cursor):
        sql_statement="SELECT last_insert_id();"
        try:
            cursor.execute(sql_statement)
            row = cursor.fetchall()
            index=row[0][0]
        except:
             print("error select last index")
             index=-1
        print('last select index' + str(index))
        return index

        #sql statements creation
    def __create_value_sql_statement(self, col, value, table_name):
        sql_select = """SELECT * FROM """ + str(table_name) + """ WHERE """ + str(col) +"" "= """ +str(value) + """;"""
        return sql_select

    def __create_all_sql_statement(self, table_name):
        sql_select = """SELECT * FROM """ + str(table_name) + """;"""
        return sql_select

    def __create_insert_sql_statement(self,column_list, table_name):
        values_to_replace = []
        for i in range(0, len(column_list)):
            values_to_replace.append('%s')
        sql_insert = """INSERT INTO """ + str(table_name) + """ ("""
        sql_insert += """,""".join(column_list)
        sql_insert += """) VALUES ("""
        sql_insert += """, """.join(values_to_replace)
        sql_insert += """);"""
        return sql_insert

    def __create_update_sql_statement(self, column_list, column, value,table_name):
        sql_update = """UPDATE """ + str(table_name) + """ SET """
        for i in range(len(column_list)-1) :
            sql_update += column_list[i] + """ = %s ,"""
        sql_update += column_list[i+1] + """ = %s """
        sql_update += """ WHERE """ + column + """ = """ + str(value)
        sql_update += """;"""
        return sql_update

    def __run_sql_exec_statement(self,cursor, sql_statement, data_tuple=()):
        try:
            cursor.execute(sql_statement, data_tuple)
        except:
            print("execute error ")
            return 0
        return 1

    def __run_sql_select_statement(self, cursor, sql_statement, data_tuple=()):
       try:
            cursor.execute(sql_statement, data_tuple)
            result = cursor.fetchall()
       except:
            # print("execute error ")
            result = None
       return result

