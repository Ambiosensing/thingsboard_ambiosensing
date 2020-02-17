# Small script to test client-side RPC requests, i.e., when a request is initiated from an external device (a Raspberry Pi for example) and the ThingsBoard installation works as a server in this client-server modelling

import json
import paho.mqtt.client as mqtt

# ThingsBoard platform credentials
# Fist, how to identify the ThingsBoard platform on the network. Since I'm going to run this script from the same device where I have my ThingsBoard installation, my server host is simply that. If this script is run from the device,
# replace this by the IP of the machine where the ThingsBoard application is installed.
# For example, I have my ThingsBoard application installed in a machine in the Uninova office that is plugged to a walled Ethernet port. The building network has
# gave a local IP address to this machine from the pool of addresses in the University's local network (I think that's the case anyhow), which, currently, is 10.172.66.223. I can now plug a Raspberry Pi unit to another Ethernet socket in this
# office, which adds this device to the same local network but with a an address from the local network's prefix, namely, 10.172.67.127 (the network manager changes this address with some frequency BTW). So, if I'm running this module from the
# Raspberry unit, I need to replace the THINGSBOARD_HOST by the IP of which the local installation can be identified in the local network
THINGSBOARD_HOST = 'localhost'
# THINGSBOARD_HOST = 10.172.66.223

# This is the access token of the device that places the request. In this case, this Access Token belongs to the device Controller A that I have configured in the THINGSBOARD_HOST machine - This is how ThingsBoard manages the data flow,
# I think. When a request from some foreign IP comes in (because I'm using the THINGSBOARD_HOST to identify the target of my request), it matches the IP from where this request came from to the access token that is provided in the request URL (
# details on this bellow). Thus, when replying to the device, the ThingsBoard installation only needs to consult this match to determine the IP of the device that is waiting for a reply, if that is the case)
ACCESS_TOKEN = 'KtPKsFFUWoQDfFUQnPJN'

# The payload to deliver to the server. In the ThingsBoard installation I've edited the Root Rule Chain and added a message filter at the head of a dedicated branch that is used only to process messages of this type. When the RPC request is
# executed, a message gets delivered at the Input node at the Root rule chain. From there, it goes to a series of filters and modifiers that forward it to the proper chain of nodes. In this case, there's a Message Filter Node that only allow
# message with JSON block containing a key "method" and a respective "getTemperature" as value. The javascript filter rule is "return msg.method === 'getTemperature'". The request variable bellow arrives to the ThingsBoard installation - Input
# node encapsulated in the "msg" structure. This is just the parent structure. In this particular case, the "msg" is going to have 2 children/keys: 'method' and 'params'. The filter javascript expression actually validates two things: 1. the 'msg'
# structure has a 'method' child and that 'method' has a 'getTemperature' value associated to it.
# The javascript filter function yields only 'true' or 'false' in this case and one can configure the rest of the rule chain in that assumption: if the result is 'false' we can raise an Alarm, send and e-mail or simply do nothing. If the result is
# true, proceed with the message processing.
data_payload = {"method": "getTemperature", "params": {}}

# Now the topics to which ThingsBoard processes Requests and Responses. Basically, to send RPC commands to the server (ThingsBoard installation) send a PUBLISH type message to the request topic/endpoint
# The server then uses the response topic to PUBLISH responses to those requests, hence why this application starts by making the client (the Raspberry Pi or the virtual device Controller A used in this example) subscribe to that topic in order to
# grab any replies from the server side

# Subscribe for RPC commands using the requests_topic
request_topic = "v1/devices/me/rpc/request/1"
response_topic = "v1/devices/me/rpc/response/+"


def do_this_on_connect(client, userdata, flags, rc):
    """When there's a successful connection from the client to the server, print the request code.
    NOTE: Apparently this method requires a specific argument signature to work, namely, 'client', 'userdata', 'flags' and 'rc' (not sure if the argument order influences this or not). I was bothered by the unused 'userdata' and 'flags' arguments
    so I remove them initially. But it turns out that the method blocks if those areguments are not in the signature! Go figure!"""
    print("rc code: ", rc)
    # And, before sending the request, subscribe the client to the response topic so that once the server sends back a response, the client can get it immediately
    client.subscribe(response_topic)
    # Now that everything in place, submit a request to the respective topic with the data payload defined in 'data_payload'
    client.publish(request_topic, json.dumps(data_payload), 1)


def do_this_on_message(client, userdata, msg):
    """This method is analogous to the previous one, including the method's signature imposition, i.e., if the associated method to the on_message parameter change doesn't have a 'client', 'userdata' and 'msg' arguments in the signature,
    regardless if they are used by the method or not, the thing simply doesn't work... always learning with this one..."""
    print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))


# Start the client instance
client = mqtt.Client()

# registering the callbaks. When the respective internal parameter of the mqtt.Client object gets set (the 'on_connect' parameter is set to None upon construction and, I assume, is set to True once a successful connection is established with the
# server instance, which can be used to trigger some method call. In the statements bellow, the methods defined above are associated to the 'on_connect' and 'on_message' parameters so that these methods get called once those parameters are set to
# something other than the default 'None'
client.on_connect = do_this_on_connect
client.on_message = do_this_on_message

# Set the necessary parameters to place the call to the server
# Apparently by setting the Access Token from the device as the client's object username this achieves the same result as sending this Access token embedded in the service URL, as it has been usual so far
client.username_pw_set(ACCESS_TOKEN)
# Connect the client to the server using the defined Host name and the MQTT default port for the ThingsBoard installation (1883) and a 'keepalive' of 60 seconds
print("Trying to connect to " + str(THINGSBOARD_HOST) + "...")
client.connect(THINGSBOARD_HOST, 1883, 60)
print("Connected to ThingsBoard server at " + str(THINGSBOARD_HOST) + "!")

try:
    # Use this to keep the connection alive and ready to process requests and responses
    client.loop_forever()
# Exit this loop via CTRL + C, which is caught by Python as a KeyboardInterrupt Exception
except KeyboardInterrupt:
    # Turn of the connection if CTRL+C is pressed
    print("Terminating connection to " + str(THINGSBOARD_HOST) + "...")
    client.disconnect()
    print("Server disconnected successfully!")
