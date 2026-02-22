#!/usr/bin/env python3
"""
Streamlit App for AWS Pricing MCP Agent with Claude Haiku via Bedrock
Intelligent assistant for AWS pricing queries and cost planning
"""
import streamlit as st
import asyncio
import boto3
import json
from datetime import datetime, timedelta
from boto3.session import Session
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AWS Pricing AI Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .price-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .price-amount {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .comparison-box {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .analysis-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .savings-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'tools' not in st.session_state:
    st.session_state.tools = []

# Initialize Bedrock client
@st.cache_resource
def get_bedrock_client():
    """Initialize Bedrock Runtime client with IAM role"""
    return boto3.client('bedrock-runtime', region_name='us-east-1')

# Helper function to get credentials from SSM
@st.cache_data(ttl=3600)
def get_credentials():
    """Retrieve credentials from SSM Parameter Store"""
    try:
        boto_session = Session()
        region = boto_session.region_name
        ssm_client = boto3.client('ssm', region_name=region)
        
        agent_arn = ssm_client.get_parameter(Name='/mcp_pricing_server/runtime/agent_arn')['Parameter']['Value']
        bearer_token = ssm_client.get_parameter(Name='/mcp_server/cognito/bearer_token', WithDecryption=True)['Parameter']['Value']
        
        return {
            'region': region,
            'agent_arn': agent_arn,
            'bearer_token': bearer_token
        }
    except Exception as e:
        st.error(f"Error retrieving credentials: {e}")
        return None

# Helper function to refresh bearer token
def refresh_bearer_token():
    """Refresh the Cognito bearer token using refresh token"""
    try:
        boto_session = Session()
        region = boto_session.region_name
        ssm_client = boto3.client('ssm', region_name=region)
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        client_id = ssm_client.get_parameter(Name='/mcp_server/cognito/client_id')['Parameter']['Value']
        refresh_token = ssm_client.get_parameter(Name='/mcp_server/cognito/refresh_token', WithDecryption=True)['Parameter']['Value']
        
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={'REFRESH_TOKEN': refresh_token}
        )
        
        new_bearer_token = response['AuthenticationResult']['AccessToken']
        
        ssm_client.put_parameter(
            Name='/mcp_server/cognito/bearer_token',
            Value=new_bearer_token,
            Type='SecureString',
            Overwrite=True
        )
        
        get_credentials.clear()
        return True
    except Exception as e:
        st.error(f"Error refreshing token: {e}")
        return False

# Helper function to connect to MCP server
async def connect_to_mcp():
    """Connect to the MCP server and list available tools"""
    try:
        creds = get_credentials()
        if not creds:
            st.error("Failed to retrieve credentials from SSM")
            return False, []
        
        region = creds['region']
        agent_arn = creds['agent_arn']
        bearer_token = creds['bearer_token']
        
        encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
        mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        headers = {
            "authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with streamablehttp_client(mcp_url, headers, timeout=timedelta(seconds=120), terminate_on_close=False) as (
                read_stream, write_stream, _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tool_result = await session.list_tools()
                    tools = [{"name": tool.name, "description": tool.description} for tool in tool_result.tools]
                    return True, tools
        except Exception as conn_error:
            import traceback
            error_details = traceback.format_exc()
            st.error(f"MCP Connection error: {str(conn_error)}")
            with st.expander("🔍 Debug: Full Error Details"):
                st.code(error_details)
            return False, []
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Connection error: {str(e)}")
        with st.expander("🔍 Debug: Full Error Details"):
            st.code(error_details)
        return False, []

# Helper function to call a tool
async def call_tool(tool_name, arguments):
    """Call a specific MCP tool"""
    try:
        creds = get_credentials()
        if not creds:
            return json.dumps({"error": "Failed to retrieve credentials"})
        
        region = creds['region']
        agent_arn = creds['agent_arn']
        bearer_token = creds['bearer_token']
        
        encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
        mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        headers = {
            "authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with streamablehttp_client(mcp_url, headers, timeout=timedelta(seconds=120), terminate_on_close=False) as (
                read_stream, write_stream, _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(name=tool_name, arguments=arguments)
                    return result.content[0].text
        except Exception as tool_error:
            import traceback
            error_details = traceback.format_exc()
            return json.dumps({
                "error": f"Tool call failed: {str(tool_error)}",
                "details": error_details
            })
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return json.dumps({
            "error": f"Error: {str(e)}",
            "details": error_details
        })

# Claude-powered intelligent assistant using Bedrock
async def intelligent_pricing_assistant(user_query):
    """Use Claude via Bedrock to orchestrate pricing tool calls and provide analysis"""
    
    bedrock = get_bedrock_client()
    
    # System prompt for Claude with pricing tool descriptions
    system_prompt = """You are an intelligent AWS Pricing Assistant with access to AWS Pricing API tools.

AVAILABLE TOOLS:

1. get_service_codes()
   - Returns: List of all AWS service codes
   - Use: To discover available services

2. get_ec2_instance_pricing(instance_type, region, operating_system, tenancy, preinstalled_sw)
   - Returns: Pricing for specific EC2 instance
   - Use: EC2 instance price lookups
   - Params: instance_type (e.g., "t3.micro"), region (e.g., "US East (N. Virginia)"), 
            operating_system ("Linux"/"Windows"), tenancy ("Shared"/"Dedicated"), 
            preinstalled_sw ("NA"/"SQL Std"/"SQL Web"/"SQL Ent")

3. get_rds_instance_pricing(instance_type, database_engine, region, deployment_option)
   - Returns: RDS database pricing
   - Use: Database instance price lookups
   - Params: instance_type (e.g., "db.t3.micro"), database_engine ("MySQL"/"PostgreSQL"/"Oracle"/"SQL Server"),
            region, deployment_option ("Single-AZ"/"Multi-AZ")

4. get_s3_pricing(region)
   - Returns: S3 storage pricing
   - Use: S3 storage cost lookups
   - Params: region

5. compare_instance_prices(instance_types, region, operating_system)
   - Returns: Price comparison for multiple instances
   - Use: Comparing multiple EC2 instance types
   - Params: instance_types (list), region, operating_system

6. calculate_monthly_cost(hourly_price, hours_per_day, days_per_month)
   - Returns: Monthly/annual cost calculations
   - Use: Converting hourly prices to monthly/annual costs
   - Params: hourly_price (float), hours_per_day (default 24), days_per_month (default 30)

7. get_attribute_values(service_code, attribute_name, max_results)
   - Returns: Available values for service attributes
   - Use: Discovering available options (regions, instance types, etc.)
   - Params: service_code (e.g., "AmazonEC2"), attribute_name (e.g., "location"), max_results

8. estimate_data_transfer_cost(data_transfer_gb, transfer_type, region)
   - Returns: Data transfer cost estimate
   - Use: Calculating data transfer costs (internet outbound, inter-region, intra-region)
   - Params: data_transfer_gb (float), transfer_type, region

9. estimate_api_gateway_cost(requests_per_month, api_type, cache_size_gb)
   - Returns: API Gateway cost estimate
   - Use: Calculating API Gateway costs for REST, HTTP, or WebSocket APIs
   - Params: requests_per_month (int), api_type ("REST"/"HTTP"/"WebSocket"), cache_size_gb (optional)

10. estimate_lambda_cost(invocations_per_month, memory_mb, avg_duration_ms)
    - Returns: Lambda cost estimate
    - Use: Calculating Lambda function costs
    - Params: invocations_per_month (int), memory_mb (int), avg_duration_ms (int)

11. estimate_dynamodb_cost(storage_gb, read_requests_per_month, write_requests_per_month, pricing_model)
    - Returns: DynamoDB cost estimate
    - Use: Calculating DynamoDB costs
    - Params: storage_gb (float), read/write requests (int), pricing_model ("on_demand"/"provisioned")

ARCHITECTURAL PRICING GUIDELINES:

For MULTI-SERVICE ARCHITECTURES:
1. Break down the architecture into individual components
2. Price each component separately using appropriate tools
3. Sum up all component costs
4. Add data transfer costs between services
5. Include monitoring and logging costs (CloudWatch ~$0.50/GB ingested, $0.03/GB stored)
6. Consider data storage costs (S3, EBS, RDS storage)

For BEDROCK/AGENTCORE SOLUTIONS:
- AgentCore Runtime: Serverless, pay per invocation (~$0.00002 per invocation)
- AgentCore Gateway: Pay per API call (~$0.000001 per call)
- Bedrock models: Pay per token (Claude Haiku ~$0.25/1M input tokens, ~$1.25/1M output tokens)
- Lambda preprocessing: Use estimate_lambda_cost()
- DynamoDB state: Use estimate_dynamodb_cost()

For ECS/CONTAINER SOLUTIONS:
- ECS Fargate: Price by vCPU-hour and GB-hour
  * 1 vCPU = $0.04048/hour, 1 GB = $0.004445/hour
- Load Balancers: ALB ~$22.50/month + $0.008/LCU-hour, NLB ~$22.50/month + $0.006/NLCU-hour
- ECR storage: $0.10/GB-month
- Data transfer: Use estimate_data_transfer_cost()

For SERVERLESS SOLUTIONS:
- Lambda: Use estimate_lambda_cost()
- API Gateway: Use estimate_api_gateway_cost()
- DynamoDB: Use estimate_dynamodb_cost()
- S3: Use get_s3_pricing()
- EventBridge: $1.00 per million events
- Step Functions: $25 per million state transitions (Standard)

For COMPLETE SOLUTIONS:
1. Identify all AWS services in the architecture
2. Price compute resources (EC2, ECS, Lambda)
3. Price databases (RDS, DynamoDB, Aurora)
4. Price storage (S3, EBS, EFS)
5. Price networking (Load Balancers, NAT Gateway, data transfer)
6. Price API/integration services (API Gateway, EventBridge)
7. Price monitoring (CloudWatch, X-Ray)
8. Sum all components for total monthly cost

COST OPTIMIZATION RECOMMENDATIONS:
- Suggest Reserved Instances for steady-state workloads (30-70% savings)
- Recommend Spot Instances for fault-tolerant workloads (up to 90% savings)
- Suggest right-sizing based on actual usage patterns
- Recommend S3 Intelligent-Tiering for variable access patterns
- Suggest Aurora Serverless for variable database workloads
- Recommend Lambda for sporadic workloads vs always-on containers

TOOL SELECTION GUIDELINES:
- For EC2 pricing: Use get_ec2_instance_pricing()
- For RDS pricing: Use get_rds_instance_pricing()
- For S3 pricing: Use get_s3_pricing()
- For comparisons: Use compare_instance_prices()
- For cost calculations: Use calculate_monthly_cost()
- For data transfer: Use estimate_data_transfer_cost()
- For API Gateway: Use estimate_api_gateway_cost()
- For Lambda: Use estimate_lambda_cost()
- For DynamoDB: Use estimate_dynamodb_cost()
- Always provide context and recommendations with pricing data
- For complex architectures, call multiple tools and sum the costs

IMPORTANT:
- Pricing API only works in us-east-1 region
- Region names use full names (e.g., "US East (N. Virginia)" not "us-east-1")
- Always calculate monthly/annual costs for better context
- Provide cost optimization recommendations when relevant"""
    
    # Ask Claude to plan which tools to call
    planning_messages = [
        {
            "role": "user",
            "content": f"""User question: "{user_query}"

Based on this pricing question, which tools should you call and with what parameters?

Respond with a JSON array of tool calls:
[
    {{"tool": "get_ec2_instance_pricing", "args": {{"instance_type": "t3.micro", "region": "US East (N. Virginia)", "operating_system": "Linux", "tenancy": "Shared", "preinstalled_sw": "NA"}}}},
    {{"tool": "calculate_monthly_cost", "args": {{"hourly_price": 0.0104, "hours_per_day": 24, "days_per_month": 30}}}}
]

Only include the tools needed to answer the question."""
        }
    ]
    
    # Get Claude's tool selection
    planning_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": planning_messages
        })
    )
    
    planning_body = json.loads(planning_response['body'].read())
    planning_text = planning_body['content'][0]['text']
    
    # Extract tool calls from Claude's response
    import re
    json_match = re.search(r'\[.*\]', planning_text, re.DOTALL)
    tool_calls = []
    
    if json_match:
        try:
            planned_tools = json.loads(json_match.group())
            for tool_call in planned_tools:
                tool_name = tool_call.get('tool')
                tool_args = tool_call.get('args', {})
                if tool_name:
                    tool_calls.append((tool_name, tool_args))
        except Exception as e:
            st.warning(f"Could not parse tool plan: {e}")
    
    # Fallback if Claude didn't provide valid tool calls
    if not tool_calls:
        tool_calls = [('get_service_codes', {})]
    
    # Execute tool calls
    tool_results = {}
    for tool_name, args in tool_calls:
        result = await call_tool(tool_name, args)
        tool_results[tool_name] = result
    
    # Parse results
    parsed_results = []
    for tool_name, result in tool_results.items():
        try:
            data = json.loads(result)
            parsed_results.append(f"{tool_name}: {json.dumps(data, indent=2)}")
        except:
            parsed_results.append(f"{tool_name}: {result}")
    
    structured_summary = "\n\n".join(parsed_results)
    
    # Get Claude's final analysis
    final_messages = [
        {
            "role": "user",
            "content": f"""User question: "{user_query}"

PRICING DATA FROM AWS:
{structured_summary}

Provide a comprehensive pricing analysis that includes:
1. **Direct Answer**: Answer the specific pricing question
2. **Pricing Details**: Show all relevant prices clearly
3. **Cost Calculations**: Provide monthly/annual costs where relevant
4. **Comparison**: If comparing options, show clear comparison
5. **Recommendations**: Provide cost optimization suggestions
6. **Context**: Explain what the pricing means for the user

Format your response professionally and make it actionable."""
        }
    ]
    
    final_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": final_messages
        })
    )
    
    final_body = json.loads(final_response['body'].read())
    analysis = final_body['content'][0]['text']
    
    return tool_results, analysis

