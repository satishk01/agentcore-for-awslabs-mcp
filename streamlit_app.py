#!/usr/bin/env python3
"""
Streamlit App for AWS Cost Explorer MCP Agent with Claude Haiku via Bedrock
Intelligent assistant that orchestrates multiple tool calls and provides analysis
Uses AWS Bedrock (IAM role-based) instead of Anthropic API
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
    page_title="AWS Cost Explorer AI Assistant",
    page_icon="🤖",
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .cost-amount {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .insight-box {
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
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .success-box {
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

# Helper functions for data formatting
def parse_cost_response(result_text):
    """Parse JSON response and extract meaningful data"""
    try:
        data = json.loads(result_text)
        if 'error' in data:
            return None, data['error']
        if 'ResultsByTime' in data or 'ForecastResultsByTime' in data:
            return data, None
        return data, None
    except json.JSONDecodeError:
        return None, "Unable to parse response"
    except Exception as e:
        return None, str(e)

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"${float(amount):,.2f}"
    except:
        return amount

def extract_cost_from_data(data):
    """Extract total cost from cost data"""
    if not data:
        return 0
    
    try:
        if 'ResultsByTime' in data:
            results = data['ResultsByTime']
            total = 0
            for r in results:
                # First try to get from Total (ungrouped data)
                if 'Total' in r and 'UnblendedCost' in r['Total']:
                    total += float(r['Total']['UnblendedCost']['Amount'])
                # If grouped by service, sum up all groups
                elif 'Groups' in r:
                    for group in r['Groups']:
                        if 'Metrics' in group and 'UnblendedCost' in group['Metrics']:
                            total += float(group['Metrics']['UnblendedCost']['Amount'])
            return total
        elif 'ForecastResultsByTime' in data:
            results = data['ForecastResultsByTime']
            total = 0
            for r in results:
                if 'MeanValue' in r:
                    total += float(r['MeanValue'])
            return total
    except (KeyError, ValueError, TypeError) as e:
        st.warning(f"Error extracting cost: {e}")
        return 0
    
    return 0

def display_cost_summary(data, title="Cost Summary"):
    """Display cost summary in a professional format"""
    if not data or 'ResultsByTime' not in data:
        return 0
    
    results = data['ResultsByTime']
    total_cost = extract_cost_from_data(data)
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.2em; opacity: 0.9;">{title}</div>
        <div class="cost-amount">{format_currency(total_cost)}</div>
        <div style="opacity: 0.8;">Period: {results[0]['TimePeriod']['Start']} to {results[-1]['TimePeriod']['End']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    return total_cost

def display_cost_by_service(data, limit=5):
    """Display costs grouped by service"""
    if not data or 'ResultsByTime' not in data:
        return {}
    
    results = data['ResultsByTime']
    service_costs = {}
    
    try:
        for result in results:
            if 'Groups' in result:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    # Handle different metric structures
                    if 'Metrics' in group and 'UnblendedCost' in group['Metrics']:
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    elif 'UnblendedCost' in group:
                        amount = float(group['UnblendedCost']['Amount'])
                    else:
                        continue
                    service_costs[service] = service_costs.get(service, 0) + amount
    except (KeyError, ValueError, TypeError) as e:
        st.error(f"Error parsing service costs: {e}")
        return {}
    
    if not service_costs:
        st.info("No service cost data available")
        return {}
    
    sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
    total_cost = sum(service_costs.values())
    
    st.subheader(f"🏢 Top {limit} Services by Cost")
    
    if sorted_services:
        service_data = []
        for i, (service, cost) in enumerate(sorted_services[:limit], 1):
            percentage = (cost / total_cost) * 100 if total_cost > 0 else 0
            service_data.append({
                'Rank': i,
                'Service': service,
                'Cost': format_currency(cost),
                'Percentage': f"{percentage:.1f}%"
            })
        
        df = pd.DataFrame(service_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    return dict(sorted_services[:limit])

# Helper function to get credentials from SSM
@st.cache_data(ttl=3600)
def get_credentials():
    """Retrieve credentials from SSM Parameter Store"""
    try:
        boto_session = Session()
        region = boto_session.region_name
        ssm_client = boto3.client('ssm', region_name=region)
        
        agent_arn = ssm_client.get_parameter(Name='/mcp_server/runtime/agent_arn')['Parameter']['Value']
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
        
        # Get stored credentials
        client_id = ssm_client.get_parameter(Name='/mcp_server/cognito/client_id')['Parameter']['Value']
        refresh_token = ssm_client.get_parameter(Name='/mcp_server/cognito/refresh_token', WithDecryption=True)['Parameter']['Value']
        
        # Refresh the token
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        new_bearer_token = response['AuthenticationResult']['AccessToken']
        
        # Update SSM with new token
        ssm_client.put_parameter(
            Name='/mcp_server/cognito/bearer_token',
            Value=new_bearer_token,
            Type='SecureString',
            Overwrite=True
        )
        
        # Clear the cache so next call gets new token
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
async def intelligent_assistant(user_query):
    """Use Claude via Bedrock to orchestrate multiple tool calls and provide intelligent analysis"""
    
    bedrock = get_bedrock_client()
    
    # Get today's date first for context
    today_result = await call_tool('get_today_date', {})
    today_data, _ = parse_cost_response(today_result)
    
    # System prompt for Claude with comprehensive tool descriptions
    system_prompt = """You are an intelligent AWS Cost Analysis Assistant with access to AWS Cost Explorer tools.

