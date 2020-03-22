CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.Ambi_05_data
(
	timestamp			DATETIME DEFAULT NULL NULL,
	test_temperature			DOUBLE DEFAULT NULL NULL,
	windDirection			DOUBLE DEFAULT NULL NULL,
	CONSTRAINT Ambi_05_data_pk UNIQUE (timestamp)
)
COMMENT 'This script was automatically created using mysql_database.python_database_modules.mysql_utils.device_database_table_script_generator method';
COMMIT;