# Sidebar
with st.sidebar:
    st.title("💰 Pricing Assistant Controls")
    
    st.success("✅ Using AWS Bedrock (IAM Role)")
    st.caption("Claude Haiku 3 via Bedrock")
    
    st.divider()
    
    # Token refresh button
    if st.button("🔄 Refresh Token", key="refresh_token_btn", use_container_width=True):
        with st.spinner("Refreshing bearer token..."):
            if refresh_bearer_token():
                st.success("✅ Token refreshed successfully!")
                st.info("Please reconnect to MCP Agent")
            else:
                st.error("❌ Failed to refresh token")
    
    # Connection status
    if st.button("🔌 Connect to Pricing Agent", key="connect_btn", use_container_width=True):
        with st.spinner("Connecting..."):
            connected, tools = asyncio.run(connect_to_mcp())
            st.session_state.connected = connected
            st.session_state.tools = tools
    
    if st.session_state.connected:
        st.success("✅ Connected to Pricing Agent")
        st.metric("Available Tools", len(st.session_state.tools))
    else:
        st.warning("⚠️ Not connected")
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Queries")
    
    if st.button("💻 EC2 Pricing", key="ec2_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "What is the hourly price for a t3.micro instance running Linux in US East (N. Virginia)? Calculate the monthly cost."
        })
        st.rerun()
    
    if st.button("🔄 Compare Instances", key="compare_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Compare the pricing for t3.micro, t3.small, and t3.medium instances in US East."
        })
        st.rerun()
    
    if st.button("🗄️ RDS Pricing", key="rds_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "What's the cost for a db.t3.micro MySQL database in US East? Compare Single-AZ vs Multi-AZ."
        })
        st.rerun()
    
    if st.button("📦 S3 Pricing", key="s3_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "What are the S3 storage costs in US East (N. Virginia)?"
        })
        st.rerun()
    
    if st.button("🌍 Regional Comparison", key="regional_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Compare the price of an m5.large instance in US East, US West, and EU Ireland."
        })
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", key="clear_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("💰 AWS Pricing AI Assistant")
st.markdown("Ask questions about AWS pricing and get intelligent cost analysis")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about AWS pricing..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        if not st.session_state.connected:
            st.warning("⚠️ Not connected to pricing agent. Please connect first.")
            response = "Please connect to the pricing agent first using the button in the sidebar."
        else:
            with st.spinner("💰 Analyzing pricing data..."):
                try:
                    tool_results, analysis = asyncio.run(intelligent_pricing_assistant(prompt))
                    
                    # Display analysis
                    st.markdown(f"""
                    <div class="analysis-box">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show raw data in expander
                    with st.expander("🔍 View Raw Pricing Data"):
                        for tool_name, result in tool_results.items():
                            st.subheader(tool_name)
                            try:
                                data = json.loads(result)
                                st.json(data)
                            except:
                                st.code(result)
                    
                    response = analysis
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    response = f"I encountered an error: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("💰 AWS Pricing API")
with col2:
    st.caption("🤖 Powered by Claude Haiku (Bedrock)")
with col3:
    st.caption("🔒 IAM Role-based access")
