import boto3
import json
import time

def lambda_handler(event, context):
    # defining the alb, asg and the sns arn
    alb_name = 'assignment-alb'
    sns_topic_arn = ''
    asg_name = 'assigment_autoscaling_grp'

    alb_client = boto3.client('elbv2')
    ec2_client = boto3.client('ec2')
    sns_client = boto3.client('sns')
    asg_client = boto3.client('autoscaling')

    # Get the target group attached to the ALB
    target_groups = alb_client.describe_target_groups(Names=[alb_name])
    target_group_arn = target_groups['TargetGroups'][0]['TargetGroupArn']

    # Get the instances registered with the target group
    instances = alb_client.describe_target_health(TargetGroupArn=target_group_arn)

    for instance in instances['TargetHealthDescriptions']:
        if instance['TargetHealth']['State'] != 'healthy':
            instance_id = instance['Target']['Id']
            print(f"Unhealthy instance found: {instance_id}")

            # Capture a snapshot of the instance
            snapshot_id = create_snapshot(ec2_client, instance_id)

            # Terminate the problematic instance
            terminate_instance(ec2_client, asg_client, asg_name, instance_id)

            # Send notification through SNS
            message = f"Unhealthy instance {instance_id} terminated. Snapshot ID: {snapshot_id}"
            send_notification(sns_client, sns_topic_arn, message)

def create_snapshot(ec2_client, instance_id):
    response = ec2_client.create_snapshot(
        Description=f"Snapshot for debugging instance {instance_id}",
        VolumeId=instance_id
    )
    return response['SnapshotId']

def terminate_instance(ec2_client, asg_client, asg_name, instance_id):
    # Detach the instance from the Auto Scaling Group
    asg_client.detach_instances(InstanceIds=[instance_id], AutoScalingGroupName=asg_name, ShouldDecrementDesiredCapacity=True)

    # Terminate the instance
    ec2_client.terminate_instances(InstanceIds=[instance_id])

def send_notification(sns_client, sns_topic_arn, message):
    sns_client.publish(TopicArn=sns_topic_arn, Message=message, Subject="Web Application Health Check")