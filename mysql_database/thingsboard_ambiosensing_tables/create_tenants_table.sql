DROP TABLE IF EXISTS ambiosensing_thingsboard.thingsboard_tenants_table;

CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.thingsboard_tenants_table
(
    entityType          VARCHAR(15)     DEFAULT NULL NULL,
    id                  VARCHAR(100)    DEFAULT NULL NULL,
    createdTime         DATETIME        DEFAULT NULL NULL,
    description         VARCHAR(255)    DEFAULT NULL NULL,
    country             VARCHAR(70)     DEFAULT NULL NULL,
    state               VARCHAR(70)     DEFAULT NULL NULL,
    city                VARCHAR(70)     DEFAULT NULL NULL,
    address             VARCHAR(255)    DEFAULT NULL NULL,
    address2            VARCHAR(255)    DEFAULT NULL NULL,
    zip                 VARCHAR(30)     DEFAULT NULL NULL,
    phone               VARCHAR(30)     DEFAULT NULL NULL,
    email               VARCHAR(100)    DEFAULT NULL NULL,
    title               VARCHAR(150)    DEFAULT NULL NULL,
    region              VARCHAR(100)    DEFAULT NULL NULL,
    name                VARCHAR(100)    DEFAULT NULL NULL,
    CONSTRAINT thingsboard_tenants_table_pk UNIQUE (id)
)
COMMENT 'Table to store the full information for a tenant, as it is returned from the remote API';
COMMIT;