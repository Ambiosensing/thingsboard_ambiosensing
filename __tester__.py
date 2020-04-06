auth_ctrl = False
ent_rel = False
asset_ctrl = False
mysql_test = False
mysql_device = False
attr_device = False
rpc_one_way = False
tb_telemetry = True
db_add = False
sql_gen = False
date_converter = False
table_creator = False


def __main__():
    if date_converter:
        from mysql_database.python_database_modules import mysql_utils
        ts1 = 1582147684275
        dt1 = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=ts1)
        print(str(dt1))

    if attr_device:
        from ThingsBoard_REST_API import tb_telemetry_controller as ttc
        import proj_config
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
        import datetime
        device_name = 'Rasp_00040'
        end_time = datetime.datetime(2020, 2, 19, 21, 28, 4)
        time_interval = int(datetime.timedelta(hours=24).total_seconds())

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

    if mysql_test:
        from mysql_database.python_database_modules import mysql_utils
        import _mysql_connector
        table_name = 'tb_tenant_assets'
        database_name = "ambiosensing_thingsboard"

        cnx = mysql_utils.connect_db(database_name)
        change_cursor = cnx.cursor(buffered=True)

        # sql_insert = """INSERT INTO tb_tenant_assets (entityType, id, createdTime, description, tenantId, customerId, name, type) VALUES ('ASSET', 'efa6d2d0-0ad9-11ea-8001-3975f352e04e', '2019-11-19 14:36:13', 'A test building that houses two
        # Thermometer devices', '863ae890-0ad9-11ea-8001-3975f352e04e', '3360f510-0fde-11ea-b852-37722cd69450', 'Building A', 'building');"""

        sql_update = """UPDATE tb_tenant_assets SET entityType = 'ASSET', id = 'efa6d2d0-0ad9-11ea-8001-3975f352e04e', createdTime = '2019-11-19 14:36:13', description = 'A test building that houses two Thermometer devices', tenantId = '863ae890-0ad9-11ea-8001-3975f352e04e', customerId = '3360f510-0fde-11ea-b852-37722cd69450', name = 'Building A', type = 'building';"""

        try:
            change_cursor = mysql_utils.run_sql_statement(cursor=change_cursor, sql_statement=sql_update, data_tuple=())
        except mysql_utils.MySQLDatabaseException as me:
            print("Got a freakin duplicated result: " + me.message)

        print("OK")

    if mysql_device:
        from mysql_database.python_database_modules import mysql_device_controller as mdc

        # mdc.update_devices_table()
        device_name = "Rotating System"
        result = mdc.get_device_credentials(device_name=device_name)

    if table_creator:
        from mysql_database.python_database_modules import mysql_utils
        device_name = "Ambi-05"

        mysql_utils.create_device_database_table(device_name=device_name)


if __name__ == "__main__":
    __main__()
