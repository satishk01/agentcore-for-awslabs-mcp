"# agentcore-for-awslabs-mcp" 


Step 1  - Setup Cognito
python3 ./setup-cognito-pool.py

Step2 - deploy the agent core runtime
python3 ./deploy-pricing.py

step3 - update the role permission for Cost explorer
python3 ./pricing-agentcore-role.py


step4 - Start the streamlit application
streamlit run streamlit_pricing.py

The file PRICING-TEST-PROMPTS.txt has sample prompts we can use to test the system