import os, time, json, subprocess, glob, boto3
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
VIDEO_BUCKET = os.environ.get("MOTION_S3_BUCKET")

def build_direct_mqtt_connection():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        cert_filepath=DEVICE_CERT,
        pri_key_filepath=DEVICE_PRIVKEY,
        endpoint=ENDPOINT,
        client_id=CLIENT_ID)
    return mqtt_connection

def upload_file(file):
    modified_time = os.stat(file).st_mtime
    print(modified_time)
    file_ready = False

    # Wait until the file is no longer being changed, then upload it
    while file_ready == False:
        time.sleep(1)
        if modified_time != os.stat(file).st_mtime:
            modified_time = os.stat(file).st_mtime
        else:
            file_ready = True

    vid = open(file, 'rb')
    s3 = boto3.resource('s3')
    s3.Bucket(VIDEO_BUCKET).put_object(Key=os.path.basename(file), Body=vid)
    print("Uploaded video to s3...")


if __name__ == "__main__":

    subprocess.run(MOTION_COMMAND,
                   shell=True, # allows pipes etc
                   check=True) # raise an error if the command exits with an error
    
    files = os.listdir(VIDEO_DIR)
    prior_checksum = hash(str(files))
    
    mqtt_connection = build_direct_mqtt_connection()
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print('Connected to MQTT topic successfully')
    
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
            
            # Wait for the publish to complete before moving on.
            publish_future.result()
            
            all_vids = glob.glob(VIDEO_DIR + "/*")
            latest_vid = max(all_vids, key=os.path.getctime)
            upload_file(latest_vid)
            
            print("uploading the latest video, which is {0}".format(latest_vid))
            
            prior_checksum = new_checksum

            print(new_checksum)
            time.sleep(1)
    
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
        

        
