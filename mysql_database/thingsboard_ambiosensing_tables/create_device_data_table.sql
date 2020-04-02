DROP TABLE IF exists ambiosensing_thingsboard.tb_device_data;

CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.tb_device_data(
    ontologyId                  VARCHAR(100)    DEFAULT NULL NULL,
    timeseriesKey               VARCHAR(100)    DEFAULT NULL NULL,
    timestamp                   DATETIME        DEFAULT NULL NULL,
    value                       DOUBLE          DEFAULT 0.0 NULL,
    deviceName                  VARCHAR(150)    DEFAULT NULL NULL,
    deviceType                  VARCHAR(100)    DEFAULT NULL NULL,
    deviceId                    VARCHAR(100)    DEFAULT NULL NULL,
    tenantId                    VARCHAR(100)    DEFAULT NULL NULL,
    customerId                  VARCHAR(100)    DEFAULT NULL NULL,
    CONSTRAINT tb_device_data_pk UNIQUE (timestamp, timeseriesKey)
)
COMMENT 'Main table to store environmental data from the ThingsBoard platform collection';
COMMIT;