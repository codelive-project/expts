import paho.mqtt.client as mqtt
import time
import os

BROKER_URLS = [
    "test.mosquitto.org"
]

class MqttConnection(mqtt.Client):
    def __init__(self, 
                 session_name, 
                 broker_url = None, 
                 port = None, 
                 qos = 0, 
                 delay = 1.0, 
                 topic = None):
        mqtt.Client.__init__(self)
        self.broker ="test.mosquitto.org" #TODO: have backup servers - a list of possible alternatives
        self.port = port or self.get_port()
        self.qos = qos
        self.delay = delay
        self.topic = topic or self.get_topic(session_name) #TODO: generate this dynamically
    
    def get_port(self):
        return 1883
    
    def get_topic(self, name):
        return name# + "_" + ''.join(random.choice(string.ascii_uppercase) for i in range(6))

    def get_default_broker(self):
        global BROKER_URLS

        for broker in BROKER_URLS:
            if self.test_broker(broker):
                return broker

        return None

    def test_broker(self, url):
        # TODO: add broker test
        return True

    def Connect(self):
        print("connecting")
        self.connect(self.broker, self.port, 60)
        self.subscribe(self.topic, qos=self.qos)
    
    def EndSession(self):
        self.disconnect()

    def PublishMessage(self, msg):
        self.publish(self.topic, msg)

    # Callback when a message is published
    def on_publish(self, client, userdata, mid):
        print("\npublished\n")
        #do something

    # Callback when connecting to the MQTT broker
    def on_connect(self,client, userdata, flags, rc):
        if rc==0:
            print('Connected to ' + self.broker)
            #do something

    # Callback when client receives a PUBLISH message from the broker
    def on_message(self,client, data, msg):
        if msg.topic == self.topic:
            print("PRINTING:", msg.payload.decode("utf-8"))
            #add to queue instead of what we're doing above




myConnection = MqttConnection("Bono")
myConnection.Connect()
myConnection.loop_start()

while True:
    x = input("Type sth: ")
    if x == "end":
        break

    try:
        myConnection.PublishMessage(x)
    except KeyboardInterrupt:
        print("Done")
        myConnection.EndSession()
        break