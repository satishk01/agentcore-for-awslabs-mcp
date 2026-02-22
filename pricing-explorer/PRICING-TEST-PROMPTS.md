# AWS Pricing MCP Server - Real-World Architecture Test Prompts

These prompts test real-world architectural solutions and provide practical cost planning for production deployments. Each prompt represents actual business scenarios you'll encounter when deploying AWS solutions.

## SECTION 1: AWS BEDROCK & AGENTCORE ARCHITECTURES

### 1. AWS Bedrock Agent with AgentCore Runtime
**Prompt:** "I'm deploying an AWS Bedrock agent using AgentCore Runtime. I need: 1 AgentCore Runtime agent handling 10,000 invocations per month (average 30 seconds each), Claude Haiku model for processing, 1 Lambda function (512MB) for preprocessing, 1 DynamoDB table (on-demand) for state management, and CloudWatch Logs. What's my total monthly cost in US East?"

**Architecture Components:**
- AgentCore Runtime (serverless)
- Bedrock Claude Haiku invocations
- Lambda preprocessing
- DynamoDB state storage
- CloudWatch Logs

**Tests:** Multi-service pricing, serverless cost calculation, Bedrock pricing

---

### 2. AgentCore Runtime with Gateway (MCP Server)
**Prompt:** "I'm deploying an MCP server using AgentCore Runtime with Gateway. Architecture: 1 AgentCore Runtime agent, 1 AgentCore Gateway exposing 5 tools, expected 50,000 API calls per month, 1 Lambda function (1GB) as backend for 2 tools, 1 API Gateway REST API, CloudWatch monitoring. Calculate monthly cost for US East."

**Architecture Components:**
- AgentCore Runtime
- AgentCore Gateway
- Lambda backends
- API Gateway
- CloudWatch

**Tests:** AgentCore Gateway pricing, API Gateway pricing, Lambda pricing

---

### 3. Multi-Agent Bedrock Solution
**Prompt:** "I'm building a multi-agent system with: 3 AgentCore Runtime agents (orchestrator, analyzer, executor), each handling 5,000 invocations/month, Claude Haiku for orchestrator, Claude Sonnet for analyzer, 2 Lambda functions (1GB each) for custom actions, 1 S3 bucket (100GB storage, 10,000 requests/month), DynamoDB (5GB storage, 100,000 reads, 50,000 writes), EventBridge for agent coordination. What's the total monthly cost?"

**Architecture Components:**
- Multiple AgentCore agents
- Multiple Bedrock models
- Lambda functions
- S3 storage
- DynamoDB
- EventBridge

**Tests:** Complex multi-agent pricing, multiple model pricing, event-driven architecture

---

### 4. AgentCore with Memory Service
**Prompt:** "I'm deploying an agent with AgentCore Memory service. Setup: 1 AgentCore Runtime agent, AgentCore Memory (semantic + event memory), 10GB vector storage, 20,000 memory operations/month, 1 RDS PostgreSQL db.t3.small for persistent storage, 50GB EBS storage. Calculate monthly cost in US East."

**Architecture Components:**
- AgentCore Runtime
- AgentCore Memory service
- Vector storage
- RDS PostgreSQL
- EBS storage

**Tests:** AgentCore Memory pricing, RDS pricing, storage pricing

---

### 5. Bedrock Agent with Code Interpreter
**Prompt:** "I need a Bedrock agent with code execution capabilities: 1 AgentCore Runtime agent, AgentCore Code Interpreter (500 executions/month, average 2 minutes each), Claude Sonnet model, 1 S3 bucket for code artifacts (50GB), Lambda for result processing (2GB, 1000 invocations). What's my monthly cost?"

**Architecture Components:**
- AgentCore Runtime
- AgentCore Code Interpreter
- Bedrock Claude Sonnet
- S3 storage
- Lambda processing

**Tests:** Code Interpreter pricing, execution time pricing, artifact storage

---

## SECTION 2: CONTAINERIZED SOLUTIONS (ECS)

### 6. ECS Service with NLB + API Gateway
**Prompt:** "I'm deploying a containerized API service: 3 ECS Fargate tasks (2 vCPU, 4GB RAM each) running 24/7, 1 Network Load Balancer, 1 API Gateway HTTP API (1 million requests/month), 1 ECR repository (10GB images), CloudWatch Container Insights, 100GB EBS for persistent storage. Calculate monthly cost for US East."

