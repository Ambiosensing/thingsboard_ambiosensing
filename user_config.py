""" This is going to be the main repository for configurable elements, such as paths, constants, database access credentials and so on. This file is for only user specific configurations (such as usernames, passwords,
etc.. For project-widec onfiguration,
please use the proj_config.py file"""

# ---------------- LOCAL INSTALLATION ------------------------------

# thingsboard_host = "http://localhost"
# thingsboard_port = 8080

# ---------------- REMOTE INSTALLATION (Sines's Server) ------------------------------
# NOTE: The access credentials for the local installation are the same as for the remote one, so it should be just a matter of changing the host's endpoints and the whole thing should still work
thingsboard_host = "http://62.48.174.118"
thingsboard_port = 5044

# Use the following parameters to switch between a local (remote_server = False) and a remote ThingsBoard installations (remote_server = True). Flip the flag accordingly
remote_server = False

# The main access info dictionary for all things accesses
access_info = {
    'thingsboard_host': 'http://62.48.174.118' if remote_server else 'http://localhost',
    'thingsboard_port': 5044 if remote_server else 8080,

    'sys_admin': {
        'username': 'sysadmin@thingsboard.org',
        'password': 'sysadmin'
    },

    'tenant_admin': {
        'username': 'rdlalmeida@gmail.com',
        'password': 'ambiosensing2019'
    },

    'customer_user': {
        'username': 'rdl.almeida@campus.fct.unl.pt',
        'password': 'ambiosensing2019'
    },
    'thingsboard_database': {
        'host': 'http://localhost',
        'port': 5432,
        'username': 'postgres',
        'password': 'ambiosensing2019'
    },
    'mysql_database': {
        'host': 'http://localhost',
        'port': 3306,
        'username': 'ambiosensing',
        'password': 'ambiosensing2019',
        'database': 'ambiosensing_thingsboard'
    }
}


# Regular user database credentials
thingsboard_database = {
    "host": "http://localhost",
    "port": 5432,
    "username": "postgres",
    "password": "ambiosensing2019"
}

# # Credentials for the administrator
# sys_admin = {
#     "host": thingsboard_host,
#     "port": thingsboard_port,
#     "username": "sysadmin@thingsboard.org",
#     "password": "sysadmin"
# }
#
# # Credentials for the regular user (a Tenant Administrator one): The password is the same for both Tenant Administrator and Customer user's but the associated e-mail is not
# tenant_admin = {
#     "host": thingsboard_host,
#     "port": thingsboard_port,
#     "username": "rdlalmeida@gmail.com",
#     "password": "ambiosensing2019"
# }
#
# # Credentials for the regular user (the following is for a Customer user)
# customer_user = {
#     "host": thingsboard_host,
#     "port": thingsboard_port,
#     "username": "rdl.almeida@campus.fct.unl.pt",
#     "password": "ambiosensing2019"
# }

# --------------------------------------------- MySQL DATABASE ACCESS CONFIGURATION ----------------------------------------------------------------------------------
# The logic here is: the database name is the key and the corresponding value are the access credentials
mysql_db_access = {
    'username': 'ambiosensing',
    'password': 'ambiosensing2019',
    'host': 'localhost',
    'database': 'ambiosensing_thingsboard'
}
