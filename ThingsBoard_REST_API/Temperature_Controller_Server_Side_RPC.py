# Test module for executing RPC commands from the remote device side. This module implements the workings of device that is going to be connected to the server instance of ThingsBoard (my local TB installation) in both read and actuate modes

import json
import paho.mqtt.client as mqtt
from threading import Thread
import time
import datetime


# ThingsBoard server credentials - The IP address that my remote Raspberry Pi Ambi-05 'sees' my TB local installation, i.e., the IP address of the machine that has that TB installation in the local network's context

# Typical host for my RICARDO-NTBOOK machine (on the Uninova's LAN)
# THINGSBOARD_HOST = '10.172.66.223'

# Typical host for my HA-RALMEIDA-P1 (On my home's LAN)
THINGSBOARD_HOST = '192.168.1.24'

# THINGSBOARD_HOST = 'localhost'

# Access token for the Ambi-05 device, as provided by the ThingsBoard local installation in the RICARDO-NTBOOK machine
# ACCESS_TOKEN = 'rizPJk2E0yXMugHeJZuQ'

# Access token for the Ambi-05 device when configured in my HA-RALMEIDA-P1 machine's local ThingsBoard installation
# Device type (for configuring the dashboard alias): temperature_controller
ACCESS_TOKEN = 'XJCv4VjHvhvtEaVoHGFK'

# Access token for the emulated Temperature controller interface
# For my RICARDO-NTBOOK machine
# ACCESS_TOKEN = 'v5JLj4EGL1qB7haqBspq'

# For my HA-RALMEIDA-P1 machine
# ACCESS_TOKEN = 'Cloy4nszTD6j7wvOxmUW'

sensor_data = {'test_temperature': 25}

subscribe_topic = 'v1/devices/me/rpc/request/+'
telemetry_topic = 'v1/devices/me/telemetry'

base_topic = 'v1/devices/me/rpc/'
request_base_topic = base_topic + 'request/'
response_base_topic = base_topic + 'response/'


def publishValue(client):
    INTERVAL = 5
    print("Thread Started...")
    next_reading = time.time()
    while True:
        client.publish(telemetry_topic, json.dumps(sensor_data), 1)
        print("Published '{0}' into {1} at {2}. Sleeping now...".format(str(sensor_data), str(THINGSBOARD_HOST), str(datetime.datetime.now().replace(microsecond=0))))
        next_reading += INTERVAL
        sleep_time = next_reading - time.time()

        if sleep_time > 0:
            time.sleep(sleep_time)


def read_temperature():
    temp = sensor_data['test_temperature']
    return temp


# Function will set the temperature value in device
def setValue(params):
    """How to execute this method using a server side RPC call:
    API service to call: rpc-controller.handleTwoWayDeviceRPCRequest
    Arguments: deviceId: the identification string obtainable by configuring the device in the ThingsBoard installation acting as server. This field expects a 32 byte hexadecimal string, with a dash '-' separating blocks of 8, 4, 4,
    4 and 12 bytes respectively. E.g: 39297590-51aa-11ea-89dc-25d13d30f848
    requestBody: A JSON dictionary in the following format:
    data =
    {
        "method": "setValue",
        "params":
        {
            "test_temperature": int
        }
    }
    , where in this basic example, the method to be executed from the client side (device) has to be properly identified under the "method" key (respecting the lower casing too) and the value to set has to come under the "params" key. Check the
    on_message method definition to see why this has to be this way and how to change it if necessary
    """
    sensor_data['test_temperature'] = params
    print("Temperature Set: ", params, " ºC")


# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    client.subscribe(subscribe_topic)
    print("Subscribed this device to the following topic: " + subscribe_topic)


# MQTT on_message callback function
def on_message(client, userdata, msg):
    # print ('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    if msg.topic.startswith(request_base_topic):
        requestId = msg.topic[len(request_base_topic):len(msg.topic)]
        # print("requestId : ", requestId)
        data = json.loads(msg.payload)

        if data['method'] == 'getValue':
            # print("getvalue request\n")
            # print("sent getValue : ", sensor_data)
            client.publish(response_base_topic + requestId, json.dumps(sensor_data['test_temperature']), 1)

        if data['method'] == 'setValue':
            # print("setvalue request\n")
            params = data['params']
            setValue(params)


# Create a client instance
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

t = Thread(target=publishValue, args=(client,))

try:
    client.loop_start()
    t.start()

    while True:
        pass

except KeyboardInterrupt:
    client.disconnect()