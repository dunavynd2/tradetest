# AWS Lambda Deployment Configuration

## Overview
This configuration allows you to deploy the trading bot as an AWS Lambda function with EventBridge for scheduling.

## Prerequisites
- AWS Account
- AWS CLI configured
- Docker installed (for Lambda container images)
- Serverless Framework or SAM CLI (optional)

## Deployment Steps

### Option 1: Using AWS Lambda with EventBridge

1. **Build the Docker image:**
   ```bash
   docker build -t trading-bot-lambda .
   ```

2. **Tag and push to Amazon ECR:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag trading-bot-lambda:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/trading-bot:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/trading-bot:latest
   ```

3. **Create Lambda function using AWS CLI:**
   ```bash
   aws lambda create-function \
     --function-name trading-bot \
     --package-type Image \
     --code ImageUri=<account-id>.dkr.ecr.us-east-1.amazonaws.com/trading-bot:latest \
     --role arn:aws:iam::<account-id>:role/lambda-execution-role \
     --timeout 300 \
     --memory-size 512 \
     --environment Variables="{ALPACA_API_KEY=xxx,ALPACA_API_SECRET=xxx,ALPACA_PAPER=true}"
   ```

4. **Create EventBridge rule for scheduling:**
   ```bash
   aws events put-rule \
     --name trading-bot-schedule \
     --schedule-expression "rate(5 minutes)"
   
   aws events put-targets \
     --rule trading-bot-schedule \
     --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<account-id>:function:trading-bot"
   
   aws lambda add-permission \
     --function-name trading-bot \
     --statement-id trading-bot-schedule \
     --action 'lambda:InvokeFunction' \
     --principal events.amazonaws.com \
     --source-arn arn:aws:events:us-east-1:<account-id>:rule/trading-bot-schedule
   ```

### Option 2: Using AWS ECS Fargate (Long-running)

1. **Create ECS task definition** (see `ecs-task-definition.json`)

2. **Create ECS cluster:**
   ```bash
   aws ecs create-cluster --cluster-name trading-bot-cluster
   ```

3. **Register task definition:**
   ```bash
   aws ecs register-task-definition --cli-input-json file://cloud-deploy/aws/ecs-task-definition.json
   ```

4. **Run the task:**
   ```bash
   aws ecs run-task \
     --cluster trading-bot-cluster \
     --launch-type FARGATE \
     --task-definition trading-bot-task \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

### Option 3: Using EC2 with cron

1. **Launch EC2 instance** (Ubuntu/Amazon Linux)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip docker.io docker-compose
   ```
3. **Clone repository and deploy:**
   ```bash
   git clone <repository-url>
   cd tradetest
   docker-compose up -d
   ```

## Environment Variables
Store sensitive data in AWS Secrets Manager or Parameter Store:

```bash
aws secretsmanager create-secret \
  --name trading-bot/alpaca-credentials \
  --secret-string '{"api_key":"xxx","api_secret":"xxx"}'
```

## Cost Considerations
- **Lambda**: Pay per invocation (~$0.20 per million requests)
- **ECS Fargate**: Pay for vCPU and memory per hour (~$30-50/month)
- **EC2**: Pay for instance time (t3.micro ~$7.50/month)
