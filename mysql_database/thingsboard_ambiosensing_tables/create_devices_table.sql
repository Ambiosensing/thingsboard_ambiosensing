DROP TABLE IF EXISTS thingsboard_devices_table;

CREATE TABLE IF NOT EXISTS thingsboard_devices_table
(
    entityType          VARCHAR(15)     DEFAULT NULL NULL,
    name                VARCHAR(100)    DEFAULT NULL NULL,
    type                VARCHAR(100)    DEFAULT NULL NULL,
    label               VARCHAR(100)    DEFAULT NULL NULL,
    timeseriesKeys      VARCHAR(999)    DEFAULT NULL NULL,
    id                  VARCHAR(100)    DEFAULT NULL NULL,
    createdTime         DATETIME        DEFAULT NULL NULL,
    description         VARCHAR(255)    DEFAULT NULL NULL,
    tenantId            VARCHAR(100)    DEFAULT NULL NULL,
    customerId          VARCHAR(100)    DEFAULT NULL NULL,
    CONSTRAINT thingsboard_device_table_pk UNIQUE (id)
)
COMMENT 'Table to store the full information of a device, as well as all its relations (associated tenant and/or customer)';
COMMIT;
