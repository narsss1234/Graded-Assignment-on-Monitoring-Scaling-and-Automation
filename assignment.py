# import boto3 Amazon SDK
import boto3
import time

# defining variable for region of choice
REGION='ap-south-1'

# Create an S3 client
s3_client = boto3.client('s3')

# defining function to create an s3 bucket with handling errors gracefully
def create_s3_bucket(bucket_name):

    # try block to attempt creating a bucket
    try:
        s3_client.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration={
                            'LocationConstraint': REGION,
                            }
                        )
        # return bucket created text if the create_bucket was successful
        return f"S3 bucket '{bucket_name}' created successfully."
    
    # If any exception, like bucket name already exists or if bucket is already owned by us
    except Exception as e:
        return f"An error occurred: {str(e)}"

# defning bucket name in a vatiable
bucket_name = 'web-application-static-files-1'

# calling the create bucket function
result_message = create_s3_bucket(bucket_name)

# printing the return value for the create bucket function
print(result_message)

# defining function to upload to s3 bucket with handling errors gracefully
def upload_to_s3_bucket(bucket_name):
    # try block to attempt upload file a bucket
    try:
        s3_client.upload_file('index.html',bucket_name, 'index.html')
        return f"File index.html has been uploaded successfully."
    # if eny exception, return the exception as a string
    except Exception as e:
        return f"An error occurred: {str(e)}"

# sotring the response from upload to s3 function
result_message_upload_to_s3 = upload_to_s3_bucket(bucket_name)

# printing the response from upload to s3 function
print(result_message_upload_to_s3)

# Create an ec2 client

ec2_client = boto3.client('ec2', region_name=REGION)

# Defining USERDATA and other variables to store the bash script and also instance details to be launched
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
# ec2 role, so that s3 bucket can be access from the instance that will be created
ROLE_PROFILE = 'ec2-service-role-admin'

# empty list to store the instance id that will get generated
InstanceIds=[]

# defining function to create an ec2 Instance with handling errors gracefully

def create_ec2_instance():
    # Try block to attempt running an instance
    try:
        response = ec2_client.run_instances(
            ImageId=AMI_IMAGE_ID,
            InstanceType=INSTANCE_TYPE,
            SecurityGroupIds=SECURITY_GROUPS_IDS,
            UserData=USERDATA,
            IamInstanceProfile={
                'Name':ROLE_PROFILE
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance', 
                    'Tags': [
                        {
                            'Key': 'key',
                            'Value': 'assignment'
                        },
                    ]
                },
            ],
            KeyName='ec2',
            MaxCount=1,
            MinCount=1,
        )

        # If the instance creation is successful, then retrieve the instance id and store it in the empty list for future use
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            instance_id = response['Instances'][0]['InstanceId']
            ec2_client.get_waiter('instance_running').wait(
                InstanceIds.append(instance_id)
            )
            print('Success! instance:', instance_id, 'is created and running')
        # if the response is not 200, then print and raise and exception.
        else:
            print('Error! Failed to create instance!')
            raise Exception('Failed to create instance!')
        return response
    # If any exception, print the exception as string
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# calling the create ec2 function
create_ec2_instance()

time.sleep(120)

# Create an elb client
elb_client = boto3.client('elbv2', region_name=REGION)

# defining ALB attributes

alb_name = "assignment-alb"
subnets = ['subnet-05a15ce69d2d9f69d','subnet-076051ff9276a558d','subnet-0564d17c714b6a55a']
security_groups = ['sg-09e0c5dd41f4bd5b9']

# create alb

def create_alb_and_attach_ec2():
    # create alb

    response_alb = elb_client.create_load_balancer(
        Name = alb_name,
        Subnets = subnets,
        SecurityGroups=security_groups,
        Scheme='internet-facing',
        Tags=[{'Key':'Name','Value':alb_name}]
    )

    # Extracting the ARN of the created ALB

    alb_arn = response_alb['LoadBalancers'][0]['LoadBalancerArn']

    # defining target_group attributes

    target_group_name = 'assignment-target-group'
    target_port = 80
    health_check_path = '/'
    protocol = 'HTTP'

    response_target_grp = elb_client.create_target_group(
        Name=target_group_name,
        Protocol=protocol,
        Port=target_port,
        VpcId='vpc-04ef1d2345f3f906e',
        HealthCheckProtocol=protocol,
        HealthCheckPath=health_check_path,
        HealthCheckPort=str(target_port),
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=5,
        HealthyThresholdCount=2,
        UnhealthyThresholdCount=2,
        Matcher={'HttpCode': '200'}
    )

    target_group_arn = response_target_grp['TargetGroups'][0]['TargetGroupArn']

    # Register ec2 instance with the target

    elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance} for instance in InstanceIds]
    )

    # Create a listener for the ALB

    listener_port = 80

    elb_client.create_listener(
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        }],
        LoadBalancerArn=alb_arn,
        Port=listener_port,
        Protocol=protocol
    )

    return f"ALB {alb_name} and Target Group {target_group_name} created successfully."

print(create_alb_and_attach_ec2())