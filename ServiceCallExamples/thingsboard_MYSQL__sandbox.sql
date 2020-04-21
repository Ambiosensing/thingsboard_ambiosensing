use ambiosensing_thingsboard;

select * from thingsboard_tenants_table;
UPDATE thingsboard_tenants_table SET entityType = 'TENANT', id = '863ae890-0ad9-11ea-8001-3975f352e04e', createdTime = '2019-11-01 12:12:14', description = NULL, country = 'Portugal', state = 'Setúbal', city = 'Caparica', address = 'Campinho City', address2 = NULL, zip = '7200', phone =  '+351 934669151', email = 'rlalmeida@gmail.com', title = 'Mr Ricardo Almeida', region = 'Global', name ='Mr Ricardo Almeida' WHERE id = '863ae890-0ad9-11ea-8001-3975f352e04e';
UPDATE thingsboard_tenants_table SET entityType = 'TENANT', id = '46a695e0-0af1-11ea-8001-3975f352e04e', createdTime = '2019-11-01 12:12:14', description = NULL, country = 'Portugal', state = 'Setúbal', city = 'Caparica', address = 'Campinho City', address2 = NULL, zip = '7200', phone =  '+351 934669151', email = 'rlalmeida@gmail.com', title = 'Mr Ricardo Almeida', region = 'Global', name ='Mr Ricardo Almeida' WHERE id = '46a695e0-0af1-11ea-8001-3975f352e04e';
UPDATE thingsboard_tenants_table SET entityType = 'TENANT', id = 'b99c3b80-0efd-11ea-91d1-4f99a1aba158', createdTime = '2019-11-01 12:12:14', description = NULL, country = 'Portugal', state = 'Setúbal', city = 'Caparica', address = 'Campinho City', address2 = NULL, zip = '7200', phone =  '+351 934669151', email = 'rlalmeida@gmail.com', title = 'Mr Ricardo Almeida', region = 'Global', name ='Mr Ricardo Almeida' WHERE id = 'b99c3b80-0efd-11ea-91d1-4f99a1aba158';
UPDATE thingsboard_tenants_table SET entityType = 'TENANT', id = '91a51a60-0efe-11ea-91d1-4f99a1aba158', createdTime = '2019-11-01 12:12:14', description = NULL, country = 'Portugal', state = 'Setúbal', city = 'Caparica', address = 'Campinho City', address2 = NULL, zip = '7200', phone =  '+351 934669151', email = 'rlalmeida@gmail.com', title = 'Mr Ricardo Almeida', region = 'Global', name ='Mr Ricardo Almeida' WHERE id = '91a51a60-0efe-11ea-91d1-4f99a1aba158';


select * from thingsboard_devices_table;

UPDATE thingsboard_devices_table SET entityType = 'DEVICE', id = '00b3e7c0-0ada-11ea-8001-3975f352e04e', createdTime = '2019-11-19 11:11:11', description = 'some bullshit', tenantId = '', customerId = '', name = 'iron maiden', type = 'torture device', label = 'nazi eater' WHERE id = '00b3e7c0-0ada-11ea-8001-3975f352e04e';
UPDATE thingsboard_devices_table SET entityType = 'DEVICE', id = '08f28040-0ada-11ea-8001-3975f352e04e', createdTime = '2019-11-19 11:11:11', description = 'some bullshit', tenantId = '', customerId = '', name = 'iron maiden', type = 'torture device', label = 'nazi eater' WHERE id = '08f28040-0ada-11ea-8001-3975f352e04e';
UPDATE thingsboard_devices_table SET entityType = 'DEVICE', id = 'e0486ea0-0f13-11ea-91d1-4f99a1aba158', createdTime = '2019-11-19 11:11:11', description = 'some bullshit', tenantId = '', customerId = '', name = 'iron maiden', type = 'torture device', label = 'nazi eater' WHERE id = 'e0486ea0-0f13-11ea-91d1-4f99a1aba158';
UPDATE thingsboard_devices_table SET entityType = 'DEVICE', id = 'fa9d0090-0f13-11ea-91d1-4f99a1aba158', createdTime = '2019-11-19 11:11:11', description = 'some bullshit', tenantId = '', customerId = '', name = 'iron maiden', type = 'torture device', label = 'nazi eater' WHERE id = 'fa9d0090-0f13-11ea-91d1-4f99a1aba158';

USE ambiosensing_thingsboard;
SELECT entityType, id, timeseriesKey FROM thingsboard_devices_table WHERE name LIKE 'Water%';

SELECT * FROM ambiosensing_thingsboard.tb_customers;
SELECT * FROM ambiosensing_thingsboard.tb_devices;
SELECT * FROM ambiosensing_thingsboard.tb_tenants;
SELECT * FROM ambiosensing_thingsboard.tb_authentication;

SELECT * FROM ambiosensing_thingsboard.tb_tenant_assets WHERE id = "efa6d2d0-0ad9-11ea-8001-3975f352e04e";

SELECT * FROM ambiosensing_thingsboard.tb_asset_devices;

SHOW TABLES FROM ambiosensing_thingsboard;
SELECT * FROM ambiosensing_thingsboard.ambi_05_data;
