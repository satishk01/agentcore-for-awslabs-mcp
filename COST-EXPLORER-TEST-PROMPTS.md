# AWS Cost Explorer MCP Server - Complex Test Prompts

These 25 prompts are designed to test the full capabilities of the Cost Explorer MCP Server and provide real business value to end users.

## 1. Multi-Period Trend Analysis
**Prompt:** "Compare my AWS costs for October, November, and December 2025. Identify which services showed the most significant cost increases and provide recommendations for cost optimization based on the trend."

**Tests:** get_cost_and_usage (multiple periods), get_cost_comparison_drivers, trend analysis

---

## 2. Budget Variance Analysis
**Prompt:** "My monthly AWS budget is $1,000. Compare my current month spending against last month and forecast next month. Tell me if I'm on track to stay within budget and what actions I should take."

**Tests:** get_current_month_cost, get_last_month_cost, get_cost_forecast, budget analysis

---

## 3. Service-Specific Deep Dive
**Prompt:** "Analyze my Amazon EC2 costs for the last 3 months. Show me the trend, identify if there are any anomalies, and recommend specific actions to reduce EC2 spending without impacting performance."

**Tests:** get_cost_by_service, multi-period comparison, anomaly detection, optimization recommendations

---

## 4. Regional Cost Distribution
**Prompt:** "Show me which AWS regions are costing me the most this month compared to last month. Identify if there are any regions where I could consolidate resources to save costs."

**Tests:** get_cost_by_region, period comparison, regional optimization

---

## 5. Quarter-over-Quarter Analysis
**Prompt:** "Compare my Q4 2025 costs (Oct-Dec) with Q3 2025 costs (Jul-Sep). What are the top 5 drivers of cost changes and what business factors might explain these changes?"

**Tests:** get_cost_and_usage (quarterly), get_cost_comparison_drivers, business context analysis

---

## 6. Sudden Cost Spike Investigation
**Prompt:** "My costs increased by 40% from last month to this month. Investigate which services caused this spike, when it started, and provide immediate recommendations to control costs."

**Tests:** get_cost_comparison_drivers, get_cost_by_service, root cause analysis

---

## 7. Year-over-Year Growth Analysis
**Prompt:** "Compare my December 2025 costs with December 2024 costs. Calculate the year-over-year growth rate and identify which services contributed most to the growth. Is this growth sustainable?"

**Tests:** get_cost_and_usage (YoY comparison), growth rate calculation, sustainability analysis

---

## 8. Cost Optimization Opportunity Identification
**Prompt:** "Analyze my current month costs and identify the top 3 services where I could potentially save money. For each service, provide specific, actionable recommendations with estimated savings."

**Tests:** get_current_month_cost, get_cost_by_service, optimization recommendations

---

## 9. Forecast Accuracy Check
**Prompt:** "Compare the forecasted costs for this month (that were predicted last month) with my actual costs so far. How accurate was the forecast and what does this tell us about our spending patterns?"

**Tests:** get_cost_forecast, get_current_month_cost, forecast accuracy analysis

---

## 10. Service Migration Impact Analysis
**Prompt:** "We migrated from EC2 to containers (ECS/EKS) in November 2025. Compare October and December costs to show the financial impact of this migration. Did we save money?"

**Tests:** get_cost_and_usage, get_cost_comparison_drivers, migration ROI analysis

---

## 11. Weekend vs Weekday Cost Pattern
**Prompt:** "Analyze my daily costs for the current month and identify if there's a pattern between weekday and weekend spending. Are we wasting money on resources that run during weekends?"

**Tests:** get_cost_and_usage (daily granularity), pattern analysis, waste identification

---

## 12. Top Cost Contributors with Context
**Prompt:** "Show me my top 10 services by cost this month. For each service, tell me the cost, percentage of total, trend compared to last month, and whether this spending level is typical or concerning."

**Tests:** get_cost_by_service, get_cost_comparison_drivers, contextual analysis

---

## 13. Cost Efficiency Metrics
**Prompt:** "Calculate my cost per day for the current month vs last month. Are we becoming more or less cost-efficient? What's driving the change in our daily burn rate?"

**Tests:** get_current_month_cost, get_last_month_cost, efficiency metrics calculation

---

## 14. New Service Adoption Analysis
**Prompt:** "Identify any AWS services that appeared in my costs this month but weren't present last month. For each new service, show the cost and assess if this is expected growth or unplanned spending."

**Tests:** get_cost_by_service (multiple periods), new service detection, spending classification

---

