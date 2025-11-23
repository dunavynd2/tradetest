# Azure Cloud Deployment Configuration

## Overview
Deploy the trading bot on Azure using Azure Container Instances, Azure Functions, or Azure Container Apps.

## Prerequisites
- Azure Account
- Azure CLI installed and configured
- Docker installed

## Deployment Options

### Option 1: Azure Container Instances (Recommended for Long-running)

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Create Resource Group:**
   ```bash
   az group create --name trading-bot-rg --location eastus
   ```

3. **Create Azure Container Registry:**
   ```bash
   az acr create --resource-group trading-bot-rg --name tradingobtacr --sku Basic
   ```

4. **Build and push image:**
   ```bash
   az acr build --registry tradingbotacr --image trading-bot:latest .
   ```

5. **Deploy Container Instance:**
   ```bash
   az container create \
     --resource-group trading-bot-rg \
     --name trading-bot-instance \
     --image tradingbotacr.azurecr.io/trading-bot:latest \
     --cpu 1 \
     --memory 1 \
     --registry-login-server tradingbotacr.azurecr.io \
     --registry-username <username> \
     --registry-password <password> \
     --environment-variables \
       ALPACA_API_KEY=<your-key> \
       ALPACA_API_SECRET=<your-secret> \
       ALPACA_PAPER=true \
       TRADING_SYMBOL=AMZN \
       TRADING_INTERVAL=5 \
     --restart-policy Always
   ```

### Option 2: Azure Functions (Scheduled Execution)

1. **Create Function App:**
   ```bash
   az functionapp create \
     --resource-group trading-bot-rg \
     --name trading-bot-function \
     --storage-account <storage-account> \
     --runtime python \
     --runtime-version 3.10 \
     --functions-version 4 \
     --os-type Linux
   ```

2. **Deploy using Azure Functions Core Tools:**
   ```bash
   func azure functionapp publish trading-bot-function
   ```

3. **Configure timer trigger** in function.json:
   ```json
   {
     "bindings": [
       {
         "name": "myTimer",
         "type": "timerTrigger",
         "direction": "in",
         "schedule": "0 */5 * * * *"
       }
     ]
   }
   ```

### Option 3: Azure Container Apps (Modern approach)

1. **Create Container App environment:**
   ```bash
   az containerapp env create \
     --name trading-bot-env \
     --resource-group trading-bot-rg \
     --location eastus
   ```

2. **Deploy Container App:**
   ```bash
   az containerapp create \
     --name trading-bot-app \
     --resource-group trading-bot-rg \
     --environment trading-bot-env \
     --image tradingbotacr.azurecr.io/trading-bot:latest \
     --registry-server tradingbotacr.azurecr.io \
     --registry-username <username> \
     --registry-password <password> \
     --env-vars \
       ALPACA_API_KEY=<your-key> \
       ALPACA_API_SECRET=<your-secret> \
       ALPACA_PAPER=true \
       TRADING_SYMBOL=AMZN \
       TRADING_INTERVAL=5 \
     --cpu 0.5 \
     --memory 1Gi \
     --min-replicas 1 \
     --max-replicas 1
   ```

## Secure Secrets with Azure Key Vault

1. **Create Key Vault:**
   ```bash
   az keyvault create \
     --name trading-bot-vault \
     --resource-group trading-bot-rg \
     --location eastus
   ```

2. **Store secrets:**
   ```bash
   az keyvault secret set --vault-name trading-bot-vault --name alpaca-api-key --value "<your-key>"
   az keyvault secret set --vault-name trading-bot-vault --name alpaca-api-secret --value "<your-secret>"
   ```

3. **Reference in Container Instance:**
   ```bash
   az container create \
     --resource-group trading-bot-rg \
     --name trading-bot-instance \
     --image tradingbotacr.azurecr.io/trading-bot:latest \
     --secrets ALPACA_API_KEY=keyvault://trading-bot-vault.vault.azure.net/secrets/alpaca-api-key \
              ALPACA_API_SECRET=keyvault://trading-bot-vault.vault.azure.net/secrets/alpaca-api-secret
   ```

## Monitoring and Logs

View container logs:
```bash
az container logs --resource-group trading-bot-rg --name trading-bot-instance --follow
```

## Cost Considerations
- **Azure Container Instances**: ~$30-50/month for continuous running
- **Azure Functions**: ~$0.20 per million executions (Consumption plan)
- **Azure Container Apps**: ~$25-40/month for dedicated instances
