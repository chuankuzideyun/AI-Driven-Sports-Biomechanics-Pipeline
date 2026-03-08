# Use a base image for a small footprint
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ . 

# Create necessary directories for runtime data
RUN mkdir -p output data

# Ensure Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]