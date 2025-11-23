# Integration and Data Access Extensions

## Overview
This document outlines various extensions and integrations available for accessing data from local drives, cloud storage, and other data sources for the trading bot.

## Local Drive Access Extensions

### 1. File System Integration
The trading bot can access local data files through standard Python file I/O operations:

```python
import pandas as pd
import os

# Access local CSV files
def load_local_data(file_path):
    """Load data from local drive"""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        raise FileNotFoundError(f"Data file not found: {file_path}")

# Example usage
local_data = load_local_data('/path/to/your/data/amzn_5min.csv')
```

### 2. Volume Mounting (Docker)
Mount local directories to the Docker container for data persistence:

```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data              # Mount local data directory
  - ./model:/app/model            # Mount model directory
  - ~/trading-data:/app/external  # Mount any external drive
```

For Windows:
```yaml
volumes:
  - C:/Users/YourName/TradingData:/app/data
```

For Mac/Linux:
```yaml
volumes:
  - /home/username/trading-data:/app/data
  - /mnt/external-drive:/app/external
```

### 3. Network File System (NFS) Access
Access network drives and shared folders:

```python
# Mount network drive (Linux/Mac)
import subprocess

def mount_network_drive(network_path, mount_point):
    """Mount a network drive"""
    subprocess.run(['mount', '-t', 'cifs', network_path, mount_point])
```

## Cloud Storage Integration

### 1. AWS S3 Integration

```python
import boto3
import pandas as pd
from io import StringIO

def load_from_s3(bucket, key):
    """Load data from S3 bucket"""
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    data = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
    return data

def save_to_s3(df, bucket, key):
    """Save data to S3 bucket"""
    s3_client = boto3.client('s3')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
```

Add to requirements.txt:
```
boto3>=1.26.0
```

### 2. Azure Blob Storage Integration

```python
from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import BytesIO

def load_from_azure_blob(connection_string, container, blob_name):
    """Load data from Azure Blob Storage"""
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
    
    download_stream = blob_client.download_blob()
    data = pd.read_csv(BytesIO(download_stream.readall()))
    return data

def save_to_azure_blob(df, connection_string, container, blob_name):
    """Save data to Azure Blob Storage"""
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    blob_client.upload_blob(output, overwrite=True)
```

Add to requirements.txt:
```
azure-storage-blob>=12.14.0
```

### 3. Google Cloud Storage Integration

```python
from google.cloud import storage
import pandas as pd
from io import BytesIO

def load_from_gcs(bucket_name, blob_name):
    """Load data from Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    data = blob.download_as_bytes()
    return pd.read_csv(BytesIO(data))

def save_to_gcs(df, bucket_name, blob_name):
    """Save data to Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    blob.upload_from_file(output, content_type='text/csv')
```

Add to requirements.txt:
```
google-cloud-storage>=2.10.0
```

## Database Integration

### 1. PostgreSQL/MySQL Integration

```python
import pandas as pd
from sqlalchemy import create_engine

def load_from_database(connection_string, query):
    """Load data from SQL database"""
    engine = create_engine(connection_string)
    data = pd.read_sql(query, engine)
    return data

# Example connection strings:
# PostgreSQL: postgresql://user:password@localhost:5432/database
# MySQL: mysql+pymysql://user:password@localhost:3306/database

def save_to_database(df, connection_string, table_name):
    """Save data to SQL database"""
    engine = create_engine(connection_string)
    df.to_sql(table_name, engine, if_exists='append', index=False)
```

Add to requirements.txt:
```
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0  # For PostgreSQL
pymysql>=1.0.0          # For MySQL
```

### 2. MongoDB Integration

```python
from pymongo import MongoClient
import pandas as pd

def load_from_mongodb(connection_string, database, collection, query=None):
    """Load data from MongoDB"""
    client = MongoClient(connection_string)
    db = client[database]
    coll = db[collection]
    
    cursor = coll.find(query or {})
    data = pd.DataFrame(list(cursor))
    return data

def save_to_mongodb(df, connection_string, database, collection):
    """Save data to MongoDB"""
    client = MongoClient(connection_string)
    db = client[database]
    coll = db[collection]
    
    records = df.to_dict('records')
    coll.insert_many(records)
```

