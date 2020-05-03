""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group entity-relation-controller"""
from mysql_database.python_database_modules import mysql_utils, mysql_asset_controller, mysql_device_controller
from ThingsBoard_REST_API import tb_entity_relation_controller
import ambi_logger
import user_config
import proj_config
import utils


def update_asset_devices_table():
    """Use this method to fill out the asset devices table that corresponds devices to the assets that are related to them. The idea here is to use ASSETs to represent spaces and the ThingsBoard relation property to associate DEVICEs to those
    assets as a way to represent the devices currently installed and monitoring that space
    @:raise mysql_utils.MySQLDatabaseException - For problems related with the database access
    @:raise utils.ServiceEndpointException - For issues related with the remote API call
    @:raise utils.AuthenticationException - For problems related with the authentication credentials used"""

    asset_devices_log = ambi_logger.get_logger(__name__)

    asset_devices_table_name = proj_config.mysql_db_tables['asset_devices']
    assets_table_name = proj_config.mysql_db_tables['tenant_assets']
    devices_table_name = proj_config.mysql_db_tables['devices']

    # Fire up the database access objects
    database_name = user_config.access_info['mysql_database']['database']
    cnx = mysql_utils.connect_db(database_name=database_name)
    outer_select_cursor = cnx.cursor(buffered=True)
    inner_select_cursor = cnx.cursor(buffered=True)

    mysql_utils.reset_table(table_name=asset_devices_table_name)

    # First get a list of all the assets supported so far. Refresh the asset database table first of all
    mysql_asset_controller.update_tenant_assets_table()
    # And the devices table too since I need data from there too later on
    mysql_device_controller.update_devices_table()

    # And grab all assets ids, names and types (I need those for later)
    sql_select = """SELECT id, name, type FROM """ + str(assets_table_name) + """;"""

    # Execute the statement with the select cursor
    outer_select_cursor = mysql_utils.run_sql_statement(cursor=outer_select_cursor, sql_statement=sql_select, data_tuple=())

    # Check if any results came back
    if outer_select_cursor.rowcount <= 0:
        error_msg = "Unable to get any results from {0}.{1} with '{2}'...".format(str(database_name), str(assets_table_name), str(outer_select_cursor.statement))
        asset_devices_log.error(error_msg)
        outer_select_cursor.close()
        inner_select_cursor.close()
        cnx.close()
        raise mysql_utils.MySQLDatabaseException(message=error_msg)

    # Got some results. Process them then
    else:
        # For each valid ASSET Id found in this table, run a query in the ThingsBoard side of things for all DEVICEs that have a relation to that asset and send it to the database
        asset_info = outer_select_cursor.fetchone()

        # Set the common used parameters for the entity-relation call
        entityType = "ASSET"
        relationTypeGroup = "COMMON"
        direction = "FROM"

        # Run this while there are still asset ids to process
        while asset_info:

            # Query for related devices
            api_response = tb_entity_relation_controller.findByQuery(entityType=entityType, entityId=asset_info[0], relationTypeGroup=relationTypeGroup, direction=direction)

            # Get rid of all non-Python terms in the response dictionary and cast it as a list too
            relation_list = eval(utils.translate_postgres_to_python(api_response.text))

            # Now lets format this info accordingly and send it to the database
            for relation in relation_list:
                # Create a dictionary to store all the data to send to the database. For now its easier to manipulate one of these and cast it to a tuple just before executing the statement
                data_dict = {
                    "fromEntityType": relation["from"]["entityType"],
                    "fromId": relation["from"]["id"],
                    "fromName": asset_info[1],
                    "fromType": asset_info[2],
                    "toEntityType": relation["to"]["entityType"],
                    "toId": relation["to"]["id"],
                    "toName": None,
                    "toType": None,
                    "relationType": relation["type"],
                    "relationGroup": relation["typeGroup"],
                }

                # As always, take care with the stupid 'description'/'additionalInfo' issue...
                if relation["additionalInfo"] is not None:
                    try:
                        # Try to get a 'description' from the returned dictionary from the 'additionalInfo' sub dictionary
                        data_dict["description"] = relation["additionalInfo"]["description"]
                    # If the field wasn't set, instead of crashing the code
                    except KeyError:
                        # Simply set this field to None and move on with it...
                        data_dict["description"] = None
                else:
                    data_dict["description"] = None

                # And now to get the data to use in the INSERT statement. For that I need to do a quick SELECT first since I need info from a different side too
                if data_dict['toEntityType'] == 'DEVICE':
                    sql_select = """SELECT name, type FROM """ + str(devices_table_name) + """ WHERE id = %s;"""
                elif data_dict['toEntityType'] == 'ASSET':
                    sql_select = """SELECT name, type FROM """ + str(assets_table_name) + """ WHERE id = %s;"""

                data_tuple = (relation['to']['id'],)

                # NOTE: I need to use the change cursor because my select_cursor still has unprocessed results from the previous SELECT execution and using it would delete those
                inner_select_cursor = mysql_utils.run_sql_statement(cursor=inner_select_cursor, sql_statement=sql_select, data_tuple=data_tuple)

                # Check if any results were returned. Use them if so, otherwise replace the missing results with 'Unknown'. In this case there's no point in raising Exceptions if I can't find the actual name or type of the related device
                if inner_select_cursor.rowcount > 0:
                    # I got the data I was looking for from the devices table
                    result = inner_select_cursor.fetchone()
                    data_dict["toName"] = result[0]
                    data_dict["toType"] = result[1]

                # Write the data in the database table
                mysql_utils.add_data_to_table(table_name=asset_devices_table_name, data_dict=data_dict)

            # Finished with the current asset. Fetch the next one and repeat the cycle if its not None
            asset_info = outer_select_cursor.fetchone()

        # Done with everything, I believe. Close the database access objects and carry on
        outer_select_cursor.close()
        inner_select_cursor.close()
        cnx.close()
