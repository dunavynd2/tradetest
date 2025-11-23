FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for data and model
RUN mkdir -p data model

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the scheduled trading bot
CMD ["python", "scheduled_trading.py"]
