"""This is a simple module to be run continuously in the remote device that is to be controlled from the ThingsBoard RCP API
The module implements two basic methods: setRelay and getRelayStatus, which emulate the typical 'getValue' and 'setValue' methods in these cases (I've increased the complexity on purpose since our end product has to be able to run way more methods
 than those simple ones) that are used to set and checnk the status of a Relay that is mounted in Raspberry Pi 3's RPi Relay Board

 IMPORTANT: To activate stuff in the RPi Relay Board from the ThingsBoard API, send a request with a following format:
 {
    "method": "setRelay",
    "params":   {
                    "relay": relay_number (int),
                    "value": status to set
                }
 }

 where relay number needs to be an integer between 1 and 3, which also identifies which relay is to be set and value is the operation to be performed in the relay. This is quite a flexible field: it accepts 1, True or any lowercase/uppercase
 permutations of 'ON' to activate a relay and 0, False or the same permutations of 'OFF' to turn it off. Invalid requests receive a message identifying what went wrong.

 To get the status of the Relay, use the following request format:
 {
    "method": "getRelayStatus"
 }

"""
import json
import paho.mqtt.client as mqtt
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


def on_connect(client, userdata, flags, rc):
    """ Define what to do once the Client object, the main interface used by this MQTT library, gets connected to the server. This method is defined here and its going to be 'loaded' into the client, i.e., the client gets the instruction to run
    whatever is going to be defined in this method as soon as it achieves a successful connection with the server entity. The client object contains an 'on_connected' parameter that expects a method signature
    IMPORTANT: To function properly, the method associated to the 'on_connect' property of the client object needs to have a very specific argument signature, regardless if those arguments are used later on or not. In the 'on_connect' case,
    the method as to have a 'client', 'userdata', 'flags' and 'rc' elements to work properly, even if the method itself only prints out a "Hello World!" and doesn't want anything with those
    """
    # The connection only happens once, so might as well inform the user about it if it was successful
    print("Client connected to {0} successfully!".format(str(THINGSBOARD_HOST)))

    # Subscribe this device to the topic, effectively connecting the physical device to the server
    client.subscribe(subscribe_topic)

    # And inform the user of that too
    print("Client subscribed successfully to the topic: {0}".format(str(subscribe_topic)))


def on_message(client, user_data, msg):
    """This method follows the same logic as the previous one: it gets 'attached' to the client object and whatever routine is set in this method gets executed as soon as the client receive a message (a RPC request from the server that is).
    Use this method to implement bi-directional communication by reacting to certain elements in the message received (which is automatically loaded into the 'msg.payload' in the argument signature). The 'msg' element is a JSON object, i.e.,
    a dictionary-type structure (key-value)"""

    # The flow from this point is directed by detecting which value is set under certain expected keys (obviously the server needs to know in advance which method signatures the client provides from its side. So, start by extract the contents of
    # the 'msg' argument into a proper JSON/dictionary structure for easier access
    data = json.loads(msg.payload)

    # Before anything, this method expects a reply (I'm assuming so for all 'gets'), therefore I need to retrieve the request Id that was used to place this request in the first place. This is how bidirectional communication works with
    # ThingsBoard: requests always need to come from the server side (doesn't make much sense otherwise really...) and they have a specific RequestId, which need to be provided in the response so that the server knows what its getting
    # responded to.
    # The requestId can be extracted directly from the URL (retrievable via msg.topic) used to place the request in the first place. The next statement simply extracts the request Id, which is currently embedded in the request URL,
    # by selecting all characters after the request_topic defined above until the end of the string
    requestId = msg.topic[len(request_topic):len(msg.topic)]

    # And from here, check what is provided in the 'method' key in the data parameter extracted
    if data['method'] == 'getRelayStatus':
        # Only trigger this method if the request topic defined above was used to place whatever message has reached this client or otherwise this method may be triggered with all sorts of maintenance messages and the such
        if msg.topic.startswith(request_topic):

            # Build the response first
            response = "Relay 1 (CH1) is {0}, Relay 2 (CH2) is {1} and Relay 3 is {2}"\
                .format(str(GPIO.input(Relay_Ch1)), str(GPIO.input(Relay_Ch2)), str(GPIO.input(Relay_Ch3)))

            # And send it back by publishing it with the requestId just retrieved in the response topic already defined
            client.publish(response_topic + requestId, json.dumps(response), 1)

    if data["method"] == 'setRelay':
        # Identically, this method is used to turn a relay ON/OFF. I'm felling so magnanimous that I'm even allowing all sorts of values for ON (1, True, 'on', 'ON', etc..) as well as for OFF (0, False, 'off', 'OFF', etc..) for this operation
        # Though this type of operations don't require a reply, I'm giving it anyway, namely if the operation was done properly or not
        # Lets grab the setting then and cast it to a lowercase str right of the bat (it keeps things so, so much simpler for what I want to do)
        relay = str(data['params']['relay'])
        setting = str(data['params']['value']).lower()

        # Providing a proper relay number is a deal breaker. Check this before going further:
        if relay == '1':
            relay = Relay_Ch1
        elif relay == '2':
            relay = Relay_Ch2
        elif relay == '3':
            relay = Relay_Ch3
        else:
            relay = None

        if relay:
            if setting == '1' or setting == 'true' or setting == 'on':
                # Yeah, my RPi Relay Board doesn't care too much for Trues or ONs. Its all a big GPIO.HIGH for it anyways...
                setting = GPIO.HIGH
            elif setting == '0' or setting == 'false' or setting == 'off':
                setting = GPIO.LOW
            else:
                # Signal a bad input by setting the 'setting' to None
                setting = None

        if relay is not None and setting is not None:
            # Set the damn relay then if all was good
            GPIO.output(relay, setting)
            response = "Relay {0} was turned {1}".format(str(data['params']['relay']), 'ON' if setting == GPIO.HIGH else "OFF")
        elif not relay:
            response = "This device only has 3 relays! Could not activate relay {0}".format(str(data['param']['relay']))
        else:
            response = "Warning: Invalid operation for relay {0} provided: {1}. Cannot continue...".format(str(relay), str(data['params']['value']))

        # Almost done. Publish the message and get done with it
        client.publish(response_topic + requestId, json.dumps(response), 1)


# Method definitions finished. Proceed with starting the main routine
# Create the main client
client = mqtt.Client()

# And attach to it the methods defined above
client.on_connect = on_connect
client.on_message = on_message

# And set the ACCESS token as this client's password, which effectively achieves the desired effect
client.username_pw_set(ACCESS_TOKEN)

# And try to connect the just created client to the server defined.
# NOTE: ThingsBoard uses port 1883 for MQTT communications, hence the argument. The last argument is the keepalive timeout (60 seconds)
client.connect(THINGSBOARD_HOST, 1883, 60)

# And run this in an loop that can be terminated with a CTRL-C (That what the try-except clause for a KeyboardInterrupt does)
try:
    client.loop_start()

    while True:
        pass

except KeyboardInterrupt:
    client.disconnect()