AVAILABLE TOOLS:

1. get_today_date() 
   - Returns: current date, current/last month names and date ranges
   - Use: Always call first to understand date context

2. get_current_month_cost()
   - Returns: Cost data for current month to date
   - Use: "current month", "this month", "month to date"

3. get_last_month_cost()
   - Returns: Complete previous month cost data
   - Use: "last month", "previous month"

4. get_cost_by_service(start_date, end_date, granularity)
   - Returns: Costs grouped by AWS service
   - Use: Service breakdowns, top services, service-specific analysis
   - Params: dates (YYYY-MM-DD), granularity ("MONTHLY"/"DAILY")
   - Can call multiple times for different periods

5. get_cost_by_region(start_date, end_date, granularity)
   - Returns: Costs grouped by AWS region
   - Use: Regional analysis, multi-region cost distribution
   - Params: dates (YYYY-MM-DD), granularity ("MONTHLY"/"DAILY")

6. get_cost_comparison_drivers(period1_start, period1_end, period2_start, period2_end, top_n)
   - Returns: Top N services driving cost changes between periods
   - Use: Understanding what caused cost increases/decreases
   - Params: two period date ranges, top_n (default 10)
   - Can call multiple times for consecutive period comparisons

7. get_cost_and_usage(start_date, end_date, granularity, group_by)
   - Returns: Cost data for any date range, optionally grouped
   - Use: Historical months, quarters, custom date ranges
   - Params: dates (YYYY-MM-DD), granularity ("MONTHLY"/"DAILY"), 
            group_by (optional: [{"Type": "DIMENSION", "Key": "SERVICE"}])
   - NOTE: 14-month historical limit
   - Can call multiple times for different periods

8. get_cost_forecast(start_date, end_date, metric, granularity)
   - Returns: Forecasted future costs
   - Use: Future predictions, budget planning, "next month"
   - Params: future dates (YYYY-MM-DD), metric ("UNBLENDED_COST"), granularity ("MONTHLY")

9. get_dimension_values(dimension, start_date, end_date, search_string)
   - Returns: Available values for dimensions (SERVICE, REGION, LINKED_ACCOUNT, etc.)
   - Use: Discovering available services, regions, accounts
   - Params: dimension name, date range, optional search filter

10. get_tag_values(tag_key, start_date, end_date, search_string)
    - Returns: Available tag values for a specific tag key
    - Use: Tag-based cost analysis
    - Params: tag key name, date range, optional search filter

TOOL SELECTION GUIDELINES:

For MULTI-PERIOD COMPARISONS (e.g., "Oct, Nov, Dec"):
- Call get_cost_and_usage() once for EACH period
- Call get_cost_comparison_drivers() between consecutive periods
- Example: 3 months = 3 get_cost_and_usage calls + 2 comparison_drivers calls

