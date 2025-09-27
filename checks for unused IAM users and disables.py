# Step 1: Create the Python Script (disable_unused_iam_users.py)
import boto3
from datetime import datetime, timedelta

AWS_REGION = "us-east-1"
DAYS_INACTIVE = 90

iam_client = boto3.client("iam", region_name=AWS_REGION)

def get_unused_iam_users():
    users = iam_client.list_users()["Users"]
    unused_users = []
    for user in users:
        user_name = user["UserName"]
        try:
            user_info = iam_client.get_user(UserName=user_name)
            last_login = user_info["User"].get("PasswordLastUsed", None)
            if not last_login:
                unused_users.append(user_name)
                continue
            last_login_date = last_login.replace(tzinfo=None)
            if last_login_date < datetime.utcnow() - timedelta(days=DAYS_INACTIVE):
                unused_users.append(user_name)
        except Exception as e:
            print(f"⚠️ Error retrieving info for {user_name}: {e}")
    return unused_users

def disable_users(users):
    if not users:
        print("✅ No unused IAM users found.")
        return
    for user in users:
        try:
            iam_client.update_login_profile(UserName=user, PasswordResetRequired=True)
            print(f"🛑 Disabled IAM user: {user}")
        except Exception as e:
            print(f"⚠️ Could not disable {user}: {e}")

if __name__ == "__main__":
    print(f"🔍 Checking for IAM users inactive for {DAYS_INACTIVE} days...")
    unused_users = get_unused_iam_users()
    if unused_users:
        print(f"⚠️ Found unused users: {unused_users}")
        disable_users(unused_users)
    else:
        print("✅ No inactive users found.")