**Architecture Components:**
- ECS Fargate tasks
- Network Load Balancer
- API Gateway HTTP API
- ECR repository
- CloudWatch Container Insights
- EBS volumes

**Tests:** ECS Fargate pricing, NLB pricing, API Gateway pricing, container registry

---

### 7. ECS Service with Application Load Balancer
**Prompt:** "Microservices architecture on ECS: 5 ECS Fargate services (each with 2 tasks: 1 vCPU, 2GB RAM), 1 Application Load Balancer with 3 target groups, 1 API Gateway REST API (500,000 requests/month), Route 53 hosted zone with 2 million queries, CloudWatch Logs (50GB/month). What's the total monthly cost?"

**Architecture Components:**
- Multiple ECS services
- Application Load Balancer
- API Gateway REST API
- Route 53
- CloudWatch Logs

**Tests:** Multi-service ECS pricing, ALB pricing, DNS pricing, log storage

---

### 8. ECS with Auto Scaling
**Prompt:** "Auto-scaling ECS deployment: ECS Fargate with auto-scaling (min 2, max 10 tasks, average 5 tasks), each task: 4 vCPU, 8GB RAM, running 24/7, 1 Application Load Balancer, CloudWatch alarms for scaling, 1 RDS MySQL db.m5.large Multi-AZ, 500GB EBS storage. Calculate monthly cost assuming average scaling."

**Architecture Components:**
- Auto-scaling ECS Fargate
- Application Load Balancer
- CloudWatch alarms
- RDS Multi-AZ
- EBS storage

**Tests:** Variable ECS pricing, auto-scaling cost estimation, RDS Multi-AZ

---

### 9. ECS with Service Discovery
**Prompt:** "Microservices with service discovery: 4 ECS Fargate services (2 vCPU, 4GB each, 2 tasks per service), AWS Cloud Map for service discovery (4 services, 100,000 API calls/month), 1 Application Load Balancer, 1 NAT Gateway, VPC endpoints for S3 and DynamoDB. What's my monthly cost?"

**Architecture Components:**
- Multiple ECS services
- AWS Cloud Map
- Application Load Balancer
- NAT Gateway
- VPC endpoints

**Tests:** Service discovery pricing, NAT Gateway pricing, VPC endpoint pricing

---

### 10. ECS with Secrets Manager
**Prompt:** "Secure ECS deployment: 3 ECS Fargate tasks (2 vCPU, 4GB RAM), AWS Secrets Manager (10 secrets, 50,000 API calls/month), Systems Manager Parameter Store (20 parameters, 100,000 API calls), 1 Application Load Balancer, KMS key for encryption. Calculate monthly cost."

**Architecture Components:**
- ECS Fargate
- Secrets Manager
- Systems Manager Parameter Store
- Application Load Balancer
- KMS encryption

**Tests:** Secrets management pricing, KMS pricing, secure configuration costs

---

## SECTION 3: SERVERLESS SOLUTIONS (LAMBDA)

### 11. Lambda + API Gateway REST API
**Prompt:** "Serverless REST API: 5 Lambda functions (1GB RAM, average 500ms execution), 2 million invocations/month total, 1 API Gateway REST API (2 million requests), DynamoDB (10GB storage, 1 million reads, 500,000 writes), CloudWatch Logs (20GB/month). What's the monthly cost?"

**Architecture Components:**
- Multiple Lambda functions
- API Gateway REST API
- DynamoDB
- CloudWatch Logs

**Tests:** Lambda pricing with execution time, API Gateway REST pricing, DynamoDB pricing

---

### 12. Lambda + API Gateway HTTP API (WebSocket)
**Prompt:** "Real-time WebSocket API: 3 Lambda functions (512MB RAM, average 1 second execution), API Gateway WebSocket API (500,000 connections, 5 million messages/month), DynamoDB Streams, ElastiCache Redis (cache.t3.micro) for session management. Calculate monthly cost."

**Architecture Components:**
- Lambda functions
- API Gateway WebSocket
- DynamoDB Streams
- ElastiCache Redis

**Tests:** WebSocket pricing, DynamoDB Streams pricing, ElastiCache pricing

---

### 13. Lambda with EventBridge
**Prompt:** "Event-driven architecture: 10 Lambda functions (average 1GB RAM, 2 seconds execution), EventBridge (1 million events/month, 20 rules), 5 SQS queues (10 million requests), 2 SNS topics (1 million notifications), S3 event notifications (100,000 events). What's my monthly cost?"

