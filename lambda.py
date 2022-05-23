import boto3
#
#   expects event parameter to contain:
#   {
#       "text":"something regarding device motion sensing",
#       "time":"some value to indicate time",
#       "lenovo_motion_arn":"the ARN of a SNS topic to publish a message to"
#   }
# 
#   sends a plain text string to be used in a text message
#
#     "Lenovo device reports message \"{0}\", at time {1}"
#   
#   where:
#       {0} is "text"
#       {1} is "time"

def lambda_handler(event, context):

    # Create an SNS client to send notification
    sns = boto3.client('sns')

    # Format text message from data
    message_text = "Lenovo device reports message \"{0}\", at time {1}".format(
            str(event['text']),
            str(event['time'])
        )

    # Publish the formatted message
    response = sns.publish(
            TopicArn = event['lenovo_motion_arn'],
            Message = message_text
        )

    return response
