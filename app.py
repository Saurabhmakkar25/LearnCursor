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
            'yahoo_finance': 'https://query1.finance.yahoo.com/v8/finance/chart'
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
        """Fetch trending stocks from Indian API"""
        return self.fetch_from_indian_api('trending')

    def fetch_nse_most_active(self):
        """Fetch most active NSE stocks"""
        return self.fetch_from_indian_api('NSE_most_active')

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
            
            # Method 2: Try Yahoo Finance
            try:
                yahoo_data = data_fetcher.fetch_from_yahoo_finance(config['symbol'])
                if yahoo_data:
                    index_info = {
                        'index_name': index_name,
                        'symbol': config['symbol'],
                        'description': config['description'],
                        'current_price': yahoo_data['current_price'],
                        'previous_close': yahoo_data['previous_close'],
                        'change': yahoo_data['change'],
                        'change_percent': yahoo_data['change_percent'],
                        'day_high': yahoo_data['day_high'],
                        'day_low': yahoo_data['day_low'],
                        'timestamp': yahoo_data['timestamp'],
                        'data_source': 'yahoo_finance'
                    }
                    indices_data.append(index_info)
                    continue
            except Exception as e:
                logger.warning(f"Yahoo Finance failed for {index_name}: {e}")
            
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
        if trending_data:
            return jsonify({
                'success': True,
                'data': trending_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to fetch trending data',
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"Error in get_trending_stocks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/most-active')
@cache_response(120)
def get_most_active():
    """Get most active stocks data"""
    try:
        active_data = data_fetcher.fetch_nse_most_active()
        if active_data:
            return jsonify({
                'success': True,
                'data': active_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to fetch most active data',
                'timestamp': datetime.now().isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"Error in get_most_active: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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