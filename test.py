import boto3
import zipfile
import os

REGION='ap-south-1'
s3_client = boto3.client('s3')

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
bucket_name = 'assignment-bucket-for-lambda-function-storing-712'

# calling the create bucket function
result_message = create_s3_bucket(bucket_name)

# printing the return value for the create bucket function
print(result_message)

# defining function to upload to s3 bucket with handling errors gracefully
def upload_to_s3_bucket(bucket_name):
    # try block to attempt upload file a bucket
    try:

        with zipfile.ZipFile('lambda.zip', 'w') as zip_file:
        # Add the file to the zip archive
            zip_file.write('lambda.py')

        s3_client.upload_file('lambda.zip',bucket_name, 'lambda.zip')
        return f"File ${bucket_name} has been uploaded successfully."
    # if eny exception, return the exception as a string
    except Exception as e:
        return f"An error occurred: {str(e)}"

# sotring the response from upload to s3 function
result_message_upload_to_s3 = upload_to_s3_bucket(bucket_name)

# printing the response from upload to s3 function
print(result_message_upload_to_s3)


# --> Step 4:Lambda-based Health Checks & Management

lambda_client = boto3.client('lambda',region_name=REGION)

response_lambda = lambda_client.create_function(
    FunctionName = 'Lambda-Health-Checks',
    Runtime = 'python3.9',
    Role = 'arn:aws:iam::367065853931:role/service-role/Lambda_for_assignment-role-difp8zc1',
    Timeout = 120,
    Code={
        'S3Bucket': 'assignment-bucket-for-lambda-function-storing-712',
        'S3Key': 'lambda.zip',
    },
    Handler='test',
)