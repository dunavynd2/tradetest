# Quick Start Guide - Cloud Deployment & Scheduling

## What's New?

This trading bot now includes:
1. **Scheduled automated trading** - Runs at configurable intervals
2. **Cloud deployment** - Deploy to AWS, Azure, or GCP
3. **Docker support** - Containerized for easy deployment
4. **REST API** - Monitor and control remotely
5. **Multiple data sources** - Cloud storage, databases, and more

## Quick Start Options

### Option 1: Run Locally with Scheduling (Easiest)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Alpaca API keys
   ```

3. **Run the scheduled bot:**
   ```bash
   python scheduled_trading.py
   ```
   
   The bot will:
   - Run every 5 minutes (configurable)
   - Make trading decisions based on the model
   - Log all activity to `trading_bot.log`

### Option 2: Run with Docker (Recommended)

1. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Alpaca API keys
   ```

2. **Start the container:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

### Option 3: Deploy to Cloud (Production)

Choose your platform:

#### AWS
See [cloud-deploy/AWS_DEPLOYMENT.md](cloud-deploy/AWS_DEPLOYMENT.md)
- Lambda + EventBridge: ~$1-5/month
- ECS Fargate: ~$30-50/month

#### Azure
See [cloud-deploy/AZURE_DEPLOYMENT.md](cloud-deploy/AZURE_DEPLOYMENT.md)
- Container Instances: ~$30-50/month
- Functions: ~$1-10/month

#### GCP (Recommended for beginners)
See [cloud-deploy/GCP_DEPLOYMENT.md](cloud-deploy/GCP_DEPLOYMENT.md)
- Cloud Run: ~$15-30/month
- Cloud Functions: ~$1-5/month

**Quick GCP Deploy:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/trading-bot
gcloud run deploy trading-bot --image gcr.io/YOUR_PROJECT/trading-bot
```

## Configuration

Edit `.env` file:

```bash
# Alpaca API (Required)
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret
ALPACA_PAPER=true  # Use paper trading for testing

# Trading Settings
TRADING_SYMBOL=AMZN
TRADING_INTERVAL=5  # Minutes between trades
POSITION_SIZE=0.15
MAX_LOSS=0.05
```

## Monitoring

### View Logs
```bash
# Local
tail -f trading_bot.log

# Docker
docker-compose logs -f

# Cloud (AWS)
aws logs tail /aws/lambda/trading-bot --follow

# Cloud (GCP)
gcloud run logs read --service trading-bot --limit 50
```

### REST API (Optional)

Start the API server:
```bash
python api_server.py
```

Then access:
- `http://localhost:5000/status` - Bot status
- `http://localhost:5000/positions` - Current positions
- `http://localhost:5000/orders` - Recent orders
- `http://localhost:5000/health` - Health check

## Understanding the Scheduling

The bot uses Python's `schedule` library to run at intervals:

```python
# Runs every 5 minutes (default)
schedule.every(5).minutes.do(trade)

# Change interval via environment variable
TRADING_INTERVAL=10  # Every 10 minutes
```

For cloud platforms, you can also use native schedulers:
- AWS: EventBridge
- Azure: Logic Apps / Timer Triggers
- GCP: Cloud Scheduler

## Data Access & Integration

The bot can access data from multiple sources:

### Local Files
```bash
# Mount local directories in docker-compose.yml
volumes:
  - ./data:/app/data
  - ~/my-trading-data:/app/external
```

### Cloud Storage
```python
# AWS S3
DATA_SOURCE=s3
S3_BUCKET=my-trading-data

# Azure Blob
DATA_SOURCE=azure
AZURE_CONNECTION_STRING=...

# Google Cloud Storage
DATA_SOURCE=gcs
GCS_BUCKET=my-trading-data
```

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for complete examples.

## Choosing a Cloud Platform

See [CLOUD_COMPARISON.md](CLOUD_COMPARISON.md) for detailed comparison.

**Quick Recommendation:**
- **New users**: Start with GCP Cloud Run (easiest, cheapest)
- **AWS users**: Use Lambda + EventBridge
- **24/7 trading**: Use ECS Fargate or Cloud Run
- **Lowest cost**: Cloud Functions with scheduling

## Security Checklist

- [ ] Use `.env` file for secrets (never commit)
- [ ] Enable paper trading (`ALPACA_PAPER=true`) for testing
- [ ] Use cloud secret managers for production
- [ ] Set appropriate `MAX_LOSS` limits
- [ ] Monitor logs regularly
- [ ] Test thoroughly before live trading

## Troubleshooting

### "Model file not found"
```bash
python train_model.py  # Train the model first
```

### "No data available"
```bash
python fetch_amzn_5min.py  # Fetch market data
```

### "API authentication failed"
Check your `.env` file has valid Alpaca credentials.

### "Container won't start"
```bash
docker-compose logs  # Check error messages
```

## Next Steps

1. **Test locally** with paper trading
2. **Monitor logs** to ensure it's working
3. **Deploy to cloud** when ready
4. **Set up monitoring** and alerts
5. **Gradually increase** position sizes

## Support

- Check [README.md](README.md) for full documentation
- Review [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for data access
- See cloud-specific guides in `cloud-deploy/` directory

## Important Warning

⚠️ **This bot is for educational purposes only.** Trading involves substantial risk. Always:
- Test with paper trading first
- Start with small position sizes
- Monitor regularly
- Understand the risks
- Never trade with money you can't afford to lose

---

**Happy Trading! 📈**

For questions, open an issue on GitHub.
