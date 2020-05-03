"""
This is going to be the main repository for configurable elements, such as paths, constants, database access credentials and so on. This file is for only user specific configurations (such as usernames, passwords,
etc.. For project-wide configuration, please use the proj_config.py file
"""
import os

# ---------------- LOCAL INSTALLATION ------------------------------

# thingsboard_host = "http://localhost"
# thingsboard_port = 8080

# ---------------- REMOTE INSTALLATION (Sines's Server) ------------------------------
# The host to use to contact the ThingsBoard API depends heavily on where the process is physically. Due to technical problems that are out of the scope of this project, if this process is running from the same server as the ThingsBoard
# installation, albeit from a different virtual machine, the address to use needs to be an internal one (internal to the physical server that is). Otherwise, the 'official' address needs to be used. In order to automate this decision as much as
# possible, the actual thingsboard_host address depends on the output of the os.getcwd() command. This command retrieves the current working directory (hence the acronym), i.e., the path to the file that was executed that triggered the command's
# execution. I can use this to detect if a 'telltale' element is present in the return string, namely the home folder path in the development server ('/home/uninova')

# NOTE: The access credentials for the local installation are the same as for the remote one, so it should be just a matter of changing the host's endpoints and the whole thing should still work
thingsboard_host = "http://10.0.1.2" if '/home/uninova' in os.getcwd() else "http://62.48.174.118"
thingsboard_port = 5044

local_host = "http://localhost"
local_port = 8080

# Use the following parameters to switch between a local (remote_server = False) and a remote ThingsBoard installations (remote_server = True). Flip the flag accordingly
remote_server = True

# The main access info dictionary for all things accesses
access_info = {
    'host': thingsboard_host if remote_server else local_host,
    'port': thingsboard_port if remote_server else local_port,

    'sys_admin': {
        'username': 'sysadmin@thingsboard.org',
        'password': 'sysadmin'
    },

    'tenant_admin': {
        'username': 'rdlalmeida@gmail.com' if remote_server else 'rdl.almeida@campus.fct.unl.pt',
        'password': 'ambiosensing2019'
    },

    'customer_user': {
        'username': 'rdl.almeida@campus.fct.unl.pt' if remote_server else 'rdlalmeida@gmail.com',
        'password': 'ambiosensing2019'
    },
    'postgres_database': {
        'host': 'localhost',
        'port': 5432,
        'username': 'postgres',
        'password': 'ambiosensing2019'
    },
    'mysql_database': {
        'host': 'localhost',
        'port': 3306,
        'username': 'ambiosensing',
        'password': 'ambiosensing2019',
        'database': 'ambiosensing_thingsboard'
    }
}

# Regular user database credentials
thingsboard_database = {
    "host": "localhost",
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
    'username': 'ricardoalmeida',
    'password': 'ambiosensing2019',
    'host': 'localhost',
    'database': 'ambiosensing_thingsboard'
}

mysql_db_accessUni = {
    'username': 'root',
    'password': 'ambiosensing2019',
    'host': 'localhost',
    'database': 'ambiosensing_bd'
}