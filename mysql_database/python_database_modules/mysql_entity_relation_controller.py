""" Place holder for methods related to the interface between the MySQL database (MySQL internal Ambiosensing database) and the data obtained from service calls placed to the API group entity-relation-controller"""


def update_asset_devices_table():
    """Use this method to fill out the asset devices table that corresponds devices to the assets that are related to them. The idea here is to use ASSETs to represent spaces and the ThingsBoard relation property to associate DEVICEs to those
    assets as a way to represent the devices currently installed and monitoring that space
    @:raise mysql_utils.MySQLDatabaseException - For problems related with the database access
    @:raise utils.ServiceEndpointException - For issues related with the remote API call
    @:raise utils.AuthenticationException - For problems related with the authentication credentials used"""

    # TODO: Damn... need to finish the asset module first...