**Architecture Components:**
- Multiple Lambda functions
- EventBridge
- SQS queues
- SNS topics
- S3 event notifications

**Tests:** Event-driven pricing, message queue pricing, notification pricing

---

### 14. Lambda with Step Functions
**Prompt:** "Workflow orchestration: AWS Step Functions (Standard workflows, 50,000 state transitions/month), 8 Lambda functions (average 1GB RAM, 1 second execution), DynamoDB for state persistence, SNS for notifications, CloudWatch Logs. Calculate total monthly cost."

**Architecture Components:**
- Step Functions Standard
- Multiple Lambda functions
- DynamoDB
- SNS
- CloudWatch

**Tests:** Step Functions pricing, workflow orchestration costs

---

### 15. Lambda@Edge with CloudFront
**Prompt:** "Global edge computing: CloudFront distribution (1TB data transfer out, 10 million requests), 2 Lambda@Edge functions (128MB RAM, 50ms execution, 5 million invocations), S3 origin (500GB storage), Route 53 hosted zone. What's the monthly cost for global distribution?"

**Architecture Components:**
- CloudFront distribution
- Lambda@Edge functions
- S3 origin
- Route 53

**Tests:** CloudFront pricing, Lambda@Edge pricing, global distribution costs

---

## SECTION 4: COMPLETE BUSINESS SOLUTIONS

### 16. E-Commerce Platform
**Prompt:** "Complete e-commerce solution: Frontend (CloudFront + S3, 2TB transfer), API layer (3 ECS Fargate tasks: 2 vCPU, 4GB), Product catalog (RDS PostgreSQL db.m5.xlarge Multi-AZ, 500GB storage), Session management (ElastiCache Redis cache.m5.large), Order processing (5 Lambda functions, 1 million invocations), Payment processing (Lambda + Secrets Manager), Image storage (S3, 1TB), Search (OpenSearch t3.medium.search, 3 nodes). What's the total monthly cost?"

**Architecture Components:**
- CloudFront + S3 frontend
- ECS Fargate API
- RDS Multi-AZ database
- ElastiCache Redis
- Lambda functions
- S3 storage
- OpenSearch cluster

**Tests:** Complete solution pricing, multi-tier architecture

---

### 17. Data Analytics Platform
**Prompt:** "Analytics platform: Data ingestion (Kinesis Data Streams, 10 shards), Processing (Lambda + Kinesis, 5 million records/month), Storage (S3, 5TB), Data warehouse (Redshift dc2.large, 2 nodes), Visualization (QuickSight, 10 users), Athena queries (1TB scanned/month), Glue ETL (10 DPU-hours/day). Calculate monthly cost."

**Architecture Components:**
- Kinesis Data Streams
- Lambda processing
- S3 data lake
- Redshift cluster
- QuickSight
- Athena
- Glue ETL

**Tests:** Data platform pricing, analytics service costs

---

### 18. IoT Solution
**Prompt:** "IoT platform: AWS IoT Core (1 million messages/month), IoT Rules Engine (10 rules), Lambda processing (2GB RAM, 500,000 invocations), Timestream database (100GB storage, 1 million writes, 500,000 queries), S3 for raw data (2TB), CloudWatch dashboards (5 dashboards). What's the monthly cost?"

**Architecture Components:**
- IoT Core
- IoT Rules Engine
- Lambda processing
- Timestream database
- S3 storage
- CloudWatch dashboards

**Tests:** IoT pricing, time-series database pricing

---

### 19. Machine Learning Pipeline
**Prompt:** "ML pipeline: SageMaker training (ml.p3.2xlarge, 100 hours/month), SageMaker endpoint (ml.m5.xlarge, 24/7), S3 for datasets (10TB), Lambda for preprocessing (5GB RAM, 10,000 invocations), Step Functions for orchestration (10,000 transitions), ECR for model images (50GB). Calculate monthly cost."

**Architecture Components:**
- SageMaker training
- SageMaker endpoint
- S3 storage
- Lambda preprocessing
- Step Functions
- ECR

**Tests:** ML infrastructure pricing, SageMaker costs

---

### 20. Multi-Tenant SaaS Platform
**Prompt:** "SaaS platform for 100 tenants: Application tier (ECS Fargate, 10 tasks: 4 vCPU, 8GB), Database (Aurora PostgreSQL, 2 instances: db.r5.2xlarge), Cache (ElastiCache Redis, 3 nodes: cache.r5.large), API Gateway (10 million requests), Cognito (10,000 MAU), S3 (5TB), CloudFront (3TB transfer), WAF (10 million requests). What's the monthly cost?"

