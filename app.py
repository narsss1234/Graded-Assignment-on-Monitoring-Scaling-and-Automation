import boto3
import json

REGION='ap-south-1'

# Create an S3 client
s3_client = boto3.client('s3')

def create_s3_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration={
                            'LocationConstraint': REGION,
                            }
                        )
        return f"S3 bucket '{bucket_name}' created successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"

bucket_name = 'web-application-static-files-1'
result_message = create_s3_bucket(bucket_name)
print(result_message)

def upload_to_s3_bucket(bucket_name):
    try:
        s3_client.upload_file('index.html',bucket_name, 'index.html')
        return f"File index.html has been uploaded successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"

result_message_upload_to_s3 = upload_to_s3_bucket(bucket_name)
print(result_message_upload_to_s3)

# Create an ec2 client

ec2_client = boto3.client('ec2')

USERDATA='''#!/bin/bash
sudo apt update
sudo apt install awscli nginx -y
aws s3 cp s3://web-application-static-files-1/index.html /tmp/index.html
sudo systemctl start nginx
sudo systemctl enable nginx
sudo rm -rf /var/www/html/*
sudo cp /tmp/index.html /var/www/html/index.html
sudo systemctl restart nginx
'''
AMI_IMAGE_ID = 'ami-03f4878755434977f'
INSTANCE_TYPE = 't2.micro'
DISK_SIZE_GB = 8
DEVICE_NAME = '/dev/xvda'
SECURITY_GROUPS_IDS = ['sg-0d9a2cb2f73468506']
ROLE_PROFILE = 'ec2-service-role-admin'

def create_ec2_instance():
    try:
        response = ec2_client.run_instances(
            ImageId=AMI_IMAGE_ID,
            InstanceType=INSTANCE_TYPE,
            SecurityGroupIds=SECURITY_GROUPS_IDS,
            UserData=USERDATA,
            IamInstanceProfile={
                'Name':ROLE_PROFILE
            },
            KeyName='ec2',
            MaxCount=1,
            MinCount=1,
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            instance_id = response['Instances'][0]['InstanceId']
            ec2_client.get_waiter('instance_running').wait(
                InstanceIds=[instance_id]
            )
            print('Success! instance:', instance_id, 'is created and running')
        else:
            print('Error! Failed to create instance!')
            raise Exception('Failed to create instance!')
        
        print("Instance has been created.")
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"

create_ec2_instance()