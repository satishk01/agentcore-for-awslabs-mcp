#!/usr/bin/env python3
"""
Update existing AgentCore execution role with Cost Explorer permissions
"""
import boto3
import json
import sys
from boto3.session import Session

print("=" * 60)
print("Update AgentCore Role with Cost Explorer Permissions")
print("=" * 60)
print()

# Get AWS region
boto_session = Session()
region = boto_session.region_name
account_id = boto3.client("sts").get_caller_identity()["Account"]

print(f"AWS Region: {region}")
print(f"Account ID: {account_id}")
print()

# The role name created by the SDK
role_name = f"AmazonBedrockAgentCoreSDKRuntime-{region}-0bb4d60a78"

print(f"Updating IAM role: {role_name}")
print()

iam_client = boto3.client("iam")

# Check if role exists
try:
    iam_client.get_role(RoleName=role_name)
    print(f"✓ Found role: {role_name}")
except iam_client.exceptions.NoSuchEntityException:
    print(f"✗ Error: Role {role_name} not found")
    print("Please run deployment first: python3 deploy.py")
    sys.exit(1)

# Cost Explorer policy
cost_explorer_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CostExplorerAccess",
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetCostForecast",
                "ce:GetAnomalies",
                "ce:GetSavingsPlansCoverage",
                "ce:GetReservationCoverage",
                "ce:GetReservationUtilization",
                "ce:GetSavingsPlansUtilization",
                "ce:GetDimensionValues",
                "ce:GetTags"
            ],
            "Resource": "*"
        }
    ]
}

# Add the policy to the role
policy_name = "CostExplorerAccessPolicy"

try:
    # Check if policy already exists
    try:
        existing_policy = iam_client.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )
        print(f"⚠ Policy {policy_name} already exists, updating...")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Adding new policy: {policy_name}")
    
    # Put (create or update) the policy
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(cost_explorer_policy)
    )
    
    print(f"✓ Successfully added Cost Explorer permissions to role")
    print()
    print("=" * 60)
    print("Permissions Added:")
    print("=" * 60)
    for action in cost_explorer_policy["Statement"][0]["Action"]:
        print(f"  ✓ {action}")
    
    print()
    print("=" * 60)
    print("✓ Role update completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Wait 10-15 seconds for IAM propagation")
    print("  2. Test Cost Explorer tools: python3 test_cost_explorer_tools.py")
    print()
    
except Exception as e:
    print(f"✗ Error updating role: {e}")
    sys.exit(1)
