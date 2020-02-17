# Small script to test server-side RPC requests.

import time
import json
import paho.mqtt.client as mqtt

# Thingsboard platform credentials
THINGSBOARD_HOST = '10.172.66.223'
ACCESS_TOKEN = 'rizPJk2E0yXMugHeJZuQ'
button_state = {"enabled": False}

subscribe_topic = 'v1/devices/m2/rpc/request/+'
attributes_topic = 'v1/devices/me/attributes'

# Create the base endpoint for the request and response dynamic
topic_base = 'v1/devices/me/rpc/'

# Complement the respective endpoints (NOTE: it still needs the request_id added to them afterwards)
request_topic_base = topic_base + "request/"
response_topic_base = topic_base + "response/"


def setValue(params):
    button_state['enabled'] = params
    print("Rx setValue is : ", button_state)


# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("rc code: ", rc)
    client.subscribe(subscribe_topic)


# MQTT on_message callback function
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    if msg.topic.startswith(request_topic_base):
        requestId = msg.topic[len(request_topic_base):len(msg.topic)]
        print("requestId : ", requestId)
        data = json.loads(msg.payload)

        if data['method'] == 'getValue':
            print("getValue request\n")
            print("sent getValue : ", button_state)
            client.publish(response_topic_base + requestId, json.dumps(button_state), 1)

        if data['method'] == 'setValue':
            print("setValue request\n")
            params = data['params']
            setValue(params=params)
            client.publish(attributes_topic, json.dumps(button_state), 1)

# Start the client instance
client = mqtt.Client()

# Registering the callbacks
client.on_connect = on_connect
client.on_message = on_message


client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

try:
    client.loop_forever()

except KeyboardInterrupt:
    client.disconnect()