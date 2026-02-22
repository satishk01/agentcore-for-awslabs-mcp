from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
import boto3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

# Initialize AWS Cost Explorer client
ce_client = boto3.client('ce')

# ============================================================================
# Original Math Tools
# ============================================================================

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."

# ============================================================================
# AWS Cost Explorer Tools (Complete Set)
# ============================================================================

@mcp.tool()
def get_today_date() -> Dict[str, str]:
    """
    Get the current date and month to determine relevant data when answering questions about 'last month'.
    
    Returns:
        Dictionary containing today's date, current month, and last month information
    """
    try:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        return {
            "today": today.strftime('%Y-%m-%d'),
            "current_month_start": first_day_current_month.strftime('%Y-%m-%d'),
            "current_month_end": today.strftime('%Y-%m-%d'),
            "last_month_start": first_day_previous_month.strftime('%Y-%m-%d'),
            "last_month_end": first_day_current_month.strftime('%Y-%m-%d'),
            "current_month_name": today.strftime('%B %Y'),
            "last_month_name": last_day_previous_month.strftime('%B %Y')
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_dimension_values(
    dimension: str,
    start_date: str,
    end_date: str,
    search_string: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get available values for a specific dimension (e.g., SERVICE, REGION, LINKED_ACCOUNT).
    
    Args:
        dimension: Dimension name (SERVICE, REGION, LINKED_ACCOUNT, etc.)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        search_string: Optional search string to filter results
    
    Returns:
        Dictionary containing available dimension values
    """
    try:
        params = {
            'TimePeriod': {
                'Start': start_date,
                'End': end_date
            },
            'Dimension': dimension
        }
        
        if search_string:
            params['SearchString'] = search_string
        
        response = ce_client.get_dimension_values(**params)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_tag_values(
    tag_key: str,
    start_date: str,
    end_date: str,
    search_string: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get available values for a specific tag key.
    
    Args:
        tag_key: Tag key name
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        search_string: Optional search string to filter results
    
    Returns:
        Dictionary containing available tag values
    """
    try:
        params = {
            'TimePeriod': {
                'Start': start_date,
                'End': end_date
            },
            'TagKey': tag_key
        }
        
        if search_string:
            params['SearchString'] = search_string
        
        response = ce_client.get_tags(**params)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_and_usage(
    start_date: str,
    end_date: str,
    granularity: str = "MONTHLY",
    metrics: Optional[List[str]] = None,
    group_by: Optional[List[Dict[str, str]]] = None,
    filter_expression: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Retrieve AWS cost and usage data with filtering and grouping options.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY, HOURLY)
        metrics: List of metrics to retrieve (default: ["UnblendedCost"])
        group_by: List of grouping dimensions (e.g., [{"Type": "DIMENSION", "Key": "SERVICE"}])
        filter_expression: Optional filter expression for cost data
    
    Returns:
        Dictionary containing cost and usage data
    """
    if metrics is None:
        metrics = ["UnblendedCost"]
    
    try:
        params = {
            'TimePeriod': {
                'Start': start_date,
                'End': end_date
            },
            'Granularity': granularity,
            'Metrics': metrics
        }
        
        if group_by:
            params['GroupBy'] = group_by
        
        if filter_expression:
            params['Filter'] = filter_expression
        
        response = ce_client.get_cost_and_usage(**params)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_and_usage_comparisons(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    granularity: str = "MONTHLY",
    group_by_dimension: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compare costs between two time periods to identify changes and trends.
    
    Args:
        period1_start: Period 1 start date in YYYY-MM-DD format
        period1_end: Period 1 end date in YYYY-MM-DD format
        period2_start: Period 2 start date in YYYY-MM-DD format
        period2_end: Period 2 end date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY)
        group_by_dimension: Optional dimension to group by (SERVICE, REGION, etc.)
    
    Returns:
        Dictionary containing cost comparison data
    """
    try:
        # Get costs for period 1
        params1 = {
            'TimePeriod': {
                'Start': period1_start,
                'End': period1_end
            },
            'Granularity': granularity,
            'Metrics': ['UnblendedCost']
        }
        
        if group_by_dimension:
            params1['GroupBy'] = [{'Type': 'DIMENSION', 'Key': group_by_dimension}]
        
        period1_data = ce_client.get_cost_and_usage(**params1)
        
        # Get costs for period 2
        params2 = {
            'TimePeriod': {
                'Start': period2_start,
                'End': period2_end
            },
            'Granularity': granularity,
            'Metrics': ['UnblendedCost']
        }
        
        if group_by_dimension:
            params2['GroupBy'] = [{'Type': 'DIMENSION', 'Key': group_by_dimension}]
        
        period2_data = ce_client.get_cost_and_usage(**params2)
        
        return {
            "period1": {
                "start": period1_start,
                "end": period1_end,
                "data": period1_data
            },
            "period2": {
                "start": period2_start,
                "end": period2_end,
                "data": period2_data
            }
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_comparison_drivers(
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Analyze what drove cost changes between periods (top N most significant drivers).
    
    Args:
        period1_start: Period 1 start date in YYYY-MM-DD format
        period1_end: Period 1 end date in YYYY-MM-DD format
        period2_start: Period 2 start date in YYYY-MM-DD format
        period2_end: Period 2 end date in YYYY-MM-DD format
        top_n: Number of top drivers to return (default: 10)
    
    Returns:
        Dictionary containing top cost change drivers
    """
    try:
        # Get costs by service for both periods
        period1_data = ce_client.get_cost_and_usage(
            TimePeriod={'Start': period1_start, 'End': period1_end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        period2_data = ce_client.get_cost_and_usage(
            TimePeriod={'Start': period2_start, 'End': period2_end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        # Extract service costs for period 1
        period1_costs = {}
        for result in period1_data.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                period1_costs[service] = period1_costs.get(service, 0) + cost
        
        # Extract service costs for period 2
        period2_costs = {}
        for result in period2_data.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                period2_costs[service] = period2_costs.get(service, 0) + cost
        
        # Calculate changes
        all_services = set(period1_costs.keys()) | set(period2_costs.keys())
        changes = []
        
        for service in all_services:
            p1_cost = period1_costs.get(service, 0)
            p2_cost = period2_costs.get(service, 0)
            change = p2_cost - p1_cost
            change_pct = (change / p1_cost * 100) if p1_cost > 0 else (100 if p2_cost > 0 else 0)
            
            changes.append({
                'service': service,
                'period1_cost': p1_cost,
                'period2_cost': p2_cost,
                'absolute_change': change,
                'percentage_change': change_pct
            })
        
        # Sort by absolute change (descending)
        changes.sort(key=lambda x: abs(x['absolute_change']), reverse=True)
        
        return {
            "period1": {"start": period1_start, "end": period1_end},
            "period2": {"start": period2_start, "end": period2_end},
            "top_drivers": changes[:top_n],
            "total_period1_cost": sum(period1_costs.values()),
            "total_period2_cost": sum(period2_costs.values()),
            "total_change": sum(period2_costs.values()) - sum(period1_costs.values())
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_forecast(
    start_date: str,
    end_date: str,
    metric: str = "UNBLENDED_COST",
    granularity: str = "MONTHLY"
) -> Dict[str, Any]:
    """
    Get AWS cost forecast for a future time period.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (must be in future)
        end_date: End date in YYYY-MM-DD format
        metric: Metric to forecast (UNBLENDED_COST, BLENDED_COST, etc.)
        granularity: Time granularity (DAILY, MONTHLY)
    
    Returns:
        Dictionary containing cost forecast data
    """
    try:
        response = ce_client.get_cost_forecast(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Metric=metric,
            Granularity=granularity
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_by_service(
    start_date: str,
    end_date: str,
    granularity: str = "MONTHLY"
) -> Dict[str, Any]:
    """
    Get AWS costs grouped by service.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY)
    
    Returns:
        Dictionary containing costs grouped by AWS service
    """
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=["UnblendedCost"],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_current_month_cost() -> Dict[str, Any]:
    """
    Get AWS costs for the current month to date.
    
    Returns:
        Dictionary containing current month's cost data
    """
    try:
        today = datetime.now()
        start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_of_month,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=["UnblendedCost"]
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_last_month_cost() -> Dict[str, Any]:
    """
    Get AWS costs for the previous month.
    
    Returns:
        Dictionary containing last month's cost data
    """
    try:
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        start_date = first_day_previous_month.strftime('%Y-%m-%d')
        end_date = first_day_current_month.strftime('%Y-%m-%d')
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=["UnblendedCost"]
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_by_region(
    start_date: str,
    end_date: str,
    granularity: str = "MONTHLY"
) -> Dict[str, Any]:
    """
    Get AWS costs grouped by region.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY)
    
    Returns:
        Dictionary containing costs grouped by AWS region
    """
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity,
            Metrics=["UnblendedCost"],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'REGION'
                }
            ]
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_cost_anomalies(
    start_date: str,
    end_date: str,
    monitor_arn: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get AWS cost anomalies detected by Cost Anomaly Detection.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        monitor_arn: Optional ARN of specific anomaly monitor
    
    Returns:
        Dictionary containing detected cost anomalies
    """
    try:
        params = {
            'DateInterval': {
                'StartDate': start_date,
                'EndDate': end_date
            }
        }
        
        if monitor_arn:
            params['MonitorArn'] = monitor_arn
        
        response = ce_client.get_anomalies(**params)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_savings_plans_coverage(
    start_date: str,
    end_date: str,
    granularity: str = "MONTHLY"
) -> Dict[str, Any]:
    """
    Get Savings Plans coverage data.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY)
    
    Returns:
        Dictionary containing Savings Plans coverage data
    """
    try:
        response = ce_client.get_savings_plans_coverage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity
        )
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_reservation_coverage(
    start_date: str,
    end_date: str,
    granularity: str = "MONTHLY"
) -> Dict[str, Any]:
    """
    Get Reserved Instance coverage data.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        granularity: Time granularity (DAILY, MONTHLY)
    
    Returns:
        Dictionary containing RI coverage data
    """
    try:
        response = ce_client.get_reservation_coverage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity=granularity
        )
        return response
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")