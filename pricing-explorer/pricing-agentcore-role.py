#!/usr/bin/env python3
"""
Update AgentCore IAM Role with AWS Pricing API Permissions
"""
import boto3
import json
import sys
from boto3.session import Session

print("=" * 60)
print("Update AgentCore Role with Pricing API Permissions")
print("=" * 60)
print()

# Get AWS region and account
boto_session = Session()
region = boto_session.region_name
sts_client = boto3.client('sts')
account_id = sts_client.get_caller_identity()['Account']

if not region:
    print("✗ Error: AWS region not configured")
    sys.exit(1)

print(f"AWS Region: {region}")
print(f"Account ID: {account_id}")
print()

# Get the AgentCore role name from SSM or find it
ssm_client = boto3.client('ssm', region_name=region)
iam_client = boto3.client('iam')

# Try to get role name from SSM (stored during deployment)
try:
    # List all roles and find the AgentCore runtime role
    roles = iam_client.list_roles()
    agentcore_role = None
    
    for role in roles['Roles']:
        if 'AmazonBedrockAgentCoreSDKRuntime' in role['RoleName']:
            agentcore_role = role['RoleName']
            break
    
    if not agentcore_role:
        print("✗ Error: Could not find AgentCore runtime role")
        print("Please ensure you have deployed an agent to AgentCore first")
        sys.exit(1)
    
    print(f"Found AgentCore Role: {agentcore_role}")
    print()
    
except Exception as e:
    print(f"✗ Error finding AgentCore role: {e}")
    sys.exit(1)

# Define the Pricing API permissions policy
pricing_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PricingAPIAccess",
            "Effect": "Allow",
            "Action": [
                "pricing:DescribeServices",
                "pricing:GetAttributeValues",
                "pricing:GetProducts"
            ],
            "Resource": "*"
        }
    ]
}

# Add the policy to the role
policy_name = "PricingAPIAccessPolicy"

try:
    print(f"Adding {policy_name} to role {agentcore_role}...")
    
    iam_client.put_role_policy(
        RoleName=agentcore_role,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(pricing_policy)
    )
    
    print(f"✓ Successfully added {policy_name}")
    print()
    print("=" * 60)
    print("✓ Permissions updated successfully!")
    print("=" * 60)
    print()
    print("The AgentCore role now has permissions to:")
    print("  - pricing:DescribeServices")
    print("  - pricing:GetAttributeValues")
    print("  - pricing:GetProducts")
    print()
    print("You can now deploy the pricing MCP server:")
    print("  python3 deploy-pricing.py")
    
except Exception as e:
    print(f"✗ Error adding policy: {e}")
    sys.exit(1)
