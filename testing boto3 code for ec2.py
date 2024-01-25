import boto3

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
DISK_SIZE_GB = 20
DEVICE_NAME = '/dev/xvda'
SECURITY_GROUPS_IDS = ['sg-0d9a2cb2f73468506']
ROLE_PROFILE = 'ec2-service-role-admin'

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

print(response)