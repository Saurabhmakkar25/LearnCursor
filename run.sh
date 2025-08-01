#!/bin/bash

echo "🚀 Starting NSE Indices Fetcher App..."
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, requests, pandas" 2>/dev/null || {
    echo "📥 Installing required packages..."
    pip3 install Flask Flask-CORS requests pandas python-dotenv APScheduler beautifulsoup4 --break-system-packages --quiet
}

# Stop any existing instance
echo "🛑 Stopping any existing instances..."
pkill -f "python3 app.py" 2>/dev/null || true

# Start the app
echo "🌟 Starting the NSE Indices Fetcher..."
echo "📊 Available indices: NIFTY 50, NIFTY Bank, NIFTY IT, Auto, Pharma, FMCG, Metal, Energy"
echo "🌐 Server will be available at: http://localhost:5000"
echo "=================================="

python3 app.py