**Architecture Components:**
- ECS Fargate application
- Aurora PostgreSQL cluster
- ElastiCache Redis cluster
- API Gateway
- Cognito user management
- S3 storage
- CloudFront CDN
- WAF protection

**Tests:** Multi-tenant architecture pricing, managed service costs

---

## SECTION 5: HYBRID & ADVANCED ARCHITECTURES

### 21. Disaster Recovery Setup
**Prompt:** "DR architecture: Primary region (US East): 5 ECS tasks, RDS db.m5.xlarge, 1TB EBS. DR region (US West): 2 ECS tasks (standby), RDS read replica db.m5.large, S3 cross-region replication (500GB/month), Route 53 health checks, CloudWatch alarms. Calculate monthly cost for both regions."

**Architecture Components:**
- Multi-region deployment
- ECS in both regions
- RDS with read replica
- S3 cross-region replication
- Route 53 failover
- CloudWatch monitoring

**Tests:** Multi-region pricing, DR cost calculation, replication costs

---

### 22. Hybrid Cloud with Direct Connect
**Prompt:** "Hybrid architecture: AWS Direct Connect (1Gbps dedicated connection), VPN backup connection, Transit Gateway (500GB data processed), 5 EC2 instances (m5.xlarge) in VPC, 1 RDS db.m5.large, S3 for hybrid storage (2TB), Storage Gateway (1TB cached). What's the monthly cost?"

**Architecture Components:**
- Direct Connect
- VPN connection
- Transit Gateway
- EC2 instances
- RDS database
- S3 storage
- Storage Gateway

**Tests:** Hybrid connectivity pricing, data transfer costs

---

### 23. High-Performance Computing (HPC)
**Prompt:** "HPC cluster: 20 EC2 c5n.18xlarge instances (running 8 hours/day, 20 days/month), Elastic Fabric Adapter, FSx for Lustre (10TB storage, 1000 MB/s throughput), S3 for results (5TB), Batch for job scheduling, CloudWatch monitoring. Calculate monthly cost."

**Architecture Components:**
- HPC EC2 instances
- Elastic Fabric Adapter
- FSx for Lustre
- S3 storage
- AWS Batch
- CloudWatch

**Tests:** HPC pricing, high-performance storage, batch processing

---

### 24. Media Processing Platform
**Prompt:** "Media platform: MediaConvert (1000 hours HD transcoding/month), S3 for video storage (20TB), CloudFront for delivery (10TB transfer), Lambda for metadata processing (2GB RAM, 50,000 invocations), DynamoDB for catalog (50GB, 5 million reads), Elemental MediaPackage (100 hours live streaming). What's the monthly cost?"

**Architecture Components:**
- MediaConvert transcoding
- S3 video storage
- CloudFront delivery
- Lambda processing
- DynamoDB catalog
- MediaPackage streaming

**Tests:** Media service pricing, video processing costs

---

### 25. Compliance & Security Platform
**Prompt:** "Security-focused architecture: GuardDuty (analyzing 500GB/month), Security Hub (100 security checks), Config (50 rules, 10,000 configuration items), CloudTrail (5 trails, 1 million events), Macie (scanning 10TB S3 data), KMS (100 keys, 1 million API calls), Inspector (10 EC2 instances), WAF (5 million requests). Calculate monthly security cost."

**Architecture Components:**
- GuardDuty threat detection
- Security Hub
- AWS Config
- CloudTrail
- Macie data security
- KMS encryption
- Inspector vulnerability scanning
- WAF protection

**Tests:** Security service pricing, compliance costs

---

## SECTION 6: COST OPTIMIZATION SCENARIOS

### 26. Right-Sizing Analysis
**Prompt:** "I'm currently running 10 m5.2xlarge instances 24/7 for my application. Based on monitoring, I only need 60% of the current capacity. Compare the cost of: current setup (10 × m5.2xlarge), right-sized option 1 (6 × m5.2xlarge), right-sized option 2 (10 × m5.xlarge), right-sized option 3 (15 × m5.large with better distribution). Which option saves the most money?"

**Tests:** Multiple instance comparisons, cost optimization analysis

---

