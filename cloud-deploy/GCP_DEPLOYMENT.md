# Google Cloud Platform (GCP) Deployment Configuration

## Overview
Deploy the trading bot on GCP using Cloud Run, Cloud Functions, or Google Kubernetes Engine.

## Prerequisites
- GCP Account with billing enabled
- Google Cloud SDK (gcloud) installed
- Docker installed

## Deployment Options

### Option 1: Cloud Run (Recommended for Containers)

1. **Set up environment:**
   ```bash
   gcloud config set project <your-project-id>
   gcloud auth configure-docker
   ```

2. **Build and push to Container Registry:**
   ```bash
   gcloud builds submit --tag gcr.io/<your-project-id>/trading-bot
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy trading-bot \
     --image gcr.io/<your-project-id>/trading-bot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ALPACA_API_KEY=<your-key>,ALPACA_API_SECRET=<your-secret>,ALPACA_PAPER=true,TRADING_SYMBOL=AMZN,TRADING_INTERVAL=5 \
     --memory 512Mi \
     --cpu 1 \
     --min-instances 1 \
     --max-instances 1
   ```

4. **Schedule with Cloud Scheduler:**
   ```bash
   gcloud scheduler jobs create http trading-bot-schedule \
     --schedule="*/5 * * * *" \
     --uri="https://trading-bot-<hash>-uc.a.run.app/trade" \
     --http-method=GET
   ```

### Option 2: Cloud Functions (Scheduled Execution)

1. **Create function directory structure:**
   ```
   cloud-deploy/gcp-function/
   ├── main.py
   ├── requirements.txt
   └── .env.yaml
   ```

2. **Deploy Cloud Function:**
   ```bash
   gcloud functions deploy trading_bot_function \
     --runtime python310 \
     --trigger-topic trading-bot-topic \
     --entry-point execute_trade \
     --env-vars-file .env.yaml \
     --memory 512MB \
     --timeout 300s \
     --region us-central1
   ```

3. **Create Cloud Scheduler job:**
   ```bash
   gcloud scheduler jobs create pubsub trading-bot-scheduler \
     --schedule="*/5 * * * *" \
     --topic=trading-bot-topic \
     --message-body='{"action":"trade"}' \
     --location=us-central1
   ```

### Option 3: Google Kubernetes Engine (GKE) - For Advanced Users

1. **Create GKE cluster:**
   ```bash
   gcloud container clusters create trading-bot-cluster \
     --num-nodes=1 \
     --machine-type=e2-small \
     --region=us-central1
   ```

2. **Apply Kubernetes deployment** (see `gke-deployment.yaml`)
   ```bash
   kubectl apply -f cloud-deploy/gcp/gke-deployment.yaml
   ```

### Option 4: Compute Engine VM (Traditional)

1. **Create VM instance:**
   ```bash
   gcloud compute instances create trading-bot-vm \
     --machine-type=e2-micro \
     --zone=us-central1-a \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --boot-disk-size=10GB
   ```

2. **SSH and setup:**
   ```bash
   gcloud compute ssh trading-bot-vm --zone=us-central1-a
   
   # Inside VM
   sudo apt update
   sudo apt install docker.io docker-compose git -y
   git clone <repository-url>
   cd tradetest
   docker-compose up -d
   ```

## Secure Secrets with Secret Manager

1. **Enable Secret Manager API:**
   ```bash
   gcloud services enable secretmanager.googleapis.com
   ```

2. **Create secrets:**
   ```bash
   echo -n "<your-api-key>" | gcloud secrets create alpaca-api-key --data-file=-
   echo -n "<your-api-secret>" | gcloud secrets create alpaca-api-secret --data-file=-
   ```

3. **Grant Cloud Run access:**
   ```bash
   gcloud secrets add-iam-policy-binding alpaca-api-key \
     --member=serviceAccount:<project-id>@appspot.gserviceaccount.com \
     --role=roles/secretmanager.secretAccessor
   ```

4. **Mount secrets in Cloud Run:**
   ```bash
   gcloud run deploy trading-bot \
     --image gcr.io/<your-project-id>/trading-bot \
     --update-secrets ALPACA_API_KEY=alpaca-api-key:latest,ALPACA_API_SECRET=alpaca-api-secret:latest
   ```

## Monitoring and Logging

View logs:
```bash
gcloud run logs read --service trading-bot --limit 50 --format json
```

Set up monitoring:
```bash
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.yaml
```

## Cost Considerations
- **Cloud Run**: ~$15-30/month (with minimum instances)
- **Cloud Functions**: ~$0.40 per million invocations
- **Compute Engine**: e2-micro ~$7/month with sustained use discount
- **GKE**: ~$75/month (cluster management + nodes)

## Best Practices
1. Use Secret Manager for credentials
2. Enable Cloud Logging and Monitoring
3. Set up alerts for failures
4. Use Cloud Build for CI/CD
5. Implement health checks
