import os, time, json, subprocess
from datetime import datetime
from awsiot import mqtt_connection_builder
from awscrt import mqtt
from dotenv import load_dotenv


VIDEO_DIR = "./vids"
MOTION_COMMAND = "motion -c ./motion.conf -l ./motion_log.txt &"

# Load secrets from local file
load_dotenv("breaksaver.env")
DEVICE_CERT = os.environ.get("IOT_THING_CERT")
DEVICE_PRIVKEY = os.environ.get("IOT_THING_PRIVKEY")
ENDPOINT = os.environ.get("MY_AWS_ENDPOINT")
CLIENT_ID = os.environ.get("MOTION_SENSOR_CLIENT")
 
subprocess.run(MOTION_COMMAND,
               shell=True, # allows pipes etc
               check=True) # raise an error if the command exits with an error

def build_direct_mqtt_connection():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        cert_filepath=DEVICE_CERT,
        pri_key_filepath=DEVICE_PRIVKEY,
        endpoint=ENDPOINT,
        client_id=CLIENT_ID)
    return mqtt_connection

files = os.listdir(VIDEO_DIR)
prior_checksum = hash(str(files))

mqtt_connection = build_direct_mqtt_connection()
connect_future = mqtt_connection.connect()
connect_future.result()
print('Connected successfully')

while True:
    files = os.listdir(VIDEO_DIR)
    new_checksum = hash(str(files))
    
    if new_checksum != prior_checksum:
        # Send a message that motion was detected
        message = {}
        message['text'] = "Motion was detected on " + CLIENT_ID
        message['time'] = "{}".format(datetime.now().strftime("%H:%M:%S"))
        message_json = json.dumps(message)

        print('publishing a message..')
        print(message_json)        

        publish_future, idnum = mqtt_connection.publish(
            topic=CLIENT_ID,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)
        publish_future.result()
        
        prior_checksum = new_checksum

    print(new_checksum)
    time.sleep(1)
    
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
print("Disconnected!")
