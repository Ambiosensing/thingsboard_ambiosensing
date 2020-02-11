import user_config
from DAOAmbiosensing.device import Device
from DAOAmbiosensing.profile import Profile
from DAOAmbiosensing.schedule import Schedule
from DAOAmbiosensing.space import Space
from DAOAmbiosensing.building import Building
from DAOAmbiosensing.activation_strategy import Activation_strategy, Strategy_occupation, Strategy_temporal
from mysql_database.python_database_modules import mysql_utils
import mysql.connector as mysqlc
from mysql_database.python_database_modules.mysql_utils import MySQLDatabaseException

class DAO_ambiosensing:

    def connect_db(selfself, database_name):
        connection_dict = user_config.mysql_db_accessUni
        print(connection_dict)
        try:
            cnx = mysqlc.connect(user=connection_dict['username'],
                                 password=connection_dict['password'],
                                 host=connection_dict['host'],
                                 database=connection_dict['database'])
        except :
           print("error connection")
        return cnx

    def load_devices(self):
        # to replace by a query to database
        device = Device(1, 'themometer', 'avac')
        list.append(self, device);
        return list

    def load_device(self, id):
        # to replace by a query to database
        device = Device(id, 'themometer', 'avac')
        return device

    def create_profile(self, profile):
        dict_column_list=['profile_name','state','space_id']
        value_list=[profile.profile_name,profile.state,profile.space.id_space]
        print("profile values")
        print(value_list)
        self.insert_data_in_table(dict_column_list,value_list,'profile')

    def create_building(self, building):
        dict_column_list = ['name']
        value_list = [building.name]
        print("building values")
        print(value_list)
        self.insert_data_in_table(dict_column_list, value_list, 'building')

    def create_space(self, space):
        dict_column_list = ['name','area','ocupation_type','building_id']
        value_list = [space.name,space.area,space.building.id_building]
        print("building values")
        print(value_list)
        self.insert_data_in_table(dict_column_list, value_list, 'space')

    def update_profile(self, profile):
        # to replace by a update to database
        print("updating profile.....")
        print(profile.toString())

    def remove_profile(self, id_profile):
        # to replace by update/delete to database
        print("removing profile.....")
        print(id_profile)

    def load_building(self,id_building):
        result = self.select_data_from_table("building", "id", id_building)
        row = result[0]
        building = Building(id=row[0], name=row[1])
        return building

    def load_space(self,id_space):
        result = self.select_data_from_table("space", "id", id_space)
        row= result[0]
        building = self.load_building(row[4]);
        space= Space(id_space=row[0],name=row[1],area=row[2],ocupation_type=row[3], building=building)
        return space

    def load_profiles(self):
        # to replace by a query to database
        print("load profile list")
        result= self.select_data_from_table("profile")
        list=[]
        for row in result:
            space = self.load_space(id_space=row[3])
            profile = Profile(id_profile=row[0],profile_name=row[1],state=row[2],space=space)
            list.append(profile)
            print(profile.toString())
        return list

    def load_profile(self, id):
        # to replace by a query to database
        profile = Profile(id, 'verao')
        schedule = Schedule(10, 20, self.load_device(1))
        profile.add_schedule(schedule)
        st = Strategy_occupation(1, 5)
        profile.set_activationStrategy(st)
        return profile


    def select_data_from_table(self,table_name,column="",value=""):
        database_name = user_config.mysql_db_accessUni['database']
        print(database_name)
        cnx = self.connect_db(database_name)
        if column == "":
            sql_select = self.create_all_sql_statement(table_name)
        else:
            sql_select = self.create_value_sql_statement(value=value, col=column,table_name=table_name)
        change_cursor = cnx.cursor(buffered=True)
        result = self.run_sql_statement(change_cursor, sql_select)
        cnx.commit()
        change_cursor.close()
        cnx.close()
        return result;



    def insert_data_in_table(self,dict_column_list, value_list, table_name):
        database_name = user_config.mysql_db_accessUni['database']
        print(database_name)
        cnx =self.connect_db(database_name)
        sql_insert = self.create_insert_sql_statement(dict_column_list, table_name)
        print(sql_insert)
        change_cursor = cnx.cursor(buffered=True)
        self.run_sql_statement(change_cursor, sql_insert, tuple(value_list))
        cnx.commit()
        change_cursor.close()
        cnx.close()

    def create_value_sql_statement(self, col, value, table_name):
        sql_select = """SELECT * FROM """ + str(table_name) + """ WHERE """ + col +"" "= """ +value + """;"""
        return sql_select

    def create_all_sql_statement(self, table_name):
        sql_select = """SELECT * FROM """ + str(table_name) + """;"""
        return sql_select

    def create_insert_sql_statement(self,column_list, table_name):
        values_to_replace = []
        for i in range(0, len(column_list)):
            values_to_replace.append('%s')

        sql_insert = """INSERT INTO """ + str(table_name) + """ ("""
        sql_insert += """,""".join(column_list)
        sql_insert += """) VALUES ("""
        sql_insert += """, """.join(values_to_replace)
        sql_insert += """);"""
        return sql_insert

    def run_sql_statement(self,cursor, sql_statement, data_tuple=()):
        print(data_tuple)
        try:

            cursor.execute(sql_statement, data_tuple)
            result=cursor.fetchall()
        except:
            print("execute error ")
            result=None
        return result