### 27. Reserved Instance vs On-Demand Analysis
**Prompt:** "I'm running 20 m5.xlarge instances 24/7 in US East. Compare: on-demand pricing, 1-year reserved instance (no upfront), 1-year reserved instance (all upfront), 3-year reserved instance (all upfront). Calculate monthly cost and total 3-year cost for each option. What's my potential savings?"

**Tests:** Reserved instance pricing, long-term cost analysis

---

### 28. Spot Instance Opportunity
**Prompt:** "I have a batch processing workload using 50 c5.4xlarge instances for 8 hours/day. Compare: on-demand pricing, spot instance pricing (assume 70% discount), reserved instances. For spot instances, calculate the monthly cost and annual savings compared to on-demand."

**Tests:** Spot instance pricing, batch workload optimization

---

### 29. Serverless vs Container Cost Comparison
**Prompt:** "I need to choose between architectures for my API (1 million requests/month, average 500ms processing): Option A: 3 ECS Fargate tasks (1 vCPU, 2GB RAM, 24/7), Option B: Lambda functions (1GB RAM, 500ms execution, 1 million invocations). Include API Gateway and CloudWatch costs for both. Which is more cost-effective?"

**Tests:** Architecture comparison, serverless vs containers

---

### 30. Storage Tier Optimization
**Prompt:** "I have 50TB of data in S3 Standard. Usage pattern: 10TB accessed frequently (daily), 20TB accessed monthly, 20TB accessed rarely (quarterly). Compare costs for: all in S3 Standard, optimized with S3 Intelligent-Tiering, manual tiering (Standard/Standard-IA/Glacier), S3 Lifecycle policies. What's the optimal strategy?"

**Tests:** S3 storage tier pricing, lifecycle optimization

---

## How to Use These Prompts

### For Architecture Planning
1. **Copy the prompt** for your architecture type
2. **Modify the specifications** to match your requirements
3. **Paste into the Streamlit pricing app**
4. **Review the cost breakdown** provided by Claude
5. **Use for budget planning** and architecture decisions

### For Cost Optimization
1. **Start with your current architecture** prompt
2. **Ask for alternative configurations**
3. **Compare multiple options**
4. **Identify cost-saving opportunities**
5. **Make data-driven decisions**

### For Business Cases
1. **Use complete solution prompts** (Section 4)
2. **Get total cost of ownership**
3. **Present to stakeholders**
4. **Plan budgets accurately**
5. **Justify architecture decisions**

---

## Expected Outcomes

Each prompt should:
- ✅ Identify all required AWS services
- ✅ Calculate individual service costs
- ✅ Provide total monthly cost estimate
- ✅ Include data transfer and storage costs
- ✅ Consider regional pricing differences
- ✅ Provide cost optimization recommendations
- ✅ Explain cost drivers and trade-offs
- ✅ Suggest alternative architectures when relevant

---

## Prompt Categories

### By Architecture Type
- **Bedrock/AgentCore:** Prompts 1-5 (AI/ML agent solutions)
- **Containers (ECS):** Prompts 6-10 (Microservices, containerized apps)
- **Serverless (Lambda):** Prompts 11-15 (Event-driven, API solutions)
- **Complete Solutions:** Prompts 16-20 (Full business applications)
- **Advanced:** Prompts 21-25 (Hybrid, HPC, media, security)
- **Optimization:** Prompts 26-30 (Cost reduction strategies)

### By Complexity
- **Simple:** Single service pricing (basic EC2, RDS, S3)
- **Moderate:** 3-5 services (API + database + storage)
- **Complex:** 5-10 services (Complete microservices)
- **Enterprise:** 10+ services (Full business solutions)

### By Use Case
- **Development:** Small-scale, cost-optimized setups
- **Production:** High-availability, multi-AZ deployments
- **Enterprise:** Multi-region, disaster recovery, compliance
- **Optimization:** Cost reduction, right-sizing, reserved instances

---

## Success Criteria

A successful pricing analysis means:
1. **Accurate Service Identification** - All required AWS services identified
2. **Correct Pricing Data** - Prices match AWS Pricing Calculator
3. **Complete Cost Breakdown** - All cost components included
4. **Realistic Estimates** - Accounts for data transfer, storage, API calls
5. **Actionable Recommendations** - Specific optimization suggestions
6. **Alternative Options** - Multiple architecture choices presented
7. **Business Context** - Explains trade-offs and decisions
8. **Budget Planning** - Clear monthly and annual cost projections

---

## Real-World Application

### Before Deployment
Use these prompts to:
- Estimate project budgets
- Compare architecture options
- Get stakeholder approval
- Plan capacity and scaling
- Identify cost drivers

