# Use a slim Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Updated libgl1-mesa-glx to libgl1 which is the current standard
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ . 

# Create output and data directories
RUN mkdir -p output data

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose the Flask port
EXPOSE 5000

# Start the Flask web server
CMD ["python", "app.py"]