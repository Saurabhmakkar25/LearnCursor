# NSE Indices Fetcher

A comprehensive web application to fetch and display NSE (National Stock Exchange) indices values on demand. This app provides real-time data for major Indian stock market indices with a beautiful, responsive web interface.

## 🚀 Features

- **Real-time NSE Indices Data**: Get live data for NIFTY 50, NIFTY Bank, NIFTY IT, and more
- **Multiple Data Sources**: Integrated with multiple APIs for reliable data fetching
- **Trending Stocks**: View top gainers and losers in the market  
- **Most Active Stocks**: Track the most actively traded stocks
- **Auto Refresh**: Automatic data updates every minute
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern UI**: Beautiful gradient design with smooth animations
- **API Documentation**: Built-in API documentation for developers
- **Caching System**: Intelligent caching to prevent excessive API calls
- **Error Handling**: Robust error handling with fallback mechanisms

## 📊 Supported Indices

- **NIFTY 50** - Top 50 companies by market cap
- **NIFTY Bank** - Banking sector index
- **NIFTY IT** - Information Technology sector index
- **NIFTY Auto** - Automobile sector index
- **NIFTY Pharma** - Pharmaceutical sector index
- **NIFTY FMCG** - Fast Moving Consumer Goods index
- **NIFTY Metal** - Metal sector index
- **NIFTY Energy** - Energy sector index

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **Python 3.8+** - Programming language
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP library for API calls
- **APScheduler** - Background task scheduling
- **nsescraper** - NSE data scraping library

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Font Awesome** - Icons
- **Animate.css** - CSS animations
- **Chart.js** - Data visualization (ready for charts)

### Data Sources
- **nsescraper** - Primary NSE data source
- **Yahoo Finance API** - Fallback data source
- **Indian API** - Additional market data
- **Mock Data** - Demo data when APIs are unavailable

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nse-indices-fetcher
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔧 Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify as needed:

```env
# Flask Configuration
FLASK_ENV=development
DEBUG=true
PORT=5000

# API Configuration
CACHE_DURATION=60
REFRESH_INTERVAL=60000

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0
```

## 🌐 API Endpoints

The application provides a RESTful API for accessing NSE data:

### Get All Indices
```http
GET /api/indices
```
Returns data for all supported NSE indices.

### Get Specific Index
```http
GET /api/index/{index_name}
```
Returns data for a specific index (e.g., `NIFTY%2050`, `NIFTY%20BANK`).

### Get Trending Stocks
```http
GET /api/trending
```
Returns top gainers and losers in the market.

### Get Most Active Stocks
```http
GET /api/most-active
```
Returns most actively traded stocks.

### API Status
```http
GET /api/status
```
Returns API health status and available indices.

### Example Response
```json
{
  "success": true,
  "data": [
    {
      "index_name": "NIFTY 50",
      "symbol": "NIFTY",
      "description": "Nifty 50 Index",
      "current_price": 21500.75,
      "previous_close": 21450.30,
      "change": 50.45,
      "change_percent": 0.24,
      "day_high": 21580.20,
      "day_low": 21420.10,
      "timestamp": "2024-01-15T14:30:00.000Z",
      "data_source": "nsescraper"
    }
  ],
  "timestamp": "2024-01-15T14:30:00.000Z",
  "total_indices": 8
}
```

## 🎨 Features in Detail

### Real-time Data Updates
- Automatic refresh every 60 seconds
- Manual refresh button
- Pause refresh when tab is not active
- Visual loading indicators

### Market Status
- Shows market open/close status
- Based on NSE trading hours (9:15 AM - 3:30 PM, Monday-Friday)
- Real-time status updates

### Responsive Design
- Mobile-first approach
- Tablet and desktop optimized
- Touch-friendly interface
- Modern gradient backgrounds

### Error Handling
- Multiple data source fallbacks
- Graceful error messages
- Retry mechanisms
- Offline support with cached data

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production
```env
FLASK_ENV=production
DEBUG=false
PORT=5000
CACHE_DURATION=60
```

## 📱 Usage

### Web Interface
1. Open the application in your browser
2. View real-time NSE indices data on the main dashboard
3. Click "Refresh" to manually update data
4. Switch between "Trending Stocks" and "Most Active" tabs
5. Use keyboard shortcuts: `Ctrl+R` to refresh, `Escape` to close modals

### API Usage
```python
import requests

# Get all indices
response = requests.get('http://localhost:5000/api/indices')
data = response.json()

# Get specific index
response = requests.get('http://localhost:5000/api/index/NIFTY%2050')
nifty_data = response.json()
```

### JavaScript Integration
```javascript
// Fetch indices data
fetch('/api/indices')
  .then(response => response.json())
  .then(data => {
    console.log('Indices data:', data);
  });
```

## 🔍 Troubleshooting

### Common Issues

1. **Dependencies not installing**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Port already in use**
   ```bash
   export PORT=8000  # Use different port
   python app.py
   ```

3. **API data not loading**
   - Check internet connection
   - Verify API endpoints are accessible
   - Check logs for error messages

4. **Performance issues**
   - Increase cache duration in `.env`
   - Use Redis for production caching
   - Reduce refresh interval

### Logs
The application logs important events and errors. Check the console output for debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and informational purposes only. The data provided should not be used for actual trading decisions. Always consult with financial advisors before making investment decisions.

## 🙏 Acknowledgments

- **NSE India** for providing market data
- **nsescraper** library for NSE data access
- **Yahoo Finance** for additional market data
- **Indian API** for comprehensive stock market data
- **Font Awesome** for beautiful icons
- **Chart.js** for data visualization capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) section
2. Create a new issue with detailed information
3. Include error logs and system information

## 🔮 Future Enhancements

- [ ] Historical data charts
- [ ] Portfolio tracking
- [ ] Price alerts and notifications
- [ ] Export data to CSV/Excel
- [ ] Dark/Light theme toggle
- [ ] Real-time WebSocket updates
- [ ] Mobile app version
- [ ] Advanced technical indicators
- [ ] Multi-language support
- [ ] User authentication and preferences

---

**Made with ❤️ for the Indian stock market community**