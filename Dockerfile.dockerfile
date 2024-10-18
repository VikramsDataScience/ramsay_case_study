FROM python:3.11-slim

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