## 15. Cost Reduction Validation
**Prompt:** "We implemented cost optimization measures in November 2025. Compare October, November, and December costs to validate if our optimization efforts were successful. Quantify the savings achieved."

**Tests:** get_cost_and_usage (multiple periods), savings calculation, ROI validation

---

## 16. Seasonal Cost Pattern Analysis
**Prompt:** "Analyze my costs for the last 6 months and identify any seasonal patterns. Are there specific months where costs consistently spike? Help me plan for these patterns in the future."

**Tests:** get_cost_and_usage (6 months), seasonal pattern detection, planning recommendations

---

## 17. Service Dependency Cost Analysis
**Prompt:** "Show me the costs for my compute services (EC2, Lambda, ECS) and related services (VPC, ELB, CloudWatch) for this month. Analyze if the supporting service costs are proportional to compute costs."

**Tests:** get_cost_by_service, dependency analysis, proportionality assessment

---

## 18. Cost Anomaly Detection and Alert
**Prompt:** "Analyze my daily costs for the current month and identify any days where spending was significantly higher than normal. For each anomaly, investigate which services caused it and why."

**Tests:** get_cost_and_usage (daily), anomaly detection, root cause analysis

---

## 19. Multi-Account Cost Consolidation
**Prompt:** "If I have multiple AWS accounts, show me the total costs across all accounts for this month vs last month. Identify which account has the highest growth rate and needs attention."

**Tests:** get_dimension_values (LINKED_ACCOUNT), multi-account aggregation, growth analysis

---

## 20. Reserved Instance vs On-Demand Analysis
**Prompt:** "Analyze my EC2 costs and estimate how much I'm spending on on-demand vs reserved instances. Based on my usage pattern, recommend if I should purchase more reserved instances."

**Tests:** get_cost_by_service, RI coverage analysis, purchase recommendations

---

## 21. Cost Forecast with Confidence Intervals
**Prompt:** "Forecast my costs for the next 3 months based on current trends. Provide best-case, worst-case, and most-likely scenarios. What should I budget for?"

**Tests:** get_cost_forecast, confidence interval analysis, budget planning

---

## 22. Service Sunset Impact Analysis
**Prompt:** "We're planning to decommission our RDS databases in January 2026. Based on current RDS costs, estimate the monthly savings and calculate the annual impact of this decision."

**Tests:** get_cost_by_service, savings projection, annual impact calculation

---

## 23. Cost per Customer/Transaction Analysis
**Prompt:** "If we served 100,000 customers this month, calculate our AWS cost per customer. Compare this with last month's cost per customer. Are we becoming more or less efficient at scale?"

**Tests:** get_current_month_cost, get_last_month_cost, unit economics calculation

---

## 24. Comprehensive Monthly Cost Report
**Prompt:** "Generate a comprehensive cost report for this month including: total costs, top 5 services, comparison with last month, cost drivers, trend analysis, forecast for next month, and 3 specific cost optimization recommendations."

**Tests:** Multiple tools, comprehensive analysis, executive summary generation

---

## 25. Cost Optimization ROI Calculator
**Prompt:** "Based on my current month costs and spending patterns, identify the top 5 cost optimization opportunities. For each opportunity, estimate the potential monthly savings, implementation effort, and ROI timeline."

**Tests:** get_current_month_cost, get_cost_by_service, optimization identification, ROI calculation

---

## How to Use These Prompts

1. **Copy any prompt** from above
2. **Paste into the Streamlit app** chat interface
3. **Review the analysis** provided by Claude
4. **Verify the data** matches your AWS Cost Explorer console
5. **Take action** based on the recommendations

## Expected Outcomes

Each prompt should:
- ✅ Call appropriate MCP tools dynamically
- ✅ Parse and analyze real AWS cost data
- ✅ Provide actionable insights
- ✅ Include specific recommendations
- ✅ Present data in a professional format
- ✅ Answer the complete question asked

## Prompt Categories

- **Trend Analysis:** Prompts 1, 3, 5, 7, 16
- **Budget Management:** Prompts 2, 9, 21
- **Cost Optimization:** Prompts 4, 8, 15, 20, 22, 25
- **Investigation:** Prompts 6, 11, 18, 19
- **Business Impact:** Prompts 10, 13, 23
- **Reporting:** Prompts 12, 14, 24
- **Planning:** Prompts 17, 21, 22

## Success Criteria

A successful test means:
1. The app correctly interprets the question
2. Claude selects the right tools to call
3. Data is accurately parsed and presented
4. Analysis is insightful and actionable
5. Recommendations are specific and valuable
6. No errors or hallucinations occur
