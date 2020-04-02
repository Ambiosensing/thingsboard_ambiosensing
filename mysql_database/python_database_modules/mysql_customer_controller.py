""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group customer-controller"""

import proj_config
import utils
from mysql_database.python_database_modules import database_table_updater
from ThingsBoard_REST_API import tb_customer_controller
from mysql_database.python_database_modules import mysql_utils


def update_customer_table():
    """Use this method to run an update on the MySQL table where the customer data is aggregated. This method places a call to retrieve the latest customer related data from the remote API and uses the table updater to decide what to do regarding
    the various returned records: insert a new record in the MySQL database, update an existing database record or do nothing (if the existing and returned records are identical)"""

    module_table_key = 'customers'
    limit = 50

    # Grab the data from the remote API
    response = tb_customer_controller.getCustomers(limit=limit)

    # Translate the response text to replace the PostGres-speak returned for Python-speak. And cast that text into a dictionary too
    response_dict = eval(utils.translate_postgres_to_python(response.text))

    # Extract the list of customers from the returned dictionary under the 'data' key
    customer_list = response_dict['data']

    # And process them one by one
    for customer in customer_list:
        # The customer table has an almost one-to-one correspondence between the dictionary keys returned in each customer and the column names in the MySQL database, except for the sub dictionary that is passed under the tenantId key (which as a
        # 'entityType and a id keys and strings as values). In the MySQL database I've condensed that entry into a column named 'tenantId' that should receive just the string under the 'id' key from the current customer dictionary. This means that
        # I should replace this sub dictionary for a 'tenantId': <id_string> at this point or otherwise this process is going to crash later on when it tries to send that data to be added to the customers table
        customer['tenantId'] = customer['tenantId']['id']

        # Remove any multilevel dictionary from the input structure
        customer = utils.extract_all_key_value_pairs_from_dictionary(input_dictionary=customer)

        # And hunt for any datetime fields that are still in the POSIX format
        try:
            # In this particular case, the datetime object comes from the API side as 'createdTime'
            customer['createdTime'] = mysql_utils.convert_timestamp_tb_to_datetime(timestamp=customer['createdTime'])
        except KeyError:
            # If the customer structure doesn't have that key, ignore it.
            pass

        # Send the data to be added to the MySQL database in the customers table
        database_table_updater.add_table_data(data_dict=customer, table_name=proj_config.mysql_db_tables[module_table_key])