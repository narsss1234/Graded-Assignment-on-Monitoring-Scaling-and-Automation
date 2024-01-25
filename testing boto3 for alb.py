import boto3
REGION='ap-south-1'

# Create an elb client
elb_client = boto3.client('elbv2', region_name=REGION)

# defining ALB attributes

alb_name = "assignment-alb"
subnets = ['subnet-05a15ce69d2d9f69d','subnet-076051ff9276a558d','subnet-0564d17c714b6a55a']
security_groups = ['sg-09e0c5dd41f4bd5b9']


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