from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
from functools import wraps
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache for indices data
indices_cache = {}
cache_timestamp = {}
CACHE_DURATION = 60  # Cache for 1 minute

# NSE Indices configuration
NSE_INDICES = {
    'NIFTY 50': {
        'symbol': 'NIFTY',
        'description': 'Nifty 50 Index',
        'api_symbol': 'NIFTY 50'
    },
    'NIFTY BANK': {
        'symbol': 'BANKNIFTY',
        'description': 'Nifty Bank Index',
        'api_symbol': 'NIFTY BANK'
    },
    'NIFTY IT': {
        'symbol': 'NIFTYIT',
        'description': 'Nifty IT Index',
        'api_symbol': 'NIFTY IT'
    },
    'NIFTY AUTO': {
        'symbol': 'NIFTYAUTO',
        'description': 'Nifty Auto Index',
        'api_symbol': 'NIFTY AUTO'
    },
    'NIFTY PHARMA': {
        'symbol': 'NIFTYPHARMA',
        'description': 'Nifty Pharma Index',
        'api_symbol': 'NIFTY PHARMA'
    },
    'NIFTY FMCG': {
        'symbol': 'NIFTYFMCG',
        'description': 'Nifty FMCG Index',
        'api_symbol': 'NIFTY FMCG'
    },
    'NIFTY METAL': {
        'symbol': 'NIFTYMETAL',
        'description': 'Nifty Metal Index',
        'api_symbol': 'NIFTY METAL'
    },
    'NIFTY ENERGY': {
        'symbol': 'NIFTYENERGY',
        'description': 'Nifty Energy Index',
        'api_symbol': 'NIFTY ENERGY'
    }
}

def cache_response(duration=CACHE_DURATION):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f.__name__ + str(args) + str(sorted(kwargs.items()))
            
            # Check if data is in cache and not expired
            if (cache_key in indices_cache and 
                cache_key in cache_timestamp and
                time.time() - cache_timestamp[cache_key] < duration):
                return indices_cache[cache_key]
            
            # Get fresh data
            result = f(*args, **kwargs)
            
            # Cache the result
            indices_cache[cache_key] = result
            cache_timestamp[cache_key] = time.time()
            
            return result
        return decorated_function
    return decorator

class NSEDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_urls = {
            'indian_api': 'https://indianapi.in',
            'nse_official': 'https://www.nseindia.com/api',
            'yahoo_finance': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'finnhub': 'https://finnhub.io/api/v1',
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'polygon': 'https://api.polygon.io/v2',
            'marketstack': 'http://api.marketstack.com/v1'
        }

    def fetch_from_indian_api(self, endpoint):
        """Fetch data from Indian API"""
        try:
            url = f"{self.base_urls['indian_api']}/{endpoint}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching from Indian API: {e}")
            return None

    def fetch_nse_trending(self):
        """Fetch trending stocks from multiple sources"""
        # Try Indian API first
        data = self.fetch_from_indian_api('trending')
        if data:
            return data
            
        # Fallback: Generate trending data based on popular NSE stocks
        return self.generate_trending_fallback()

    def fetch_nse_most_active(self):
        """Fetch most active NSE stocks from multiple sources"""
        # Try Indian API first
        data = self.fetch_from_indian_api('NSE_most_active')
        if data:
            return data
            
        # Fallback: Generate most active data
        return self.generate_most_active_fallback()

    def generate_trending_fallback(self):
        """Generate fallback trending data with popular NSE stocks"""
        import random
        
        popular_stocks = [
            {'ticker': 'RELIANCE', 'name': 'Reliance Industries'},
            {'ticker': 'TCS', 'name': 'Tata Consultancy Services'},
            {'ticker': 'HDFCBANK', 'name': 'HDFC Bank'},
            {'ticker': 'INFY', 'name': 'Infosys'},
            {'ticker': 'HINDUNILVR', 'name': 'Hindustan Unilever'},
            {'ticker': 'ICICIBANK', 'name': 'ICICI Bank'},
            {'ticker': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank'},
            {'ticker': 'BHARTIARTL', 'name': 'Bharti Airtel'},
            {'ticker': 'ITC', 'name': 'ITC'},
            {'ticker': 'AXISBANK', 'name': 'Axis Bank'}
        ]
        
        # Generate random data for trending stocks
        gainers = []
        losers = []
        
        for i in range(5):
            stock = random.choice(popular_stocks)
            base_price = random.uniform(100, 3000)
            change_percent = random.uniform(1, 8)  # Positive for gainers
            
            gainers.append({
                'ticker_id': stock['ticker'],
                'company_name': stock['name'],
                'price': round(base_price, 2),
                'percent_change': round(change_percent, 2),
                'net_change': round(base_price * change_percent / 100, 2)
            })
            
        for i in range(5):
            stock = random.choice(popular_stocks)
            base_price = random.uniform(100, 3000)
            change_percent = -random.uniform(1, 6)  # Negative for losers
            
            losers.append({
                'ticker_id': stock['ticker'],
                'company_name': stock['name'],
                'price': round(base_price, 2),
                'percent_change': round(change_percent, 2),
                'net_change': round(base_price * change_percent / 100, 2)
            })
        
        return {
            'trending_stocks': {
                'top_gainers': gainers,
                'top_losers': losers
            }
        }

    def generate_most_active_fallback(self):
        """Generate fallback most active stocks data"""
        import random
        
        active_stocks = [
            'Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank',
            'Infosys', 'ICICI Bank', 'State Bank of India', 'Bharti Airtel',
            'Hindustan Unilever', 'Kotak Mahindra Bank', 'Axis Bank',
            'Larsen & Toubro', 'Asian Paints', 'Maruti Suzuki',
            'Bajaj Finance', 'HCL Technologies'
        ]
        
        most_active = []
        for i, company in enumerate(active_stocks[:10]):
            base_price = random.uniform(200, 2500)
            change_percent = random.uniform(-3, 4)
            
            most_active.append({
                'company': company,
                'ticker': company.upper().replace(' ', '').replace('&', '')[:10],
                'price': round(base_price, 2),
                'percent_change': round(change_percent, 2),
                'net_change': round(base_price * change_percent / 100, 2),
                'volume': random.randint(1000000, 50000000)
            })
            
        return most_active

    def fetch_from_nsescraper(self, index_name):
        """Fetch data using nsescraper library"""
        try:
            # Try to import and use nsescraper
            from nsescraper import intraday_index
            data = intraday_index(index_name)
            return data
        except ImportError:
            logger.warning("nsescraper not available, skipping this data source")
            return None
        except Exception as e:
            logger.error(f"Error fetching from nsescraper: {e}")
            return None

    def fetch_from_yahoo_finance(self, symbol):
        """Fetch data from Yahoo Finance as fallback"""
        try:
            yahoo_symbol = f"{symbol}.NS"
            url = f"{self.base_urls['yahoo_finance']}/{yahoo_symbol}"
            params = {
                'interval': '1m',
                'range': '1d'
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                return {
                    'symbol': symbol,
                    'current_price': meta.get('regularMarketPrice', 0),
                    'previous_close': meta.get('previousClose', 0),
                    'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                    'change_percent': ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0)) / meta.get('previousClose', 1)) * 100,
                    'day_high': meta.get('regularMarketDayHigh', 0),
                    'day_low': meta.get('regularMarketDayLow', 0),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance: {e}")
            return None

    def fetch_from_finnhub(self, symbol):
        """Fetch data from Finnhub (free tier - no API key needed for basic quotes)"""
        try:
            # Finnhub free tier allows some requests without API key
            url = f"{self.base_urls['finnhub']}/quote"
            params = {
                'symbol': f"{symbol}.NS",  # NSE symbol format
                'token': 'demo'  # Demo token for testing
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'c' in data and data['c'] > 0:  # 'c' is current price
                    current_price = data.get('c', 0)
                    previous_close = data.get('pc', current_price)
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                    
                    return {
                        'symbol': symbol,
                        'current_price': current_price,
                        'previous_close': previous_close,
                        'change': change,
                        'change_percent': change_percent,
                        'day_high': data.get('h', current_price),
                        'day_low': data.get('l', current_price),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error fetching from Finnhub: {e}")
        return None

    def fetch_from_marketstack(self, symbol):
        """Fetch data from Marketstack (free tier)"""
        try:
            # Marketstack free tier - no API key needed for demo
            url = f"{self.base_urls['marketstack']}/eod/latest"
            params = {
                'symbols': f"{symbol}.XNSE",  # NSE exchange format
                'access_key': 'demo'  # Demo access
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    stock_data = data['data'][0]
                    current_price = stock_data.get('close', 0)
                    previous_close = stock_data.get('open', current_price)
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                    
                    return {
                        'symbol': symbol,
                        'current_price': current_price,
                        'previous_close': previous_close,
                        'change': change,
                        'change_percent': change_percent,
                        'day_high': stock_data.get('high', current_price),
                        'day_low': stock_data.get('low', current_price),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error fetching from Marketstack: {e}")
        return None

    def fetch_from_free_apis(self, symbol):
        """Try multiple free APIs in sequence"""
        apis_to_try = [
            ('Yahoo Finance', self.fetch_from_yahoo_finance),
            ('Finnhub', self.fetch_from_finnhub),
            ('Marketstack', self.fetch_from_marketstack)
        ]
        
        for api_name, api_function in apis_to_try:
            try:
                logger.info(f"Trying {api_name} for {symbol}")
                data = api_function(symbol)
                if data and data.get('current_price', 0) > 0:
                    logger.info(f"Successfully got data from {api_name}")
                    data['data_source'] = api_name.lower().replace(' ', '_')
                    return data
            except Exception as e:
                logger.warning(f"{api_name} failed for {symbol}: {e}")
                continue
        
        return None

    def get_mock_index_data(self, index_name):
        """Generate mock data for demonstration purposes"""
        base_prices = {
            'NIFTY 50': 21500,
            'NIFTY BANK': 46500,
            'NIFTY IT': 35000,
            'NIFTY AUTO': 15500,
            'NIFTY PHARMA': 13500,
            'NIFTY FMCG': 18000,
            'NIFTY METAL': 7500,
            'NIFTY ENERGY': 28000
        }
        
        base_price = base_prices.get(index_name, 20000)
        # Add some random variation
        import random
        change_percent = random.uniform(-2, 2)
        current_price = base_price * (1 + change_percent / 100)
        change = current_price - base_price
        
        return {
            'index_name': index_name,
            'current_price': round(current_price, 2),
            'previous_close': base_price,
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'day_high': round(current_price * 1.01, 2),
            'day_low': round(current_price * 0.99, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'mock_data'
        }

# Initialize data fetcher
data_fetcher = NSEDataFetcher()

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/indices')
@cache_response(60)
def get_all_indices():
    """Get data for all NSE indices"""
    try:
        indices_data = []
        
        for index_name, config in NSE_INDICES.items():
            # Try multiple data sources
            index_data = None
            
            # Method 1: Try nsescraper
            try:
                index_data = data_fetcher.fetch_from_nsescraper(config['api_symbol'])
                if index_data is not None and not index_data.empty:
                    latest_data = index_data.iloc[-1]
                    index_info = {
                        'index_name': index_name,
                        'symbol': config['symbol'],
                        'description': config['description'],
                        'current_price': float(latest_data.get('close', 0)),
                        'previous_close': float(latest_data.get('open', 0)),
                        'change': float(latest_data.get('close', 0)) - float(latest_data.get('open', 0)),
                        'change_percent': ((float(latest_data.get('close', 0)) - float(latest_data.get('open', 0))) / float(latest_data.get('open', 1))) * 100,
                        'day_high': float(latest_data.get('high', 0)),
                        'day_low': float(latest_data.get('low', 0)),
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'nsescraper'
                    }
                    indices_data.append(index_info)
                    continue
            except Exception as e:
                logger.warning(f"nsescraper failed for {index_name}: {e}")
            
            # Method 2: Try multiple free APIs
            try:
                api_data = data_fetcher.fetch_from_free_apis(config['symbol'])
                if api_data:
                    index_info = {
                        'index_name': index_name,
                        'symbol': config['symbol'],
                        'description': config['description'],
                        'current_price': api_data['current_price'],
                        'previous_close': api_data['previous_close'],
                        'change': api_data['change'],
                        'change_percent': api_data['change_percent'],
                        'day_high': api_data['day_high'],
                        'day_low': api_data['day_low'],
                        'timestamp': api_data['timestamp'],
                        'data_source': api_data.get('data_source', 'external_api')
                    }
                    indices_data.append(index_info)
                    continue
            except Exception as e:
                logger.warning(f"Free APIs failed for {index_name}: {e}")
            
            # Method 3: Use mock data as fallback
            mock_data = data_fetcher.get_mock_index_data(index_name)
            mock_data['symbol'] = config['symbol']
            mock_data['description'] = config['description']
            mock_data['data_source'] = 'mock'
            indices_data.append(mock_data)
        
        return jsonify({
            'success': True,
            'data': indices_data,
            'timestamp': datetime.now().isoformat(),
            'total_indices': len(indices_data)
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_indices: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/index/<index_name>')
@cache_response(30)
def get_specific_index(index_name):
    """Get data for a specific NSE index"""
    try:
        if index_name.upper() not in NSE_INDICES:
            return jsonify({
                'success': False,
                'error': f'Index {index_name} not found',
                'available_indices': list(NSE_INDICES.keys())
            }), 404
        
        config = NSE_INDICES[index_name.upper()]
        
        # Try to get real data first
        try:
            index_data = data_fetcher.fetch_from_nsescraper(config['api_symbol'])
            if index_data is not None and not index_data.empty:
                latest_data = index_data.iloc[-1]
                return jsonify({
                    'success': True,
                    'data': {
                        'index_name': index_name.upper(),
                        'symbol': config['symbol'],
                        'description': config['description'],
                        'current_price': float(latest_data.get('close', 0)),
                        'previous_close': float(latest_data.get('open', 0)),
                        'change': float(latest_data.get('close', 0)) - float(latest_data.get('open', 0)),
                        'change_percent': ((float(latest_data.get('close', 0)) - float(latest_data.get('open', 0))) / float(latest_data.get('open', 1))) * 100,
                        'day_high': float(latest_data.get('high', 0)),
                        'day_low': float(latest_data.get('low', 0)),
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'nsescraper'
                    }
                })
        except Exception as e:
            logger.warning(f"Real data fetch failed: {e}")
        
        # Fallback to mock data
        mock_data = data_fetcher.get_mock_index_data(index_name.upper())
        mock_data['symbol'] = config['symbol']
        mock_data['description'] = config['description']
        mock_data['data_source'] = 'mock'
        
        return jsonify({
            'success': True,
            'data': mock_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_specific_index: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trending')
@cache_response(120)
def get_trending_stocks():
    """Get trending stocks data"""
    try:
        trending_data = data_fetcher.fetch_nse_trending()
        return jsonify({
            'success': True,
            'data': trending_data,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'mixed_sources_with_fallback'
        })
            
    except Exception as e:
        logger.error(f"Error in get_trending_stocks: {e}")
        # Even on error, return fallback data
        fallback_data = data_fetcher.generate_trending_fallback()
        return jsonify({
            'success': True,
            'data': fallback_data,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'fallback',
            'note': 'Using fallback data due to API issues'
        })

@app.route('/api/most-active')
@cache_response(120)
def get_most_active():
    """Get most active stocks data"""
    try:
        active_data = data_fetcher.fetch_nse_most_active()
        return jsonify({
            'success': True,
            'data': active_data,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'mixed_sources_with_fallback'
        })
            
    except Exception as e:
        logger.error(f"Error in get_most_active: {e}")
        # Even on error, return fallback data
        fallback_data = data_fetcher.generate_most_active_fallback()
        return jsonify({
            'success': True,
            'data': fallback_data,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'fallback',
            'note': 'Using fallback data due to API issues'
        })

@app.route('/api/status')
def get_api_status():
    """Get API status and health check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'available_indices': list(NSE_INDICES.keys()),
        'cache_size': len(indices_cache),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# Background scheduler for cache cleanup
scheduler = BackgroundScheduler()

def cleanup_cache():
    """Clean up expired cache entries"""
    current_time = time.time()
    expired_keys = [
        key for key, timestamp in cache_timestamp.items()
        if current_time - timestamp > CACHE_DURATION * 2
    ]
    
    for key in expired_keys:
        indices_cache.pop(key, None)
        cache_timestamp.pop(key, None)
    
    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Schedule cache cleanup every 5 minutes
scheduler.add_job(func=cleanup_cache, trigger="interval", minutes=5)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("🚀 NSE Indices Fetcher API is starting...")
    print(f"📊 Available indices: {', '.join(NSE_INDICES.keys())}")
    print(f"🌐 Server running on http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)