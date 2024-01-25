# import boto3 Amazon SDK
import boto3

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

ec2_client = boto3.client('ec2')

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