### During Operation
Use these prompts to:
- Validate actual vs estimated costs
- Identify optimization opportunities
- Plan for scaling
- Evaluate new features
- Justify infrastructure changes

### For Optimization
Use these prompts to:
- Find cost-saving opportunities
- Compare current vs optimized architectures
- Calculate ROI for changes
- Plan reserved instance purchases
- Optimize storage tiers

---

## Advanced Usage Tips

### 1. Combine Multiple Prompts
Start with a complete solution prompt, then drill down:
```
1. "Calculate cost for e-commerce platform" (Prompt 16)
2. "Compare RDS vs Aurora for the database tier"
3. "What if I use Spot instances for batch processing?"
4. "Show me reserved instance savings for the ECS tasks"
```

### 2. Modify for Your Scale
Adjust the numbers in prompts to match your scale:
- Change instance counts
- Adjust data volumes
- Modify request rates
- Update storage requirements

### 3. Regional Variations
Test the same architecture in different regions:
```
"Calculate cost for [architecture] in US East"
"Calculate cost for [architecture] in EU Frankfurt"
"Calculate cost for [architecture] in Asia Pacific Sydney"
```

### 4. Growth Planning
Model different growth scenarios:
```
"Current state: 5 ECS tasks, 100GB database"
"6 months: 10 ECS tasks, 500GB database"
"12 months: 20 ECS tasks, 1TB database"
```

### 5. Cost Optimization Workflow
```
1. Get current architecture cost
2. Ask for optimization recommendations
3. Compare alternative architectures
4. Calculate potential savings
5. Plan implementation
```

---

## Integration with Cost Explorer

### Complete Cost Management Workflow

**Step 1: Planning (Pricing Agent)**
```
"What will my new microservices architecture cost?"
→ Get estimated monthly cost: $5,000
```

**Step 2: Deployment**
```
Deploy the architecture to AWS
```

**Step 3: Validation (Cost Explorer Agent)**
```
"What are my actual costs for the microservices?"
→ Actual cost: $5,200 (4% over estimate)
```

**Step 4: Optimization (Both Agents)**
```
Cost Explorer: "Which services are costing more than expected?"
→ Identifies: ECS tasks running more than planned

Pricing Agent: "Compare current ECS setup vs right-sized alternative"
→ Shows: 20% potential savings with optimization
```

**Step 5: Implementation**
```
Implement optimization recommendations
```

**Step 6: Verification (Cost Explorer Agent)**
```
"Compare this month vs last month costs"
→ Validates: 18% cost reduction achieved
```

---

## Troubleshooting Complex Prompts

### If the response is incomplete:
1. **Break down the prompt** into smaller parts
2. **Ask for one service at a time**
3. **Combine results manually**

### If pricing seems incorrect:
1. **Verify region names** (use full names)
2. **Check instance type formats**
3. **Confirm service availability** in that region
4. **Cross-reference** with AWS Pricing Calculator

### If recommendations are unclear:
1. **Ask for clarification**: "Explain why you recommend X"
2. **Request alternatives**: "Show me 3 other options"
3. **Get specific numbers**: "Calculate exact monthly savings"

---

## Additional Resources

### AWS Pricing Calculator
Use for validation: https://calculator.aws/

### AWS Cost Management
- AWS Cost Explorer (actual costs)
- AWS Budgets (cost alerts)
- AWS Cost Anomaly Detection
- AWS Compute Optimizer (right-sizing)

### Architecture Patterns
- AWS Well-Architected Framework
- AWS Architecture Center
- AWS Solutions Library

---

## Feedback and Iteration

After using these prompts:
1. **Note which prompts work best** for your use cases
2. **Modify prompts** to match your specific needs
3. **Create custom prompts** for your common architectures
4. **Share successful prompts** with your team
5. **Build a library** of organization-specific prompts

---

## Summary

These 30 real-world prompts cover:
- ✅ AWS Bedrock and AgentCore architectures (5 prompts)
- ✅ Containerized solutions with ECS (5 prompts)
- ✅ Serverless solutions with Lambda (5 prompts)
- ✅ Complete business solutions (5 prompts)
- ✅ Advanced and hybrid architectures (5 prompts)
- ✅ Cost optimization scenarios (5 prompts)

**Total: 30 production-ready architectural pricing scenarios**

Use these prompts to make informed decisions about AWS architecture, plan budgets accurately, and optimize costs effectively.
