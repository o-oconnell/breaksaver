# breaksaver
This is a simple motion detection application that sends notifications by publishing to an AWS IoT MQTT topic and uploads recordings to S3. It has been tested on Ubuntu Linux 20.04 and relies on [Motion for Linux](https://motion-project.github.io/), along with the Python libraries listed in the main script. 

To use this script, you will need to set up your AWS account properly. Notifications are done using an AWS Lambda, whose code is included in the repository. The Lambda is triggered by an [AWS IoT rule](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html) which subscribes to the topic published to by the Python script. You can easily [publish to S3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) after configuring AWS CLI on your computer. All environment variables listed at the top of the Python script are required (either in a .env file or as part of your environment) to get the script hooked in to AWS. You can find a tutorial for setting up your device as a thing object for IoT [here](https://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html)

Screenshots:

![terminal](https://github.com/o-oconnell/breaksaver/blob/main/screenshots/terminal.png)
![notification](https://github.com/o-oconnell/breaksaver/blob/main/screenshots/notification2.jpg)

