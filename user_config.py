""" This is going to be the main repository for configurable elements, such as paths, constants, database access credentials and so on. This file is for only user specific configurations (such as usernames, passwords,
etc.. For project-widec onfiguration,
please use the proj_config.py file"""

# ---------------- LOCAL INSTALLATION ------------------------------

thingsboard_host = "http://localhost"
thingsboard_port = 8080

# ---------------- REMOTE INSTALLATION (Sines's Server) ------------------------------
# NOTE: The access credentials for the local installation are the same as for the remote one, so it should be just a matter of changing the host's endpoints and the whole thing should still work
# thingsboard_host = "http://62.48.174.118"
# thingsboard_port = 5044


# Regular user database credentials
database = {
    "host": "http://localhost",
    "port": 5432,
    "username": "postgres",
    "password": "ambiosensing2019"
}

# Credentials for the administrator
thingsboard_admin = {
    "host": thingsboard_host,
    "port": thingsboard_port,
    "username": "sysadmin@thingsboard.org",
    "password": "sysadmin"
}

# Credentials for the regular user
thingsboard_regular = {
    "host": thingsboard_host,
    "port": thingsboard_port,
    "username": "rdl.almeida@campus.fct.unl.pt",
    "password": "ambiosensing2019"
}