Add to requirements.txt:
```
pymongo>=4.3.0
```

## Real-time Data Streaming

### 1. Kafka Integration

```python
from kafka import KafkaConsumer, KafkaProducer
import json

def consume_from_kafka(topic, bootstrap_servers):
    """Consume data from Kafka topic"""
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    for message in consumer:
        yield message.value

def produce_to_kafka(topic, data, bootstrap_servers):
    """Produce data to Kafka topic"""
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    producer.send(topic, value=data)
```

Add to requirements.txt:
```
kafka-python>=2.0.0
```

### 2. WebSocket Integration

```python
import websocket
import json

def connect_to_websocket(url, on_message_callback):
    """Connect to WebSocket for real-time data"""
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message_callback
    )
    ws.run_forever()

# Example: Alpaca WebSocket for real-time market data
from alpaca.data.live import StockDataStream

def stream_market_data():
    stream = StockDataStream(api_key, api_secret)
    
    @stream.on_bar('AMZN')
    async def on_bar(bar):
        print(f"Received bar: {bar}")
    
    stream.run()
```

## IDE-like Integration (Similar to Claude Code)

### 1. VS Code Extension Compatibility
The trading bot is designed to work seamlessly with VS Code:

- **Remote Development**: Use VS Code Remote SSH to edit code on remote servers
- **Docker Extension**: Manage containers directly from VS Code
- **Python Extension**: Full IntelliSense and debugging support
- **Jupyter Notebooks**: Analyze trading data interactively

### 2. File System Watchers
Automatically reload data when files change:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DataFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.csv'):
            print(f"Data file updated: {event.src_path}")
            # Reload model or data
            load_model()

def watch_directory(path):
    event_handler = DataFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
```

Add to requirements.txt:
```
watchdog>=3.0.0
```

### 3. API Server for Remote Access

```python
from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def get_status():
    """Get bot status"""
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()})

@app.route('/trade', methods=['POST'])
def manual_trade():
    """Trigger manual trade"""
    trade()
    return jsonify({"message": "Trade executed"})

@app.route('/data', methods=['GET'])
def get_data():
    """Retrieve latest data"""
    data = fetch_latest_data()
    return jsonify(data.to_dict())

def run_api_server():
    app.run(host='0.0.0.0', port=5000)

# Run in separate thread
api_thread = threading.Thread(target=run_api_server, daemon=True)
api_thread.start()
```

Add to requirements.txt:
```
flask>=2.3.0
```

## Configuration Management

### Environment-based Configuration

```python
import os
from dotenv import load_dotenv

class Config:
    """Configuration management"""
    
    def __init__(self):
        load_dotenv()
        
        # Data source configuration
        self.data_source = os.getenv('DATA_SOURCE', 'local')  # local, s3, azure, gcs
        self.data_path = os.getenv('DATA_PATH', './data')
        
        # Cloud storage configuration
        self.s3_bucket = os.getenv('S3_BUCKET')
        self.azure_connection = os.getenv('AZURE_CONNECTION_STRING')
        self.gcs_bucket = os.getenv('GCS_BUCKET')
        
        # Database configuration
        self.db_connection = os.getenv('DATABASE_URL')
        
        # API configuration
        self.api_enabled = os.getenv('API_ENABLED', 'false').lower() == 'true'
        self.api_port = int(os.getenv('API_PORT', '5000'))

config = Config()
```

## Summary

The trading bot supports multiple integration methods:

1. **Local Access**: Direct file system access, volume mounting
2. **Cloud Storage**: AWS S3, Azure Blob, Google Cloud Storage
3. **Databases**: PostgreSQL, MySQL, MongoDB
4. **Streaming**: Kafka, WebSocket
5. **Remote Access**: REST API, VS Code Remote Development
6. **IDE Integration**: Compatible with VS Code, PyCharm, Jupyter

For Claude Code-like experience:
- Use VS Code with Remote SSH for editing code on any machine
- Mount local/network drives as Docker volumes
- Enable the REST API for programmatic access
- Use file watchers for automatic updates
