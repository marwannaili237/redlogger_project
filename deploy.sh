#!/bin/bash

# Redlogger Deployment Script
# This script helps deploy the Redlogger controller to various platforms

set -e

echo "🔴 Redlogger Deployment Script"
echo "=============================="

# Function to display usage
usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --railway     Deploy to Railway"
    echo "  --docker      Build Docker image"
    echo "  --local       Run locally"
    echo "  --help        Show this help message"
    echo ""
    echo "Environment variables required:"
    echo "  TELEGRAM_BOT_TOKEN    - Y7588831662:AAGsQmG624Dhl6q5opTQS4fGU_SGXE8EcoU"
    echo "  TELEGRAM_CHAT_ID      - 7070240983"
    echo "  NOIP_URL             - https://marwangpt237.ddns.net"
}

# Function to check requirements
check_requirements() {
    echo "Checking requirements..."
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "YOUR_TELEGRAM_BOT_TOKEN" ]; then
        echo "⚠️ Warning: TELEGRAM_BOT_TOKEN not set or using placeholder"
    fi
    
    if [ -z "$TELEGRAM_CHAT_ID" ] || [ "$TELEGRAM_CHAT_ID" = "YOUR_TELEGRAM_CHAT_ID" ]; then
        echo "⚠️ Warning: TELEGRAM_CHAT_ID not set or using placeholder"
    fi
    
    if [ ! -f "controller/redlogger_controller/requirements.txt" ]; then
        echo "❌ Error: requirements.txt not found"
        exit 1
    fi
    
    echo "✅ Requirements check completed"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚀 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    # Login to Railway (if not already logged in)
    railway login
    
    # Create new project or use existing
    railway project create redlogger-controller || true
    
    # Set environment variables
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "YOUR_TELEGRAM_BOT_TOKEN" ]; then
        railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
    fi
    
    if [ -n "$TELEGRAM_CHAT_ID" ] && [ "$TELEGRAM_CHAT_ID" != "YOUR_TELEGRAM_CHAT_ID" ]; then
        railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
    fi
    
    if [ -n "$NOIP_URL" ] && [ "$NOIP_URL" != "YOUR_NOIP_URL" ]; then
        railway variables set NOIP_URL="$NOIP_URL"
    fi
    
    # Deploy
    railway up
    
    echo "✅ Railway deployment completed"
    echo "Check your Railway dashboard for the deployment URL"
}

# Function to build Docker image
build_docker() {
    echo "🐳 Building Docker image..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    docker build -t redlogger-controller .
    
    echo "✅ Docker image built successfully"
    echo "Run with: docker run -p 5000:5000 -e TELEGRAM_BOT_TOKEN=your_token -e TELEGRAM_CHAT_ID=your_chat_id redlogger-controller"
}

# Function to run locally
run_local() {
    echo "🏠 Running locally..."
    
    cd controller/redlogger_controller
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run the application
    echo "Starting Redlogger controller..."
    echo "Access the web interface at: http://localhost:5000"
    python src/main.py
}

# Main script logic
case "$1" in
    --railway)
        check_requirements
        deploy_railway
        ;;
    --docker)
        check_requirements
        build_docker
        ;;
    --local)
        check_requirements
        run_local
        ;;
    --help)
        usage
        ;;
    *)
        echo "❌ Invalid option: $1"
        usage
        exit 1
        ;;
esac

