import boto3
import json
import gzip
import re

def lambda_handler(event, context):
    # Initialize S3 and SNS clients
    s3_client = boto3.client('s3')
    sns_client = boto3.client('sns')

    # Specify the S3 bucket and SNS topic ARN
    bucket_name = 'assignment_bucket_s3_logs_from_alb_712'
    sns_topic_arn = 'arn:aws:sns:ap-south-1:367065853931:assignment_sns'

    for record in event['Records']:
        # Get the S3 bucket and object key from the event record
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Download and unzip the log file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        log_data = gzip.decompress(response['Body'].read())

        # Perform log analysis (replace this with your own logic)
        if is_ddos_attack(log_data):
            # If predefined criteria for DDoS attack are met, send a notification
            send_notification(sns_client, sns_topic_arn, "Potential DDoS attack detected!")

def is_ddos_attack(log_data):
    # Replace this with your own logic to detect DDoS attacks
    # At this moment I am unaware about any logic for DDoS attacks
    return 'DDoS' in log_data.decode('utf-8')

def send_notification(sns_client, topic_arn, message):
    # Send a notification via SNS
    sns_client.publish(TopicArn=topic_arn, Message=message, Subject="Log Analysis Alert")