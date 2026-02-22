#!/usr/bin/env python3
"""
Step 2: Deploy MCP Server to AgentCore Runtime
Retrieves Cognito config from SSM and deploys the MCP server to AWS AgentCore
"""
import os
import sys
import boto3
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime

print("=" * 60)
print("STEP 2: Deploy MCP Server to AgentCore Runtime")
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

# Retrieve Cognito config from SSM Parameter Store
print("Retrieving Cognito configuration from SSM Parameter Store...")
ssm_client = boto3.client('ssm', region_name=region)

try:
    client_id_response = ssm_client.get_parameter(Name='/mcp_server/cognito/client_id')
    client_id = client_id_response['Parameter']['Value']
    
    discovery_url_response = ssm_client.get_parameter(Name='/mcp_server/cognito/discovery_url')
    discovery_url = discovery_url_response['Parameter']['Value']
    
    print("✓ Retrieved Cognito configuration from SSM")
    print(f"  Client ID: {client_id}")
    print()
    
except ssm_client.exceptions.ParameterNotFound as e:
    print(f"✗ Error: Cognito configuration not found in SSM Parameter Store")
    print("Please run: python3 setup-cognito-pool.py first")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error retrieving Cognito configuration: {e}")
    sys.exit(1)

# Verify required files
print("Verifying required files...")
required_files = ['mcp_server.py', 'requirements.txt']
for file in required_files:
    if not os.path.exists(file):
        print(f"✗ Error: Required file {file} not found")
        sys.exit(1)
print("✓ All required files found")
print()

# Configure AgentCore Runtime
tool_name = "mcp_math_tools"
agentcore_runtime = Runtime()

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [client_id],
        "discoveryUrl": discovery_url,
    }
}

print("Configuring AgentCore Runtime...")
try:
    response = agentcore_runtime.configure(
        entrypoint="mcp_server.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        authorizer_configuration=auth_config,
        protocol="MCP",
        agent_name=tool_name
    )
    print("✓ Configuration completed")
except Exception as e:
    print(f"✗ Error during configuration: {e}")
    sys.exit(1)

print()
print("Launching MCP server to AgentCore Runtime...")
print("⏳ This may take several minutes (building Docker image)...")
print()

# Retry logic for IAM propagation
import time
max_retries = 3
retry_delay = 30  # seconds

for attempt in range(1, max_retries + 1):
    try:
        launch_result = agentcore_runtime.launch()
        print("✓ Launch completed")
        print()
        print("=" * 60)
        print("Deployment Results:")
        print("=" * 60)
        print(f"Agent ARN: {launch_result.agent_arn}")
        print(f"Agent ID: {launch_result.agent_id}")
        print()
        
        # Store Agent ARN in SSM Parameter Store
        print("Storing Agent ARN in SSM Parameter Store...")
        ssm_client.put_parameter(
            Name='/mcp_server/runtime/agent_arn',
            Value=launch_result.agent_arn,
            Type='String',
            Description='Agent ARN for MCP server',
            Overwrite=True
        )
        print("✓ Agent ARN stored in SSM")
        
        print()
        print("=" * 60)
        print("✓ Deployment completed successfully!")
        print("=" * 60)
        print()
        print("All credentials are now stored in SSM Parameter Store:")
        print("  /mcp_server/cognito/pool_id")
        print("  /mcp_server/cognito/client_id")
        print("  /mcp_server/cognito/bearer_token")
        print("  /mcp_server/cognito/refresh_token")
        print("  /mcp_server/cognito/discovery_url")
        print("  /mcp_server/runtime/agent_arn")
        print()
        print("Next step: python3 my_mcp_client_remote.py")
        break  # Success, exit retry loop
        
    except Exception as e:
        error_msg = str(e)
        if "AssumeRole" in error_msg and attempt < max_retries:
            print(f"⚠ IAM role propagation in progress (attempt {attempt}/{max_retries})")
            print(f"  Waiting {retry_delay} seconds for IAM to propagate...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        else:
            print(f"✗ Error during launch: {e}")
            if "AssumeRole" in error_msg:
                print()
                print("💡 Troubleshooting:")
                print("  The IAM roles were just created and may need more time to propagate.")
                print("  Wait 1-2 minutes and try running this command again:")
                print("  python3 deploy.py")
            sys.exit(1)