# XGBoost AMZN Equity Pipeline

## Overview
This project trains an XGBoost model to predict short-term price movements for AMZN using 5-minute data. It includes:

- Model training with GridSearchCV
- Backtesting with Backtrader
- Live trading via Alpaca API
- **Scheduled automated trading** with configurable intervals
- **Cloud deployment** support (AWS, Azure, GCP)
- **Docker containerization** for easy deployment
- Logging and risk management
- **Multiple data source integrations** (local, cloud storage, databases)

## Quick Start

### Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Fetch market data:**
   ```bash
   python fetch_amzn_5min.py
   ```

4. **Train the model:**
   ```bash
   python train_model.py
   ```

5. **Backtest the strategy:**
   ```bash
   python backtest.py
   ```

6. **Run scheduled trading bot:**
   ```bash
   python scheduled_trading.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the bot:**
   ```bash
   docker-compose down
   ```

## Cloud Deployment

The trading bot supports deployment to multiple cloud platforms with automated scheduling:

### AWS
- **Lambda** with EventBridge for scheduled execution
- **ECS Fargate** for long-running containers
- **EC2** with cron scheduling
- See [AWS_DEPLOYMENT.md](cloud-deploy/AWS_DEPLOYMENT.md) for detailed instructions

### Azure
- **Azure Container Instances** for continuous running
- **Azure Functions** with timer triggers
- **Azure Container Apps** for modern serverless containers
- See [AZURE_DEPLOYMENT.md](cloud-deploy/AZURE_DEPLOYMENT.md) for detailed instructions

### Google Cloud Platform
- **Cloud Run** with Cloud Scheduler
- **Cloud Functions** with Pub/Sub triggers
- **GKE** for Kubernetes-based deployment
- **Compute Engine** for traditional VM hosting
- See [GCP_DEPLOYMENT.md](cloud-deploy/GCP_DEPLOYMENT.md) for detailed instructions

## Scheduled Trading

The bot includes a sophisticated scheduling system that runs trades at configurable intervals:

```bash
# Run with default 5-minute interval
python scheduled_trading.py

# Configure via environment variables
export TRADING_INTERVAL=10  # Run every 10 minutes
python scheduled_trading.py
```

**Features:**
- Configurable trading intervals
- Automatic data fetching
- Position management
- Comprehensive logging
- Error handling and recovery
- Environment-based configuration

## Integration & Data Access

The trading bot supports multiple data sources and integration methods:

### Local & Network Drives
- Direct file system access
- Docker volume mounting for persistent storage
- Network file system (NFS) support

### Cloud Storage
- **AWS S3** - Store and retrieve data from S3 buckets
- **Azure Blob Storage** - Azure cloud storage integration
- **Google Cloud Storage** - GCP storage buckets

### Databases
- **PostgreSQL/MySQL** - Relational database support
- **MongoDB** - NoSQL document storage

### Real-time Data
- **Kafka** - Event streaming platform
- **WebSocket** - Real-time market data streams
- **Alpaca WebSocket** - Live trading data

### IDE Integration
- **VS Code Remote** - Edit code on remote servers
- **Docker Extension** - Container management
- **REST API** - Programmatic access to the bot

For detailed integration examples, see [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Alpaca API Configuration
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here
ALPACA_PAPER=true

# Trading Configuration
TRADING_SYMBOL=AMZN
POSITION_SIZE=0.15
MAX_LOSS=0.05

# Scheduling Configuration (in minutes)
TRADING_INTERVAL=5
```

### Data Sources

Configure data source in `.env`:

```bash
# Options: local, s3, azure, gcs, database
DATA_SOURCE=local
DATA_PATH=./data

# Cloud storage (if applicable)
S3_BUCKET=my-trading-data
AZURE_CONNECTION_STRING=...
GCS_BUCKET=my-trading-data

# Database (if applicable)
DATABASE_URL=postgresql://user:pass@localhost/trading
```

## Project Structure

```
tradetest/
├── train_model.py           # Model training script
├── backtest.py              # Backtesting with Backtrader
├── live_trading.py          # One-time live trading execution
├── scheduled_trading.py     # Scheduled automated trading (NEW)
├── load_model.py            # Model loading utility
├── fetch_amzn_5min.py       # Data fetching from Yahoo Finance
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose orchestration
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── README.md                # This file
├── INTEGRATION_GUIDE.md     # Integration & data access guide
├── cloud-deploy/            # Cloud deployment configurations
│   ├── AWS_DEPLOYMENT.md    # AWS deployment guide
│   ├── AZURE_DEPLOYMENT.md  # Azure deployment guide
│   ├── GCP_DEPLOYMENT.md    # GCP deployment guide
│   └── ecs-task-definition.json
└── .github/
    └── workflows/
        └── ci-cd.yml        # GitHub Actions CI/CD pipeline
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow that:
- Runs tests on every push/PR
- Validates dependencies
- Builds Docker images
- (Optional) Deploys to cloud platforms

See [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) for configuration.

## Monitoring & Logging

The bot includes comprehensive logging:

```python
# Logs are written to both console and file
# View real-time logs:
tail -f trading_bot.log

# Docker logs:
docker-compose logs -f
```

## Security Best Practices

1. **Never commit secrets** - Use `.env` files (included in `.gitignore`)
2. **Use cloud secret managers** - AWS Secrets Manager, Azure Key Vault, GCP Secret Manager
3. **Enable paper trading** - Test with `ALPACA_PAPER=true` before live trading
4. **Monitor positions** - Set appropriate `MAX_LOSS` limits
5. **Regular backups** - Back up models and configuration

## Troubleshooting

### Common Issues

**Model file not found:**
```bash
# Ensure you've trained the model first
python train_model.py
```

**API credentials error:**
```bash
# Check your .env file has valid credentials
cat .env
```

**Data not available:**
```bash
# Fetch fresh data
python fetch_amzn_5min.py
```

**Docker container won't start:**
```bash
# Check logs for errors
docker-compose logs
```

## Cost Estimates

### Cloud Hosting (Monthly)
- **AWS Lambda**: ~$1-5 (scheduled runs)
- **AWS ECS Fargate**: ~$30-50 (continuous)
- **Azure Container Instances**: ~$30-50
- **GCP Cloud Run**: ~$15-30
- **Basic VM (EC2/Compute Engine)**: ~$7-15

### API Costs
- **Alpaca API**: Free for paper trading, variable for live
- **Market data**: Included with Alpaca

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Disclaimer

**IMPORTANT**: This bot is for educational and research purposes only. Trading involves substantial risk of loss. Always test thoroughly with paper trading before considering live trading. Past performance does not guarantee future results.

## Support

For questions or issues:
1. Check the [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for integration help
2. Review cloud deployment guides in `cloud-deploy/`
3. Open an issue on GitHub

## Roadmap

- [ ] Multi-asset support
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Portfolio optimization
- [ ] Real-time monitoring dashboard
- [ ] Backtesting web interface
- [ ] Mobile alerts integration
- [ ] Advanced risk management

---

**Happy Trading! 📈**
