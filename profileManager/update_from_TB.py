import user_config
from mysql_database.python_database_modules import mysql_entity_relation_controller as erc
from mysql_database.python_database_modules import mysql_utils as sql
from DAOAmbiosensing.DAO_ambiosensing import DAO_ambiosensing, Space, Building


def get_update_from_TB():
    #erc.update_asset_devices_table()

    database_name = user_config.mysql_db_access['database']
    cnx = sql.connect_db(database_name=database_name)

    column_list = ['fromID', 'fromName', 'fromType', 'toID', 'toName', 'toType']
    trigger_column_list = ['fromEntityType', 'toEntityType', 'relationType']
    data_tuple = ('ASSET', 'DEVICE', 'Contains')

    # result is a list with the values of the selected columns
    result = __select_data_from_table(cnx, "tb_asset_devices", column_list, trigger_column_list, data_tuple)

    dao_ambi = DAO_ambiosensing()
    # in the future this should come in the result set...
    building = Building('EdificioE', 2)
    #dao_ambi.save_building(building)
    # now is going to populate the space table
    populate_space(dao_ambi, building, result)

    # VOU AQUI
    #for space in building.spaces:
    #    if

print("DONE\n")


def populate_space(dao_ambi, building, result=None):
    if result is None:
        print("Error: Could not populate space table")
        return

    for i in range (len(result)):
        elem = result[i]
        new_space = Space(id_thingsboard=elem[0], name=elem[1], area=-1, occupation_type=elem[2], building=building)
        print('*******************************\n')
        print(new_space.to_string())
        dao_ambi.save_space(new_space)
        building.add_space(new_space)

def populate_device(dao_ambi, space, result=None):
    if result is None:
        print("Error: Could not populate device table")
        return


# sql related methods (to put in a class in the future!!!)
def __select_data_from_table(cnx, table_name, column_list=None, trigger_column_list=None, data_tuple=()):
    #print(table_name, column_list, trigger_column_list)

    if column_list and trigger_column_list is None:
        sql_select = __create_all_sql_statement(table_name)
    else:
        sql_select = __create_value_sql_statement(column_list=column_list, trigger_column_list=trigger_column_list,
                                                  table_name=table_name)

    change_cursor = cnx.cursor(buffered=True)

    result = __run_sql_select_statement(change_cursor, sql_select, data_tuple)
    print(result)
    change_cursor.close()
    return result


def __create_value_sql_statement(table_name, column_list, trigger_column_list):
    sql_select = """SELECT """

    for i in range(0, len(column_list) - 1):
        sql_select += str(column_list[i]) + """, """
    sql_select += str(column_list[len(column_list) - 1]) + """ FROM """ + str(table_name) + """ WHERE """

    for i in range(0, len(trigger_column_list) - 1):
        sql_select += str(trigger_column_list[i]) + """ = %s AND """
    sql_select += str(trigger_column_list[len(trigger_column_list) - 1]) + """ = %s; """

    print(sql_select)
    return sql_select


def __create_all_sql_statement(table_name):
    sql_select = """SELECT * FROM """ + str(table_name) + """;"""
    return sql_select


def __run_sql_select_statement(cursor, sql_statement, data_tuple=()):
    try:
        cursor.execute(sql_statement, data_tuple)
        result = cursor.fetchall()
    except:
        # print("execute error ")
        result = None
    return result
