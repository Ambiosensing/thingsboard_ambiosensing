DROP TABLE IF EXISTS ambiosensing_thingsboard.tb_authentication;

CREATE TABLE IF NOT EXISTS ambiosensing_thingsboard.tb_authentication
(
    user_type                   VARCHAR(30)     DEFAULT NULL NULL,
    token                       VARCHAR(999)    DEFAULT NULL NULL,
    token_timestamp             DATETIME        DEFAULT NULL NULL,
    refreshToken                VARCHAR(999)    DEFAULT NULL NULL,
    refreshToken_timestamp      DATETIME        DEFAULT NULL NULL
)
COMMENT 'Table to store the authentication and refresh tokens for all the supported user types, namely "SYS_ADMIN", "TENANT_ADMIN" and "CUSTOMER_USER". This table is to be used as a place holder for these tokens so that its not needed to request 
for a new one every time a service is executed. This means that updated tokens should replace old, expired ones instead of writing a new one'
COMMIT;