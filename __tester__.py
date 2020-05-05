auth_ctrl = False
ent_rel = False
asset_ctrl = False
mysql_device = False
attr_device = False
rpc_one_way = False
tb_telemetry = False
db_add = False
sql_gen = False
date_converter = False
table_creator = False
device_types = True
asset_info = False
device_data = False


def __main__():
    if device_data:
        from mysql_database.python_database_modules import mysql_asset_controller as mac
        import datetime
        import json

        base_date = datetime.datetime(2020, 4, 28, 20, 0, 0)
        time_interval = datetime.timedelta(hours=6)
        variable_list = ['carbon_dioxide', 'temperature', 'chocolate']
        asset_name = 'TheFactory_SandingRoom'
        asset_id = '77f3b910-685d-11ea-971a-c108b8f2be6f'

        results = mac.get_asset_env_data(base_date=base_date, time_interval=time_interval, variable_list=variable_list, asset_name=asset_name, asset_id=asset_id)

        print(json.dumps(results))

    if asset_info:
        from mysql_database.python_database_modules import mysql_asset_controller as mac
        valid_name = 'TheFactory_CommonAreas'
        valid_id = 'e76a6be0-685d-11ea-971a-c108b8f2be6f'

        invalid_name = 'TheFactory_Graveyard'
        invalid_id = 'e76a6be0-685d-11ea-971a-c108b8f2be6e'

        db_name = mac.retrieve_asset_name(asset_id=valid_id)
        print("Valid name: {0}, retrieved db name: {1}".format(str(valid_name), str(db_name)))

        db_id = mac.retrieve_asset_id(asset_name=valid_name)
        print("Valid id = {0}\nID from db = {1}".format(str(valid_id), str(db_id)))

        db_name = mac.retrieve_asset_name(asset_id=invalid_id)
        print("Invalid name: {0}, retrieved db name: {1}".format(str(invalid_name), str(db_name)))

        db_id = mac.retrieve_asset_id(asset_name=invalid_name)
        print("Invalid_id: {0}, Id retrieved from invalid name: {1}".format(str(invalid_id), str(db_id)))

    if device_types:
        from mysql_database.python_database_modules import mysql_device_controller as mdc

        result = mdc.get_device_types()

        print(str(result))

    if date_converter:
        from mysql_database.python_database_modules import mysql_utils
        ts1 = 1582147684275
        dt1 = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=ts1)
        print(str(dt1))

    if attr_device:
        from ThingsBoard_REST_API import tb_telemetry_controller as ttc
        device_name = "Multi-sensor device"

        resp = ttc.getAttributes(deviceName=device_name)

        print(str(resp))

    if db_add:
        from mysql_database.python_database_modules import database_table_updater as dtu

        dtu.add_table_data(data_dict={}, table_name="tb_asset_devices")

    if sql_gen:
        from mysql_database.python_database_modules import mysql_utils
        import user_config

        table_name = 'tb_authentication'
        database_name = user_config.access_info['mysql_database']['database']
        trigger_column_list = ['token_timestamp', 'refreshToken_timestamp']
        column_list = mysql_utils.get_table_columns(database_name=database_name, table_name=table_name)

        sql_insert = mysql_utils.create_insert_sql_statement(column_list=column_list, table_name=table_name)
        sql_update = mysql_utils.create_update_sql_statement(column_list=column_list, table_name=table_name, trigger_column_list=trigger_column_list)
        sql_delete = mysql_utils.create_delete_sql_statement(trigger_column_list=trigger_column_list, table_name=table_name)

        print(sql_insert)
        print(sql_update)
        print(sql_delete)

    if tb_telemetry:
        from ThingsBoard_REST_API import tb_telemetry_controller as ttc
        device_name = 'Rasp_00040'
        # end_time = datetime.datetime(2020, 2, 19, 21, 28, 4)
        # time_interval = int(datetime.timedelta(hours=24).total_seconds())

        # result = ttc.getTimeseries(device_name=device_name, end_time=end_time, time_interval=time_interval)
        result = ttc.getLatestTimeseries(device_name=device_name)

        print(str(result))

    if asset_ctrl:
        from mysql_database.python_database_modules import mysql_asset_controller as mac

        mac.update_tenant_assets_table()

    if ent_rel:
        from mysql_database.python_database_modules import mysql_entity_relation_controller as erc

        erc.update_asset_devices_table()

    if auth_ctrl:
        from mysql_database.python_database_modules import mysql_auth_controller as mac

        mac.populate_auth_table()
        # mac.get_auth_token("tenant_admin")

    if rpc_one_way:
        from ThingsBoard_REST_API import tb_rpc_controller as trc
        method = "setRelayMode"
        param_dict = {"relay": 2, "value": False}
        deviceId = "9e35beb0-54a9-11ea-baa1-bd1d876ee3ed"

        # response = trc.handleOneWayDeviceRPCRequests(deviceId=deviceId, remote_method=method, param_dict=param_dict)
        response = trc.handleTwoWayDeviceRPCRequest(deviceId=deviceId, remote_method=method, param_dict=param_dict)
        print("RPC command returned HTTP " + str(response))

    if mysql_device:
        from mysql_database.python_database_modules import mysql_device_controller as mdc

        # mdc.update_devices_table()
        device_name = "Rotating System"
        result = mdc.get_device_credentials(device_name=device_name)

        print(str(result))

    if table_creator:
        from mysql_database.python_database_modules import mysql_utils
        device_name = "Ambi-05"

        mysql_utils.create_device_database_table(device_name=device_name)


if __name__ == "__main__":
    __main__()
