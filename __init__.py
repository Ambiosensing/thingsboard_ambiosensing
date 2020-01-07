# TODO: Find a way to find out the ids of the devices in the system by following relationships between entities. I discovered that the getAssetTypes service
#  call might be an interesting entry point given that it lists and returns every registered tenant, along with his id (a rare find given that most services
#  require an id or specific token of some kind to return any meaningful data). Use it to navigate until getting deviceId values via API calls instead of using
#  the ThingsBoard web interface

log_file = False
entity_view = False
tenant = False
db_utils = False
mysql_ten = False
auth = False
tenant_dev = False
devices = True
timeseries = False
database = False
basic_setup = False
customer = False

def __main__():
    if customer:
        from mysql_database.python_database_modules import mysql_customer_controller
        mysql_customer_controller.update_customer_table()

    if basic_setup:
        from mysql_database.python_database_modules import mysql_tenant_controller as mtc
        from mysql_database.python_database_modules import mysql_device_controller as mdc
        mtc.update_tenants_table()
        mdc.update_devices_table()

    if database:
        from mysql_database.python_database_modules import mysql_utils
        import config, utils
        table_key = 'devices'
        device_name = "%"

        cnx = mysql_utils.connect_db(config.mysql_db_access['database'])

        select_cursor = cnx.cursor(buffered=True)

        sql_select = """SELECT entityType, id, timeseriesKey FROM """ + str(config.mysql_db_tables[table_key]) + """ WHERE name LIKE %s;"""

        select_cursor = mysql_utils.run_sql_statement(select_cursor, sql_select, (device_name,))

        result = select_cursor.fetchone()

        while result:
            print(result)
            result = select_cursor.fetchone()

        print("OK")

    if timeseries:
        from ThingsBoard_REST_API import telemetry_controller
        import datetime

        device_name = "Water Meter A1"
        end_time = datetime.datetime(2019, 11, 24, 20, 0, 0)
        start_time = datetime.datetime(2019, 11, 24, 19, 0, 0)
        limit = 10

        data_list = telemetry_controller.getTimeseries(device_name=device_name, end_time=end_time, start_time=start_time, limit=limit)

        print(data_list)

    if devices:
        from mysql_database.python_database_modules import mysql_device_controller
        mysql_device_controller.update_devices_table(customer_name="Thomas Yorke")

    if tenant_dev:
        from ThingsBoard_REST_API import device_controller as dc
        response = dc.getTenantDevices(limit=50)

        print(response.text)

    if auth:
        import utils
        utils.get_auth_token(admin=True)
        utils.get_auth_token(admin=False)

    if mysql_ten:
        from mysql_database.python_database_modules import mysql_tenant_controller as mtc
        from mysql_database.python_database_modules import database_table_updater as dbtu
        import utils, config
        d1 = {
          "id": {
            "entityType": "TENANT",
            "id": "863ae890-0ad9-11ea-8001-3975f352e04e"
          },
          "createdTime": 1574173996441,
          "description": None,
          "country": "Portugal",
          "state": "Setúbal",
          "city": "Caparica",
          "address": "Faculdade de Ciências e Tecnologia - Monte da Caparica",
          "address2": None,
          "zip": "2628",
          "phone": None,
          "email": "rdl.almeida@campus.fct.unl.pt",
          "title": "Mr Ricardo Almeida",
          "region": "Global",
          "name": "Mr Ricardo Almeida"
             }

        print("d1 list of keys: " + str(utils.extract_all_keys_from_dictionary(d1, [])))
        print("d1 list of vals: " + str(utils.extract_all_values_from_dictionary(d1, [])))
        print(dbtu.insert_table_data(d1, config.mysql_db_tables['tenants']))

    if db_utils:
        from mysql_database.python_database_modules import mysql_utils
        import config
        database_name = 'ambiosensing_thingsboard'
        table_key = 'tenants'
        print(mysql_utils.get_table_columns(database_name, config.mysql_db_tables[table_key]))

    if tenant:
        from mysql_database.python_database_modules import mysql_tenant_controller as mtc

        mtc.update_tenants_table()

    if entity_view:
        from ThingsBoard_REST_API import entity_view_controller as evc
        import utils, config
        resp = evc.getEntityViewTypes(utils.get_auth_token(admin=True))
        print("Got a reply from " + str(config.thingsboard_host) + ":" + str(config.thingsboard_port) + ":")
        print(resp.text)

    if log_file:
        import ambi_logger

        my_log = ambi_logger.get_logger(__name__)

        my_log.debug("This is a DEBUG message")
        my_log.info("This is an INFO message")
        my_log.warning("This is a WARNING message")
        my_log.error("This is an ERROR message")
        my_log.critical("This is a CRITICAL message")


__main__()
