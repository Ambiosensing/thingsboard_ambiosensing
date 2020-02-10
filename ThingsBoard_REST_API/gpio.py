# Base module to control the GPIO pins in a Raspberry Pi 3 modules using the MQTT interface, which allows for RPC calls from the ThingsBoard interface (including the API) and thus actuating in a remote prototype through the ThingsBoard API
# interface. This code was based on the source available at https://blog.thingsboard.io/2016/12/raspberry-pi-gpio-control-over-mqtt.html
# Ricardo Almeida Feb 2020
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json

THINGSBOARD_HOST = '10.172.66.223'
ACCESS_TOKEN = 'rizPJk2E0yXMugHeJZuQ'

# Assuming all GPIOs are LOW by default
gpio_state = {
    7: False,
    11: False,
    12: False,
    13: False,
    15: False,
    16: False,
    18: False,
    22: False,
    29: False,
    31: False,
    32: False,
    33: False,
    35: False,
    36: False,
    37: False,
    38: False,
    40: False
}


# Call back for when the client receives a CONNACK response from the server side
def on_connect(client, userdata, rc):
    print('Connected with result code ' + str(rc))

    # Subscribe to receive RPC requests
    client.subscribe('v1/devices/me/rpc/request/+')
    # Sending current GPIO status
    client.publish('v1/devices/me/attributes', get_gpio_status(), 1)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))

    # Decode JSON request
    data = json.loads(msg.payload)

    # Check request method
    if data['method'] == 'getGpioStatus':
        # Reply with GPIO status
        client.publish(msg.topic.replace('request', 'response'),get_gpio_status(), 1)
    elif data['method'] == 'setGpioStatus':
        # Update GPIOs status and reply
        set_gpio_status(data['params']['pin'], data['params']['enabled'])
        client.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
        client.publish('v1/devices/me/attributes', get_gpio_status(), 1)


def get_gpio_status():
    # This method encodes the GPIOs state into a json structures
    return json.dumps(gpio_state)


def set_gpio_status(pin, status):
    # Output the GPIOs state
    GPIO.output(pin, GPIO.HIGH if status else GPIO.LOW)
    # Update GPIOs state
    gpio_state[pin] = status


# Now the main logic
# Using board GPIO layout
GPIO.setmode(GPIO.BOARD)
for pin in gpio_state:
    # Set the output mode for all GPIO pins
    GPIO.setup(pin, GPIO.OUT)

client = mqtt.Client()

# Register connect callback
client.on_connect = on_connect

# Registered publish message callback
client.on_message = on_message

# Set access token
client.username_pw_set(ACCESS_TOKEN)

# Connect to Thingsboard using default MQTT port and 60 seconds keepalive interval
client.connect(THINGSBOARD_HOST, 1883, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    GPIO.cleanup()
