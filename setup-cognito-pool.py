#!/usr/bin/env python3
"""
Step 1: Setup Cognito User Pool
Creates a Cognito User Pool with test user and stores credentials in SSM Parameter Store
"""
from utils import setup_cognito_user_pool
import boto3
import sys
from boto3.session import Session

print("=" * 60)
print("STEP 1: Setting up Amazon Cognito User Pool")
print("=" * 60)
print()

# Get AWS region
boto_session = Session()
region = boto_session.region_name

if not region:
    print("✗ Error: AWS region not configured")
    sys.exit(1)

print(f"Using AWS region: {region}")
print()

print("Creating Cognito User Pool...")
cognito_config = setup_cognito_user_pool()

if not cognito_config:
    print("✗ Error: Failed to setup Cognito user pool")
    sys.exit(1)

print()
print("=" * 60)
print("✓ Cognito User Pool created successfully!")
print("=" * 60)
print()
print("Cognito Configuration:")
print(f"  User Pool ID: {cognito_config.get('pool_id', 'N/A')}")
print(f"  Client ID: {cognito_config.get('client_id', 'N/A')}")
print(f"  Discovery URL: {cognito_config.get('discovery_url', 'N/A')}")
print()
print("Test User Credentials:")
print("  Username: testuser")
print("  Password: MyPassword123!")
print()

# Store credentials in SSM Parameter Store
print("Storing Cognito credentials in SSM Parameter Store...")
ssm_client = boto3.client('ssm', region_name=region)

try:
    ssm_client.put_parameter(
        Name='/mcp_server/cognito/pool_id',
        Value=cognito_config['pool_id'],
        Type='String',
        Description='Cognito Pool ID for MCP server',
        Overwrite=True
    )
    print("✓ Cognito Pool ID stored in SSM")

    ssm_client.put_parameter(
        Name='/mcp_server/cognito/client_id',
        Value=cognito_config['client_id'],
        Type='String',
        Description='Cognito Client ID for MCP server',
        Overwrite=True
    )
    print("✓ Cognito Client ID stored in SSM")

    ssm_client.put_parameter(
        Name='/mcp_server/cognito/bearer_token',
        Value=cognito_config['bearer_token'],
        Type='SecureString',
        Description='Cognito Bearer Token for MCP server',
        Overwrite=True
    )
    print("✓ Cognito Bearer Token stored in SSM (encrypted)")

    ssm_client.put_parameter(
        Name='/mcp_server/cognito/refresh_token',
        Value=cognito_config['refresh_token'],
        Type='SecureString',
        Description='Cognito Refresh Token for MCP server',
        Overwrite=True
    )
    print("✓ Cognito Refresh Token stored in SSM (encrypted)")

    ssm_client.put_parameter(
        Name='/mcp_server/cognito/discovery_url',
        Value=cognito_config['discovery_url'],
        Type='String',
        Description='Cognito Discovery URL for MCP server',
        Overwrite=True
    )
    print("✓ Cognito Discovery URL stored in SSM")

    print()
    print("=" * 60)
    print("✓ All Cognito credentials stored in SSM Parameter Store!")
    print("=" * 60)
    print()
    print("Next step: python3 deploy.py")

except Exception as e:
    print(f"✗ Error storing credentials in SSM: {e}")
    sys.exit(1)