For QUARTERLY ANALYSIS (e.g., "Q3 vs Q4"):
- Calculate quarter date ranges (Q3: Jul-Sep, Q4: Oct-Dec)
- Call get_cost_and_usage() for each quarter
- Call get_cost_comparison_drivers() to compare quarters

For DAILY ANALYSIS (e.g., "weekday vs weekend"):
- Use granularity="DAILY" in get_cost_and_usage()
- Call for the entire period needed

For SERVICE-SPECIFIC ANALYSIS:
- Use get_cost_by_service() for the relevant periods
- Can filter by calling multiple times for different date ranges

For REGIONAL ANALYSIS:
- Use get_cost_by_region() instead of get_cost_by_service()

For FORECASTING:
- Use get_cost_forecast() with future dates
- Can forecast multiple months by adjusting date ranges

For BUDGET ANALYSIS:
- Combine get_current_month_cost(), get_last_month_cost(), and get_cost_forecast()
- User provides budget number in question

For YEAR-OVER-YEAR:
- Call get_cost_and_usage() for same month in different years
- Example: Dec 2024 vs Dec 2025

IMPORTANT RULES:
1. Always call get_today_date() first
2. Choose the SIMPLEST tools that answer the question
3. For recent months (current/last), use simple tools (get_current_month_cost, get_last_month_cost)
4. For historical months, use get_cost_and_usage() with exact dates
5. Call tools multiple times if needed (e.g., 6 months = 6 calls)
6. Include group_by for service breakdowns when needed
7. Be efficient - don't call unnecessary tools"""
    
    # Ask Claude to plan which tools to call
    planning_messages = [
        {
            "role": "user",
            "content": f"""Today's date context: {json.dumps(today_data, indent=2)}

User question: "{user_query}"

Based on this question, which tools should you call and with what parameters?

Respond with a JSON array of tool calls:
[
    {{"tool": "get_current_month_cost", "args": {{}}}},
    {{"tool": "get_last_month_cost", "args": {{}}}},
    {{"tool": "get_cost_by_service", "args": {{"start_date": "2026-02-01", "end_date": "2026-02-21", "granularity": "MONTHLY"}}}}
]

Only include the tools needed to answer the question. Be minimal and efficient."""
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
        tool_calls = [
            ('get_current_month_cost', {}),
            ('get_last_month_cost', {})
        ]
    
    # Execute tool calls and parse the data
    tool_results = {}
    parsed_data = {
        'date_info': None,
        'periods': [],  # List of {name, cost, services}
        'cost_drivers': [],
        'forecast': None
    }
    
    period_counter = 0
    current_month_data = None
    last_month_data = None
    
    for tool_name, args in tool_calls:
        result = await call_tool(tool_name, args)
        tool_results[tool_name] = result
        
        # Parse the result immediately
        data, error = parse_cost_response(result)
        if data and not error:
            # Handle get_today_date
            if 'today_date' in tool_name or tool_name == 'get_today_date':
                parsed_data['date_info'] = data
            
            # Handle get_current_month_cost
            elif 'current_month_cost' in tool_name or tool_name == 'get_current_month_cost':
                if 'ResultsByTime' in data:
                    current_month_data = data
                    period_cost = extract_cost_from_data(data)
                    period_name = datetime.now().strftime('%B %Y')
                    parsed_data['periods'].append({
                        'name': period_name,
                        'cost': period_cost,
                        'services': []
                    })
            
            # Handle get_last_month_cost
            elif 'last_month_cost' in tool_name or tool_name == 'get_last_month_cost':
                if 'ResultsByTime' in data:
                    last_month_data = data
                    period_cost = extract_cost_from_data(data)
                    last_month = (datetime.now().replace(day=1) - timedelta(days=1))
                    period_name = last_month.strftime('%B %Y')
                    # Insert at beginning so last month comes before current month
                    parsed_data['periods'].insert(0, {
                        'name': period_name,
                        'cost': period_cost,
                        'services': []
                    })
            
            # Handle get_cost_by_service
            elif ('by_service' in tool_name or 'get_cost_by_service' in tool_name) and 'ResultsByTime' in data:
                services = []
                service_costs = {}
                for result_item in data['ResultsByTime']:
                    if 'Groups' in result_item:
                        for group in result_item['Groups']:
                            service = group['Keys'][0]
                            if 'Metrics' in group and 'UnblendedCost' in group['Metrics']:
                                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                                service_costs[service] = service_costs.get(service, 0) + amount
                
                sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:10]
                total_cost = sum(service_costs.values())
                
                for service, cost in sorted_services:
                    percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                    services.append({
                        'name': service,
                        'cost': cost,
                        'percentage': percentage
                    })
                
                # Add to most recent period or create new period
                if parsed_data['periods']:
                    parsed_data['periods'][-1]['services'] = services
                else:
                    # Create a period for this service data
                    period_name = "Service Breakdown"
                    if 'start_date' in args:
                        try:
                            date_obj = datetime.strptime(args['start_date'], '%Y-%m-%d')
                            period_name = date_obj.strftime('%B %Y')
                        except:
                            pass
                    parsed_data['periods'].append({
                        'name': period_name,
                        'cost': total_cost,
                        'services': services
                    })
            
            # Handle get_cost_by_region
            elif ('by_region' in tool_name or 'get_cost_by_region' in tool_name) and 'ResultsByTime' in data:
                regions = []
                region_costs = {}
                for result_item in data['ResultsByTime']:
                    if 'Groups' in result_item:
                        for group in result_item['Groups']:
                            region = group['Keys'][0]
                            if 'Metrics' in group and 'UnblendedCost' in group['Metrics']:
                                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                                region_costs[region] = region_costs.get(region, 0) + amount
                
                sorted_regions = sorted(region_costs.items(), key=lambda x: x[1], reverse=True)
                total_cost = sum(region_costs.values())
                
                for region, cost in sorted_regions:
                    percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                    regions.append({
                        'name': region,
                        'cost': cost,
                        'percentage': percentage
                    })
                
                # Store regional data separately
                if 'regions' not in parsed_data:
                    parsed_data['regions'] = []
                parsed_data['regions'].extend(regions)
            
            # Handle get_cost_and_usage (multiple periods)
            elif 'cost_and_usage' in tool_name and tool_name != 'get_cost_and_usage_comparisons':
                if 'ResultsByTime' in data:
                    period_cost = extract_cost_from_data(data)
                    
                    # Extract service breakdown if available
                    services = []
                    for result_item in data['ResultsByTime']:
                        if 'Groups' in result_item:
                            service_costs = {}
                            for group in result_item['Groups']:
                                service = group['Keys'][0]
                                if 'Metrics' in group and 'UnblendedCost' in group['Metrics']:
                                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                                    service_costs[service] = service_costs.get(service, 0) + amount
                            
                            sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
                            total_cost = sum(service_costs.values())
                            
                            for service, cost in sorted_services:
                                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                                services.append({
                                    'name': service,
                                    'cost': cost,
                                    'percentage': percentage
                                })
                    
                    # Determine period name from args
                    period_name = f"Period {period_counter + 1}"
                    if 'start_date' in args:
                        start = args['start_date']
                        try:
                            date_obj = datetime.strptime(start, '%Y-%m-%d')
                            period_name = date_obj.strftime('%B %Y')
                        except:
                            pass
                    
                    parsed_data['periods'].append({
                        'name': period_name,
                        'cost': period_cost,
                        'services': services
                    })
                    period_counter += 1
            
            # Handle get_cost_comparison_drivers
            elif 'comparison_drivers' in tool_name or tool_name == 'get_cost_comparison_drivers':
                if 'top_drivers' in data:
                    parsed_data['cost_drivers'].extend(data['top_drivers'][:5])
            
            # Handle forecast
            elif 'forecast' in tool_name and 'ForecastResultsByTime' in data:
                forecast_total = 0
                for result_item in data['ForecastResultsByTime']:
                    if 'MeanValue' in result_item:
                        forecast_total += float(result_item['MeanValue'])
                parsed_data['forecast'] = forecast_total
    
    # Create a structured summary for Claude
    data_summary = []
    
    if parsed_data['date_info']:
        data_summary.append(f"Reference Date: {parsed_data['date_info'].get('today', 'N/A')}")
        data_summary.append("")
    
    if parsed_data['periods']:
        data_summary.append("COST DATA BY PERIOD:")
        for i, period in enumerate(parsed_data['periods'], 1):
            data_summary.append(f"\n{period['name']}: ${period['cost']:.2f}")
            
            if period['services']:
                data_summary.append(f"  Top Services:")
                for j, svc in enumerate(period['services'][:10], 1):
                    data_summary.append(f"    {j}. {svc['name']}: ${svc['cost']:.2f} ({svc['percentage']:.1f}%)")
        
        # Calculate period-to-period changes
        if len(parsed_data['periods']) >= 2:
            data_summary.append("\nPERIOD-TO-PERIOD CHANGES:")
            for i in range(len(parsed_data['periods']) - 1):
                p1 = parsed_data['periods'][i]
                p2 = parsed_data['periods'][i + 1]
                change = p2['cost'] - p1['cost']
                change_pct = (change / p1['cost'] * 100) if p1['cost'] > 0 else 0
                data_summary.append(f"{p1['name']} → {p2['name']}: ${change:+.2f} ({change_pct:+.1f}%)")
        
        data_summary.append("")
    
    if parsed_data.get('regions'):
        data_summary.append("COST BY REGION:")
        for i, region in enumerate(parsed_data['regions'][:10], 1):
            data_summary.append(f"{i}. {region['name']}: ${region['cost']:.2f} ({region['percentage']:.1f}%)")
        data_summary.append("")
    
    if parsed_data['cost_drivers']:
        data_summary.append("TOP COST CHANGE DRIVERS:")
        for i, driver in enumerate(parsed_data['cost_drivers'][:10], 1):
            service = driver.get('service', 'Unknown')
            p1_cost = driver.get('period1_cost', 0)
            p2_cost = driver.get('period2_cost', 0)
            change = driver.get('absolute_change', 0)
            change_pct = driver.get('percentage_change', 0)
            data_summary.append(f"{i}. {service}: ${p1_cost:.2f} → ${p2_cost:.2f} (${change:+.2f}, {change_pct:+.1f}%)")
        data_summary.append("")
    
    if parsed_data['forecast'] is not None:
        data_summary.append(f"FORECAST: ${parsed_data['forecast']:.2f}")
        data_summary.append("")
    
    structured_summary = "\n".join(data_summary)
    
    # Get Claude's final analysis with ONLY the parsed data
    final_messages = [
        {
            "role": "user",
            "content": f"""User question: "{user_query}"

ACTUAL DATA FROM AWS COST EXPLORER:
{structured_summary}

CRITICAL INSTRUCTIONS:
- Use ONLY the data provided above
- Do NOT make up or invent any service names, costs, or percentages
- Answer the SPECIFIC question asked (pay attention to which months/periods they asked about)
- If the requested data is not available, clearly state that
- Base ALL analysis on the actual numbers provided

Please provide a comprehensive analysis that includes:

1. **Direct Answer**: 
   - State the ACTUAL cost for each period requested (use the numbers from "COST DATA BY PERIOD")
   - Example: "October 2025: $471.58, November 2025: $450.00, December 2025: $583.00"

2. **Trend Analysis**: 
   - Describe the cost trend across the periods (increasing, decreasing, or stable)
   - Calculate and explain the percentage changes between consecutive periods
   - Identify if there's an overall upward or downward trend
   - Example: "Costs decreased 4.6% from Oct to Nov, then increased 29.6% from Nov to Dec, showing an overall upward trend of 23.6%"

3. **Usage Pattern Insights**:
   - Analyze which services are driving the changes
   - Identify services with significant increases or decreases
   - Look for patterns (e.g., consistent growth in certain services, seasonal changes)
   - Example: "Amazon Bedrock usage increased significantly in December, suggesting increased AI/ML workload"

4. **Top Services**:
   - List the top services for each period with their actual costs
   - Highlight services that changed significantly between periods

5. **Key Findings**:
   - What are the most important takeaways from the data?
   - Are there any concerning trends (rapid cost increases)?
   - Are there any positive trends (cost optimizations)?

6. **Recommendations**:
   - Provide specific, actionable recommendations based on the actual trends observed
   - Focus on services showing the largest increases
   - Suggest optimization opportunities

Keep your response factual, detailed, and based strictly on the data provided."""
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
    st.title("🤖 AI Assistant Controls")
    
    st.success("✅ Using AWS Bedrock (IAM Role)")
    st.caption("Claude Haiku 3 via Bedrock")
    
    st.divider()
    
    # Token refresh button
    if st.button("� Roefresh Token", key="refresh_token_btn", use_container_width=True):
        with st.spinner("Refreshing bearer token..."):
            if refresh_bearer_token():
                st.success("✅ Token refreshed successfully!")
                st.info("Please reconnect to MCP Agent")
            else:
                st.error("❌ Failed to refresh token")
    
    # Connection status
    if st.button("🔌 Connect to MCP Agent", key="connect_btn", use_container_width=True):
        with st.spinner("Connecting..."):
            connected, tools = asyncio.run(connect_to_mcp())
            st.session_state.connected = connected
            st.session_state.tools = tools
    
    if st.session_state.connected:
        st.success("✅ Connected to MCP Agent")
        st.metric("Available Tools", len(st.session_state.tools))
    else:
        st.warning("⚠️ Not connected")
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Smart Queries")
    
    if st.button("📊 Full Cost Analysis", key="full_analysis_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Get the cost for current month and previous month, show me top 5 services contributing to my cost, and provide detailed analysis comparing the two months"
        })
        st.rerun()
    
    if st.button("📈 Cost Trends", key="trends_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Compare my current month costs with last month and tell me which services increased the most"
        })
        st.rerun()
    
    if st.button("🎯 Top Spenders", key="spenders_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show me my top 5 most expensive services this month and compare with last month"
        })
        st.rerun()
    
    if st.button("🔮 Forecast Analysis", key="forecast_analysis_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Show me current month costs, forecast for next month, and provide recommendations"
        })
        st.rerun()
    
    if st.button("💡 Cost Optimization", key="optimization_btn", use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": "Analyze my costs and provide specific recommendations for cost optimization"
        })
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", key="clear_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🤖 AWS Cost Explorer AI Assistant")
st.markdown("Ask complex questions - I'll analyze multiple data sources and provide intelligent insights")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your AWS costs..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with Claude via Bedrock
    with st.chat_message("assistant"):
        if not st.session_state.connected:
            st.warning("⚠️ Not connected to MCP agent. Please connect first.")
            response = "Please connect to the MCP agent first using the button in the sidebar."
        else:
            with st.spinner("🤖 Analyzing your question and gathering data..."):
                try:
                    # Use Claude via Bedrock to orchestrate tool calls
                    tool_results, analysis = asyncio.run(intelligent_assistant(prompt))
                    
                    # Display tool results with formatting
                    if tool_results:
                        st.markdown("### 📊 Data Gathered:")
                        
                        for tool_name, result in tool_results.items():
                            data, error = parse_cost_response(result)
                            
                            if error:
                                st.error(f"❌ {tool_name}: {error}")
                                # Show raw response for debugging
                                with st.expander("🔍 Debug: Raw Response"):
                                    st.code(result, language="json")
                            elif data:
                                if 'current_month' in tool_name:
                                    display_cost_summary(data, "Current Month Cost")
                                elif 'last_month' in tool_name:
                                    display_cost_summary(data, "Last Month Cost")
                                elif 'by_service' in tool_name:
                                    display_cost_by_service(data, limit=5)
                                
                                # Add debug expander to see raw data
                                with st.expander("🔍 Debug: View Raw Data"):
                                    st.json(data)
                    
                    # Display Claude's analysis
                    st.markdown("### 🧠 AI Analysis:")
                    st.markdown(f"""
                    <div class="analysis-box">
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    response = analysis
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    response = f"I encountered an error: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by Claude Haiku (Bedrock)")
with col2:
    st.caption("🔄 Multi-tool orchestration")
with col3:
    st.caption("🔒 IAM Role-based access")
