FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy controller files
COPY controller/redlogger_controller/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create database directory
RUN mkdir -p src/database

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "src/main.py"]

