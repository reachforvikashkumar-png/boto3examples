# Step 1: Install Required Dependencies
# pip install boto3 paramiko

# I am using my_profile and not using the default profile you can see your profile in by running command cat ~/.aws/credentials


import boto3
import paramiko
import time
import os

os.environ['AWS_PROFILE'] = "my-profile" # Replace with your profile name
os.environ['AWS_DEFAULT_REGION'] = "eu-west-1"

# AWS Configuration
AWS_REGION = "eu-west-1"
INSTANCE_TYPE = "t2.micro"
AMI_ID = "ami-0bc"  # Replace with a valid AMI ID
SECURITY_GROUP_NAME = "my-ec2-security-group"
VPC_ID = "vpc-0fb" # Replace with your VPC ID
SUBNET_ID = "subnet-000" # Replace with your subnet ID
KEY_PAIR_NAME = "my-ec2-keypair"
SSH_USERNAME = "ubuntu"  # Change based on AMI

# Initialize AWS Clients
ec2_client = boto3.client("ec2", region_name=AWS_REGION)
ec2_resource = boto3.resource("ec2", region_name=AWS_REGION)

def create_key_pair():
    print("🔑 Creating key pair...")
    key_pair = ec2_client.create_key_pair(KeyName=KEY_PAIR_NAME)
    with open(f"{KEY_PAIR_NAME}.pem", "w") as file:
        file.write(key_pair["KeyMaterial"])
    print(f"✅ Key pair '{KEY_PAIR_NAME}' created and saved as '{KEY_PAIR_NAME}.pem'")
    return f"{KEY_PAIR_NAME}.pem"

def create_security_group():
    print("🔐 Creating security group...")
    response = ec2_client.create_security_group(
        GroupName=SECURITY_GROUP_NAME,
        VpcId=VPC_ID,
        Description="Security group for EC2 SSH access"
    )
    security_group_id = response["GroupId"]
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[{
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
        }]
    )
    print(f"✅ Security group '{SECURITY_GROUP_NAME}' created with ID {security_group_id}")
    return security_group_id

def launch_ec2_instance(security_group_id, key_name):
    print("🚀 Launching EC2 instance...")
    instance = ec2_resource.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "MyEC2Instance"}]
        }]
    )[0]
    instance.wait_until_running()
    instance.reload()
    print(f"✅ EC2 instance launched with ID: {instance.id}")
    print(f"🌐 Public IP: {instance.public_ip_address}")
    return instance.id, instance.public_ip_address

def check_ec2_via_ssh(instance_ip, key_file):
    print("🔍 Connecting to EC2 instance via SSH...")
    private_key = paramiko.RSAKey(filename=key_file)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=instance_ip, username=SSH_USERNAME, pkey=private_key, timeout=30)
        stdin, stdout, stderr = ssh_client.exec_command("uptime")
        print(f"✅ SSH Successful! Uptime: {stdout.read().decode().strip()}")
    except Exception as e:
        print(f"❌ SSH Connection Failed: {e}")
    finally:
        ssh_client.close()

if __name__ == "__main__":
    key_file = create_key_pair()
    security_group_id = create_security_group()
    instance_id, instance_ip = launch_ec2_instance(security_group_id, KEY_PAIR_NAME)
    print("⏳ Waiting for EC2 instance to initialize...")
    time.sleep(60)
    check_ec2_via_ssh(instance_ip, key_file)
