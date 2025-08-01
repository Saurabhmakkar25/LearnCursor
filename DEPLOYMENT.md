# 🚀 NSE Indices Fetcher - Deployment Guide

## Quick Start

### Option 1: One-Command Run
```bash
./run.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip3 install Flask Flask-CORS requests pandas python-dotenv APScheduler beautifulsoup4

# Run the app
python3 app.py
```

## 🌐 Access the App

Once running, access the app at:
- **Local**: `http://localhost:5000`
- **Gitpod**: Check the "Ports" tab for port 5000
- **Codespaces**: Use the forwarded port URL
- **Replit**: Will auto-detect and show preview

## 📦 Deployment Options

### 1. **Local Development**
```bash
git clone https://github.com/Saurabhmakkar25/LearnCursor.git
cd LearnCursor
git checkout cursor/fetch-nse-index-values-on-demand-881c
./run.sh
```

### 2. **Heroku Deployment**
```bash
# Create Procfile
echo "web: python app.py" > Procfile

# Deploy
heroku create your-nse-app
git push heroku cursor/fetch-nse-index-values-on-demand-881c:main
```

### 3. **Railway Deployment**
1. Connect GitHub repository
2. Select branch: `cursor/fetch-nse-index-values-on-demand-881c`
3. Railway auto-deploys

### 4. **Render Deployment**
1. Connect repository
2. Build command: `pip install -r requirements.txt`
3. Start command: `python app.py`

### 5. **Docker Deployment**
```bash
# Build image
docker build -t nse-indices-app .

# Run container
docker run -p 5000:5000 nse-indices-app
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```env
FLASK_ENV=production
DEBUG=false
PORT=5000
CACHE_DURATION=60
```

### For Production
```bash
# Use Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🌍 Cloud Platforms

### **Free Hosting Options:**
- ✅ **Heroku** (Easy, 550 free hours/month)
- ✅ **Railway** (Modern, $5 credit free)
- ✅ **Render** (Free tier available)
- ✅ **PythonAnywhere** (Free tier)
- ✅ **Replit** (Always free)

### **Paid Options:**
- **DigitalOcean App Platform** ($5/month)
- **AWS Elastic Beanstalk** (Pay per use)
- **Google Cloud Run** (Pay per request)

## 🛠️ Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   pkill -f "python3 app.py"
   ./run.sh
   ```

2. **Dependencies missing**
   ```bash
   pip3 install -r requirements.txt --break-system-packages
   ```

3. **Permission denied**
   ```bash
   chmod +x run.sh
   ```

4. **API not responding**
   - Check if port 5000 is open
   - Look for firewall restrictions
   - Verify app is running: `ps aux | grep app.py`

## 📊 Features Working

- ✅ **8 NSE Indices** (NIFTY 50, Bank, IT, Auto, Pharma, FMCG, Metal, Energy)
- ✅ **Real-time Updates** (Auto-refresh every minute)
- ✅ **Trending Stocks** (Top gainers/losers)
- ✅ **Most Active Stocks** (High volume trading)
- ✅ **Multiple APIs** (Yahoo Finance, Finnhub, fallbacks)
- ✅ **Mobile Responsive** (Works on all devices)
- ✅ **Error Handling** (Never crashes, always shows data)

## 🔗 API Endpoints

- `GET /` - Web interface
- `GET /api/indices` - All NSE indices
- `GET /api/index/{name}` - Specific index
- `GET /api/trending` - Trending stocks
- `GET /api/most-active` - Most active stocks
- `GET /api/status` - Health check

## 📱 Usage

1. **Web Interface**: Open in browser for full dashboard
2. **API Access**: Use endpoints for programmatic access
3. **Mobile**: Responsive design works on phones/tablets
4. **Real-time**: Data updates automatically

## 🎯 Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Use Gunicorn for production
- [ ] Set up monitoring/logging
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificate
- [ ] Configure caching (Redis)
- [ ] Set up backup strategy

---

**🌟 Your NSE Indices Fetcher is ready to deploy!**