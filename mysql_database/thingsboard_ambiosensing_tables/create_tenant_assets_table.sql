DROP TABLE IF EXISTS ambiosensing_thingsboard.tb_tenant_assets;

CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.tb_tenant_assets
(
    entityType          VARCHAR(15)     DEFAULT NULL NULL,
    id                  VARCHAR(100)    DEFAULT NULL NULL,
    createdTime         DATETIME        DEFAULT NULL NULL,
    description         VARCHAR(255)    DEFAULT NULL NULL,
    tenantId            VARCHAR(100)    DEFAULT NULL NULL,
    customerId          VARCHAR(100)    DEFAULT NULL NULL,
    name                VARCHAR(100)    DEFAULT NULL NULL,
    type                VARCHAR(100)    DEFAULT NULL NULL,
    CONSTRAINT thingsboard_tenant_assets_table_pk UNIQUE (id)
)
    COMMENT 'Table to store all assets belonging to a given tenant';
COMMIT;
