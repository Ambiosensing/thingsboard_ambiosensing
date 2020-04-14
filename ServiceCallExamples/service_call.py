from ThingsBoard_REST_API import tb_device_controller

var1 = tb_device_controller.getTenantDevices(limit=10)
print('ok')


{"data" :

     [{ "id":
            {"entityType":"DEVICE","id":"34f391a0-4876-11ea-971a-c108b8f2be6f"},"createdTime":1580948311994,
              "additionalInfo":{"description":"TSL2561(Luminosity) / SGP30(Air Quality) / SCD30 (Air Quality) / CCS881 (Gas Sensor)"},
              "tenantId": {"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},
              "customerId": {"entityType":"CUSTOMER","id":"52783040-ae17-11e9-be3e-5191a24525ae"},
              "name": "Rasp_00039", "type":"RASPBERRY_PI"},
      {"id":
            {"entityType": "DEVICE", "id": "b26b9550-92e2-11e9-b2d7-a9d50a42a11e"}, "createdTime":1560983796517,
              "additionalInfo":{"description":"Sensors 2x SHT-31D (Temperature and Humidity) and TSL-2561 (Luminosity)."},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_001","type":"raspberry_pi"},{"id":{"entityType":"DEVICE","id":"2b9378c0-946a-11e9-b2d7-a9d50a42a11e"},"createdTime":1561151933004,"additionalInfo":{"description":"Sensors SHT31-D (Temperature and Humidity), MQ4 (CH4) and MG811 (CO2)."},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_003","type":"raspberry_pi"},{"id":{"entityType":"DEVICE","id":"bf8f2900-946c-11e9-b2d7-a9d50a42a11e"},"createdTime":1561153040272,"additionalInfo":{"description":"Sensors BME280 (Pressure, Temperature and Humidity), MG811 (CO2) and Heating (Multichannel Gas)."},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_004","type":"raspberry_pi"},{"id":{"entityType":"DEVICE","id":"507a5780-d281-11e9-8d16-d75afdb8a7ce"},"createdTime":1567978845432,"additionalInfo":{"description":"HTU21D-F and BME680"},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_005","type":"RASPBERRY_PI"},{"id":{"entityType":"DEVICE","id":"5b17a080-d281-11e9-8d16-d75afdb8a7ce"},"createdTime":1567978863240,"additionalInfo":{"description":"Sensors: HTU21D-F and BME680 (Pressure, Temperature and Humidity)"},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_006","type":"raspberry_pi"},{"id":{"entityType":"DEVICE","id":"9e391040-04ab-11ea-8d16-d75afdb8a7ce"},"createdTime":1573494572868,"additionalInfo":{"description":"Sensors: TSL2561(Luminosity) / BME280(Pressure, Humidity and Temperature)"},"tenantId":{"entityType":"TENANT","id":"02bda270-92e1-11e9-b2d7-a9d50a42a11e"},"customerId":{"entityType":"CUSTOMER","id":"db518340-92e1-11e9-b2d7-a9d50a42a11e"},"name":"Rasp_007","type":"raspberry_pi"}],"nextPageLink":null,"hasNext":false}