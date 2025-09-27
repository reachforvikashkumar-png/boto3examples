# Step 1: Create the Python Script (s3_lifecycle.py)
import boto3
import os

os.environ['AWS_PROFILE'] = "my-profile" # Replace with your profile name
os.environ['AWS_DEFAULT_REGION'] = "eu-west-1"

AWS_REGION = "eu-west-1"
BUCKET_NAME = "mys3bucketfortestingpurpose5818"
LIFECYCLE_RULE_NAME = "MoveToGlacier123"

s3_client = boto3.client("s3", region_name=AWS_REGION)

def apply_s3_lifecycle_policy():
    lifecycle_policy = {
        "Rules": [
            {
                "ID": LIFECYCLE_RULE_NAME,
                "Prefix": "",
                "Status": "Enabled",
                "Transitions": [
                    {
                        "Days": 30,
                        "StorageClass": "GLACIER"
                    }
                ],
                "NoncurrentVersionTransitions": [
                    {
                        "NoncurrentDays": 30,
                        "StorageClass": "GLACIER"
                    }
                ]
            }
        ]
    }
    try:
        response = s3_client.put_bucket_lifecycle_configuration(
            Bucket=BUCKET_NAME,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"✅ S3 Lifecycle policy applied successfully to '{BUCKET_NAME}'")
    except Exception as e:
        print(f"❌ Failed to apply lifecycle policy: {e}")

apply_s3_lifecycle_policy()
