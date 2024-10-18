FROM python:3.11-slim

# Install the required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
libgomp1 \
&& rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt to working directory
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files to the container
COPY . . 

# Set python path to the /app root folder
ENV PYTHONPATH=/app

# Copy the data directory to working directory
RUN mkdir -p /app/data
COPY data/ /app/data/