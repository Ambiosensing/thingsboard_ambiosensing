"""This is a simple module to be run continuously in the remote device that is to be controlled from the ThingsBoard RCP API
The module implements two basic methods: setRelay and getRelayStatus, which emulate the typical 'getValue' and 'setValue' methods in these cases (I've increased the complexity on purpose since our end product has to be able to run way more methods
 than those simple ones) that are used to set and checnk the status of a Relay that is mounted in Raspberry Pi 3's RPi Relay Board
"""
import json
import paho.mqtt as mqtt
import time
import datetime
import RPi.GPIO as GPIO

# Set the GPIO pin code for the pins used by the Relays mounted in the RPi Relay Board
# Example, the Relay 1 (identified in the board as CH1) is controlled by setting GPIO pin 26 HIGH or LOW
Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

# Turn off warnings from the RPi side
GPIO.setwarnings(False)
# And switch on the BCM mode so that it can use the bcm2835 python module methods
GPIO.setmode(GPIO.BCM)

# Just because, set all the pins defined above as OUT pins, since they are only going to drive the Relays
GPIO.setup(Relay_Ch1, GPIO.OUT)
GPIO.setup(Relay_Ch1, GPIO.OUT)
GPIO.setup(Relay_Ch3, GPIO.OUT)


# ThingsBoard server credentials: in order dor this client (Raspberry Pi) to establish communication with the server (the machine where the ThingsBoard application is installed), the client needs the IP/hostname that the machine is identified in
# the Local Area Network or even Internet (if the server has a public IP)
THINGSBOARD_HOST = '192.168.1.24'

# Access token used in the ThingsBoard installation to identify THIS device in its environment. Devices configured in the ThingsBoard platform are abstractions of the actual device - the only connection between the 'virtual device' created in the
# ThingsBoard installation and the physical device is this AccessToken. Any data sent from this device to the server instance has this Access Token configured in the URL used. ThingsBoard can then cross check this token with the devices that it
# has configured and, if a match is found, data received in that communication (telemetry data, RPC commands, attributes, etc...) is submitted into the platform under this device, i.e., from the ThingsBoard installation perspective,
# the data was produced by the 'virtual device' identified by the Access Token provided
ACCESS_TOKEN = 'OTPl99XqUaQNPMAtmdy4'

# Use this topic to subscribe this device for RPC commands. This is the most important action in this routine: its how the ThingsBoard installation knows where the data is coming from and where it has to go in the case of RCP replays. Note that
# until the subscribe action is executed, the device configured in the ThingsBoard side is just an abstraction with no physical target
# IMPORTANT: This is the subscribe topic for MQTT interface, which is the one that is going to be used in this module! If you use HTTP or other communication protocol, please consult the ThingsBoard documentation to find the correct topic to
# subscribe too. Also, this only refers to the communication in the client -> server direction. The ThingsBoard Swagger API is used to communicate in the direction server -> client and it doesn't need this types of concerns
subscribe_topic = 'v1/devices/me/rpc/request/+'

# To properly communicate between interfaces, a pair of request/response topics need to be used (the subscribe one is used only for that):
base_topic = 'v1/devices/me/rpc/'
request_topic = base_topic + 'request/'
response_topic = base_topic + 'response/'

# Define what to do once the Client object, the main interface used by this MQTT library, gets connected to the server. This method is defined here and its going to be 'loaded' into the client, i.e., the client gets the instruction to run whatever
# is going to be defined in this method as soon as it achieves a successful connection with the server entity. The client object contains an 'on_connected' parameter that expects a method signature
# IMPORTANT: To function properly, the method associated to the 'on_connect' property of the client object needs to have a very specific argument signature, regardless if those arguments are used later on or not. In the 'on_connect' case,
# the method as to have a 'client', 'userdata', 'flags' and 'rc' elements to work properly, even if the method itself only prints out a "Hello World!" and doesn't want anything with those
def on_connect(client, userdata, flags, rc):

    # The connection only happens once, so might as well inform the user about it if it was successful
    print("Client connected to {0} successfully!".format(str(THINGSBOARD_HOST)))

    # Subscribe this device to the topic, effectively connecting the physical device to the server
    client.subscribe(subscribe_topic)

    # And inform the user of that too
    print("Client subscribed successfully to the topic: {0}".format(str(subscribe_topic)))

