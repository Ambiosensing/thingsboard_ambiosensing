/*
This script restores the ambiosensing_thingsboard database.
WARNING: Running this script deletes any data that may exist in a older version of this database - RUN THIS AT YOUR OWN RISK
*/
DROP DATABASE IF EXISTS ambiosensing_thingsboard; -- Delete any instances of this database that may exist in the connected server

/*
Create the database from scratch. NOTE: The CHARACTER SET configuration is a preemptive action against problems integrating the Python mysql adapter and the actual instance of the database. This configuration sets the character
set used to the same set as the Python applications. Using different sets of characters between these two interfaces turns out to be a huge source of problems in my experience...
*/
CREATE DATABASE IF NOT EXISTS ambiosensing_thingsboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ambiosensing_thingsboard;
COMMIT;
