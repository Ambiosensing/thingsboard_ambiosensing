/*
NOTE: To be able to execute this script you must be connected to the database server using a role that allows the creation of new users (root is a nice default option)
*/
CREATE USER 'ambiosensing'@'localhost' IDENTIFIED BY 'ambiosensing2019'; -- 'ambiosensing2019' being user ambiosensing's password
GRANT ALL PRIVILEGES ON *.* TO 'ambiosensing'@'localhost'; -- Gives full access permissions to user 'ambiosensing' in server 'localhost'. For more narrow privileges, replace the first '*' on '*.*' for a specific database to limit the user's privileges to all tables of that database only and replace the second '*' to narrow the scope of these privileges further to just a table in the database