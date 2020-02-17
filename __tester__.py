# TODO: Find a way to find out the ids of the devices in the system by following relationships between entities. I discovered that the getAssetTypes service
#  call might be an interesting entry point given that it lists and returns every registered tenant, along with his id (a rare find given that most services
#  require an id or specific token of some kind to return any meaningful data). Use it to navigate until getting deviceId values via API calls instead of using
#  the ThingsBoard web interface

auth_ctrl = True
ent_rel = False
asset_ctrl = False
mysql_test = False
mysql_device = False


def __main__():
    if asset_ctrl:
        from mysql_database.python_database_modules import mysql_asset_controller as mac

        mac.update_tenant_assets_table()

    if ent_rel:
        from mysql_database.python_database_modules import mysql_entity_relation_controller as erc

        erc.update_asset_devices_table()

    if auth_ctrl:
        from mysql_database.python_database_modules import mysql_auth_controller as mac

        mac.populate_auth_table()

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

        mdc.update_devices_table()


if __name__ == "__main__":
    __main__()
