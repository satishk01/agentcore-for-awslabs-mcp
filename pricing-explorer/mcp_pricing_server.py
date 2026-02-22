from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
import boto3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

# Initialize AWS Pricing client
pricing_client = boto3.client('pricing', region_name='us-east-1')  # Pricing API only available in us-east-1

# ============================================================================
# AWS Pricing Tools
# ============================================================================

@mcp.tool()
def get_service_codes() -> Dict[str, Any]:
    """
    Get list of all AWS service codes available in the Pricing API.
    
    Returns:
        Dictionary containing list of service codes
    """
    try:
        response = pricing_client.describe_services(MaxResults=100)
        services = []
        for service in response.get('Services', []):
            services.append({
                'ServiceCode': service.get('ServiceCode'),
                'ServiceName': service.get('ServiceName', 'N/A')
            })
        
        return {
            'services': services,
            'count': len(services)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_service_attributes(service_code: str) -> Dict[str, Any]:
    """
    Get available attributes for a specific AWS service.
    
    Args:
        service_code: AWS service code (e.g., 'AmazonEC2', 'AmazonS3')
    
    Returns:
        Dictionary containing service attributes and their possible values
    """
    try:
        response = pricing_client.describe_services(
            ServiceCode=service_code,
            MaxResults=1
        )
        
        if not response.get('Services'):
            return {"error": f"Service code '{service_code}' not found"}
        
        service = response['Services'][0]
        return {
            'ServiceCode': service.get('ServiceCode'),
            'AttributeNames': service.get('AttributeNames', [])
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_attribute_values(
    service_code: str,
    attribute_name: str,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Get possible values for a specific attribute of an AWS service.
    
    Args:
        service_code: AWS service code (e.g., 'AmazonEC2')
        attribute_name: Attribute name (e.g., 'instanceType', 'location')
        max_results: Maximum number of results to return (default: 100)
    
    Returns:
        Dictionary containing attribute values
    """
    try:
        response = pricing_client.get_attribute_values(
            ServiceCode=service_code,
            AttributeName=attribute_name,
            MaxResults=max_results
        )
        
        values = [item['Value'] for item in response.get('AttributeValues', [])]
        
        return {
            'ServiceCode': service_code,
            'AttributeName': attribute_name,
            'Values': values,
            'Count': len(values)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_products(
    service_code: str,
    filters: Optional[List[Dict[str, Any]]] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Get pricing information for AWS products with optional filters.
    
    Args:
        service_code: AWS service code (e.g., 'AmazonEC2', 'AmazonS3')
        filters: List of filter dictionaries with Type, Field, and Value
                 Example: [{"Type": "TERM_MATCH", "Field": "instanceType", "Value": "t3.micro"}]
        max_results: Maximum number of results (default: 10, max: 100)
    
    Returns:
        Dictionary containing product pricing information
    """
    try:
        params = {
            'ServiceCode': service_code,
            'MaxResults': min(max_results, 100)
        }
        
        if filters:
            params['Filters'] = filters
        
        response = pricing_client.get_products(**params)
        
        price_list = response.get('PriceList', [])
        products = []
        
        for price_item in price_list:
            # Parse the JSON string
            product_data = json.loads(price_item)
            products.append(product_data)
        
        return {
            'ServiceCode': service_code,
            'Products': products,
            'Count': len(products)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_ec2_instance_pricing(
    instance_type: str,
    region: str = "US East (N. Virginia)",
    operating_system: str = "Linux",
    tenancy: str = "Shared",
    preinstalled_sw: str = "NA"
) -> Dict[str, Any]:
    """
    Get pricing for a specific EC2 instance type.
    
    Args:
        instance_type: EC2 instance type (e.g., 't3.micro', 'm5.large')
        region: AWS region name (e.g., 'US East (N. Virginia)')
        operating_system: Operating system (e.g., 'Linux', 'Windows')
        tenancy: Tenancy type ('Shared', 'Dedicated', 'Host')
        preinstalled_sw: Pre-installed software ('NA', 'SQL Std', 'SQL Web', 'SQL Ent')
    
    Returns:
        Dictionary containing EC2 instance pricing details
    """
    try:
        filters = [
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "location", "Value": region},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": operating_system},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": tenancy},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": preinstalled_sw},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"}
        ]
        
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=filters,
            MaxResults=1
        )
        
        if not response.get('PriceList'):
            return {"error": f"No pricing found for {instance_type} in {region}"}
        
        product_data = json.loads(response['PriceList'][0])
        
        # Extract on-demand pricing
        on_demand_price = None
        terms = product_data.get('terms', {})
        on_demand = terms.get('OnDemand', {})
        
        for term_key, term_data in on_demand.items():
            price_dimensions = term_data.get('priceDimensions', {})
            for dim_key, dim_data in price_dimensions.items():
                price_per_unit = dim_data.get('pricePerUnit', {})
                on_demand_price = price_per_unit.get('USD', 'N/A')
                break
            break
        
        return {
            'InstanceType': instance_type,
            'Region': region,
            'OperatingSystem': operating_system,
            'OnDemandPricePerHour': on_demand_price,
            'Currency': 'USD',
            'ProductDetails': product_data.get('product', {})
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_s3_pricing(region: str = "US East (N. Virginia)") -> Dict[str, Any]:
    """
    Get S3 storage pricing for a specific region.
    
    Args:
        region: AWS region name (e.g., 'US East (N. Virginia)')
    
    Returns:
        Dictionary containing S3 pricing details
    """
    try:
        filters = [
            {"Type": "TERM_MATCH", "Field": "location", "Value": region},
            {"Type": "TERM_MATCH", "Field": "storageClass", "Value": "General Purpose"}
        ]
        
        response = pricing_client.get_products(
            ServiceCode='AmazonS3',
            Filters=filters,
            MaxResults=10
        )
        
        pricing_info = []
        for price_item in response.get('PriceList', []):
            product_data = json.loads(price_item)
            
            # Extract pricing
            terms = product_data.get('terms', {})
            on_demand = terms.get('OnDemand', {})
            
            for term_key, term_data in on_demand.items():
                price_dimensions = term_data.get('priceDimensions', {})
                for dim_key, dim_data in price_dimensions.items():
                    price_per_unit = dim_data.get('pricePerUnit', {})
                    pricing_info.append({
                        'Description': dim_data.get('description', 'N/A'),
                        'PricePerUnit': price_per_unit.get('USD', 'N/A'),
                        'Unit': dim_data.get('unit', 'N/A')
                    })
        
        return {
            'Service': 'Amazon S3',
            'Region': region,
            'PricingDetails': pricing_info
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_rds_instance_pricing(
    instance_type: str,
    database_engine: str = "MySQL",
    region: str = "US East (N. Virginia)",
    deployment_option: str = "Single-AZ"
) -> Dict[str, Any]:
    """
    Get pricing for RDS database instances.
    
    Args:
        instance_type: RDS instance type (e.g., 'db.t3.micro', 'db.m5.large')
        database_engine: Database engine ('MySQL', 'PostgreSQL', 'Oracle', 'SQL Server')
        region: AWS region name
        deployment_option: Deployment option ('Single-AZ', 'Multi-AZ')
    
    Returns:
        Dictionary containing RDS pricing details
    """
    try:
        filters = [
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": database_engine},
            {"Type": "TERM_MATCH", "Field": "location", "Value": region},
            {"Type": "TERM_MATCH", "Field": "deploymentOption", "Value": deployment_option}
        ]
        
        response = pricing_client.get_products(
            ServiceCode='AmazonRDS',
            Filters=filters,
            MaxResults=1
        )
        
        if not response.get('PriceList'):
            return {"error": f"No pricing found for {instance_type} with {database_engine}"}
        
        product_data = json.loads(response['PriceList'][0])
        
        # Extract on-demand pricing
        on_demand_price = None
        terms = product_data.get('terms', {})
        on_demand = terms.get('OnDemand', {})
        
        for term_key, term_data in on_demand.items():
            price_dimensions = term_data.get('priceDimensions', {})
            for dim_key, dim_data in price_dimensions.items():
                price_per_unit = dim_data.get('pricePerUnit', {})
                on_demand_price = price_per_unit.get('USD', 'N/A')
                break
            break
        
        return {
            'InstanceType': instance_type,
            'DatabaseEngine': database_engine,
            'Region': region,
            'DeploymentOption': deployment_option,
            'OnDemandPricePerHour': on_demand_price,
            'Currency': 'USD'
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def compare_instance_prices(
    instance_types: List[str],
    region: str = "US East (N. Virginia)",
    operating_system: str = "Linux"
) -> Dict[str, Any]:
    """
    Compare pricing for multiple EC2 instance types.
    
    Args:
        instance_types: List of EC2 instance types to compare
        region: AWS region name
        operating_system: Operating system
    
    Returns:
        Dictionary containing price comparison
    """
    try:
        comparisons = []
        
        for instance_type in instance_types:
            result = get_ec2_instance_pricing(
                instance_type=instance_type,
                region=region,
                operating_system=operating_system
            )
            
            if 'error' not in result:
                comparisons.append({
                    'InstanceType': instance_type,
                    'PricePerHour': result.get('OnDemandPricePerHour', 'N/A')
                })
        
        # Sort by price
        comparisons.sort(key=lambda x: float(x['PricePerHour']) if x['PricePerHour'] != 'N/A' else float('inf'))
        
        return {
            'Region': region,
            'OperatingSystem': operating_system,
            'Comparison': comparisons
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def calculate_monthly_cost(
    hourly_price: float,
    hours_per_day: float = 24,
    days_per_month: int = 30
) -> Dict[str, Any]:
    """
    Calculate monthly cost from hourly pricing.
    
    Args:
        hourly_price: Hourly price in USD
        hours_per_day: Hours of usage per day (default: 24)
        days_per_month: Days per month (default: 30)
    
    Returns:
        Dictionary containing cost calculations
    """
    try:
        daily_cost = hourly_price * hours_per_day
        monthly_cost = daily_cost * days_per_month
        annual_cost = monthly_cost * 12
        
        return {
            'HourlyPrice': hourly_price,
            'DailyCost': round(daily_cost, 2),
            'MonthlyCost': round(monthly_cost, 2),
            'AnnualCost': round(annual_cost, 2),
            'Currency': 'USD',
            'Assumptions': {
                'HoursPerDay': hours_per_day,
                'DaysPerMonth': days_per_month
            }
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def estimate_data_transfer_cost(
    data_transfer_gb: float,
    transfer_type: str = "internet_outbound",
    region: str = "US East (N. Virginia)"
) -> Dict[str, Any]:
    """
    Estimate data transfer costs for AWS services.
    
    Args:
        data_transfer_gb: Amount of data transfer in GB
        transfer_type: Type of transfer (internet_outbound, inter_region, intra_region)
        region: AWS region
    
    Returns:
        Dictionary containing data transfer cost estimate
    """
    try:
        # Simplified pricing tiers (actual pricing varies by region and volume)
        pricing_tiers = {
            'internet_outbound': {
                'first_10tb': 0.09,  # per GB
                'next_40tb': 0.085,
                'next_100tb': 0.07,
                'over_150tb': 0.05
            },
            'inter_region': {
                'default': 0.02  # per GB
            },
            'intra_region': {
                'default': 0.01  # per GB
            }
        }
        
        if transfer_type not in pricing_tiers:
            return {"error": f"Unknown transfer type: {transfer_type}"}
        
        # Calculate cost based on tiers
        if transfer_type == 'internet_outbound':
            tiers = pricing_tiers['internet_outbound']
            remaining_gb = data_transfer_gb
            total_cost = 0
            
            # First 10TB
            if remaining_gb > 0:
                tier_gb = min(remaining_gb, 10240)  # 10TB in GB
                total_cost += tier_gb * tiers['first_10tb']
                remaining_gb -= tier_gb
            
            # Next 40TB
            if remaining_gb > 0:
                tier_gb = min(remaining_gb, 40960)  # 40TB in GB
                total_cost += tier_gb * tiers['next_40tb']
                remaining_gb -= tier_gb
            
            # Next 100TB
            if remaining_gb > 0:
                tier_gb = min(remaining_gb, 102400)  # 100TB in GB
                total_cost += tier_gb * tiers['next_100tb']
                remaining_gb -= tier_gb
            
            # Over 150TB
            if remaining_gb > 0:
                total_cost += remaining_gb * tiers['over_150tb']
        else:
            # Simple calculation for other transfer types
            rate = pricing_tiers[transfer_type]['default']
            total_cost = data_transfer_gb * rate
        
        return {
            'DataTransferGB': data_transfer_gb,
            'TransferType': transfer_type,
            'Region': region,
            'EstimatedCost': round(total_cost, 2),
            'Currency': 'USD',
            'Note': 'Estimate based on typical pricing tiers. Actual costs may vary.'
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def estimate_api_gateway_cost(
    requests_per_month: int,
    api_type: str = "REST",
    cache_size_gb: float = 0
) -> Dict[str, Any]:
    """
    Estimate API Gateway costs.
    
    Args:
        requests_per_month: Number of API requests per month
        api_type: API type (REST, HTTP, WebSocket)
        cache_size_gb: Cache size in GB (for REST API only)
    
    Returns:
        Dictionary containing API Gateway cost estimate
    """
    try:
        # API Gateway pricing (US East)
        pricing = {
            'REST': 3.50,  # per million requests
            'HTTP': 1.00,  # per million requests
            'WebSocket': {
                'messages': 1.00,  # per million messages
                'connection_minutes': 0.25  # per million connection minutes
            }
        }
        
        cache_pricing = {
            0.5: 0.020,   # per hour
            1.6: 0.038,
            6.1: 0.200,
            13.5: 0.250,
            28.4: 0.500,
            58.2: 1.000,
            118: 1.900,
            237: 3.800
        }
        
        if api_type not in ['REST', 'HTTP', 'WebSocket']:
            return {"error": f"Unknown API type: {api_type}"}
        
        # Calculate request cost
        if api_type in ['REST', 'HTTP']:
            millions = requests_per_month / 1_000_000
            request_cost = millions * pricing[api_type]
        else:  # WebSocket
            millions = requests_per_month / 1_000_000
            request_cost = millions * pricing['WebSocket']['messages']
        
        # Calculate cache cost (REST only)
        cache_cost = 0
        if api_type == 'REST' and cache_size_gb > 0:
            # Find closest cache size
            closest_size = min(cache_pricing.keys(), key=lambda x: abs(x - cache_size_gb))
            hourly_rate = cache_pricing[closest_size]
            cache_cost = hourly_rate * 730  # hours per month
        
        total_cost = request_cost + cache_cost
        
        return {
            'APIType': api_type,
            'RequestsPerMonth': requests_per_month,
            'RequestCost': round(request_cost, 2),
            'CacheCost': round(cache_cost, 2),
            'TotalMonthlyCost': round(total_cost, 2),
            'Currency': 'USD'
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def estimate_lambda_cost(
    invocations_per_month: int,
    memory_mb: int,
    avg_duration_ms: int
) -> Dict[str, Any]:
    """
    Estimate AWS Lambda costs.
    
    Args:
        invocations_per_month: Number of Lambda invocations per month
        memory_mb: Memory allocation in MB
        avg_duration_ms: Average execution duration in milliseconds
    
    Returns:
        Dictionary containing Lambda cost estimate
    """
    try:
        # Lambda pricing (US East)
        request_price = 0.20  # per 1 million requests
        compute_price = 0.0000166667  # per GB-second
        
        # Free tier
        free_requests = 1_000_000  # per month
        free_compute_gb_seconds = 400_000  # per month
        
        # Calculate billable requests
        billable_requests = max(0, invocations_per_month - free_requests)
        request_cost = (billable_requests / 1_000_000) * request_price
        
        # Calculate compute cost
        memory_gb = memory_mb / 1024
        duration_seconds = avg_duration_ms / 1000
        gb_seconds = invocations_per_month * memory_gb * duration_seconds
        
        billable_gb_seconds = max(0, gb_seconds - free_compute_gb_seconds)
        compute_cost = billable_gb_seconds * compute_price
        
        total_cost = request_cost + compute_cost
        
        return {
            'InvocationsPerMonth': invocations_per_month,
            'MemoryMB': memory_mb,
            'AvgDurationMS': avg_duration_ms,
            'RequestCost': round(request_cost, 2),
            'ComputeCost': round(compute_cost, 2),
            'TotalMonthlyCost': round(total_cost, 2),
            'GBSeconds': round(gb_seconds, 2),
            'Currency': 'USD',
            'Note': 'Includes AWS Free Tier deductions'
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def estimate_dynamodb_cost(
    storage_gb: float,
    read_requests_per_month: int,
    write_requests_per_month: int,
    pricing_model: str = "on_demand"
) -> Dict[str, Any]:
    """
    Estimate DynamoDB costs.
    
    Args:
        storage_gb: Storage size in GB
        read_requests_per_month: Number of read requests per month
        write_requests_per_month: Number of write requests per month
        pricing_model: Pricing model (on_demand or provisioned)
    
    Returns:
        Dictionary containing DynamoDB cost estimate
    """
    try:
        # DynamoDB pricing (US East)
        storage_price = 0.25  # per GB-month
        
        if pricing_model == "on_demand":
            read_price = 0.25  # per million read request units
            write_price = 1.25  # per million write request units
            
            # Free tier
            free_storage = 25  # GB
            
            # Calculate costs
            billable_storage = max(0, storage_gb - free_storage)
            storage_cost = billable_storage * storage_price
            
            read_cost = (read_requests_per_month / 1_000_000) * read_price
            write_cost = (write_requests_per_month / 1_000_000) * write_price
            
            total_cost = storage_cost + read_cost + write_cost
            
            return {
                'PricingModel': 'On-Demand',
                'StorageGB': storage_gb,
                'ReadRequestsPerMonth': read_requests_per_month,
                'WriteRequestsPerMonth': write_requests_per_month,
                'StorageCost': round(storage_cost, 2),
                'ReadCost': round(read_cost, 2),
                'WriteCost': round(write_cost, 2),
                'TotalMonthlyCost': round(total_cost, 2),
                'Currency': 'USD',
                'Note': 'Includes 25GB free tier storage'
            }
        else:
            return {"error": "Provisioned capacity pricing requires RCU/WCU specification"}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
