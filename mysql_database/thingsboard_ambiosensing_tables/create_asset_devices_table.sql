DROP TABLE IF EXISTS ambiosensing_thingsboard.thingsboard_asset_devices_table;

CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.thingsboard_asset_devices_table
(
    fromType            VARCHAR(30)     DEFAULT NULL NULL,  -- entity Type of the element in the 'From' (originator) side of the relation
    fromId              VARCHAR(100)    DEFAULT NULL NULL,  -- Respective entity Id of the previous element
    toType              VARCHAR(30)     DEFAULT NULL NULL,  -- entity Type of the element in the 'To' (destination) side of the relation
    toId                VARCHAR(100)    DEFAULT NULL NULL,  -- Respective entity Id of the previous element
    relationType        VARCHAR(50)     DEFAULT NULL NULL,
    relationGroup       VARCHAR(50)     DEFAULT NULL NULL,
    description         VARCHAR(999)    DEFAULT NULL NULL,
    CONSTRAINT thingsboard_asset_devices_pk UNIQUE (fromId, toId)
)
COMMENT 'This is one of the several tables that the Ambiosensing project needs to keep up that do not reflect direct arrangements that are already made on the ThingsBoard installation side. This table establishes a more direct connection between
ASSESTs and the DEVICEs that are associated/related to those assets. This relation is very important in our internal project structure but its not directly supported by the default ThingsBoard installation, i.e., there is not a direct API call
that can return that per se.';
COMMIT;