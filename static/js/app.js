// NSE Indices Dashboard JavaScript
class NSEDashboard {
    constructor() {
        this.apiBaseUrl = '/api';
        this.refreshInterval = 60000; // 1 minute
        this.refreshTimer = null;
        this.isLoading = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
        this.updateMarketStatus();
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.loadInitialData());
        }

        // Tab buttons
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('apiModal');
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.refreshData();
            }
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    async loadInitialData() {
        this.showLoading();
        
        try {
            await Promise.all([
                this.loadIndicesData(),
                this.loadTrendingData(),
                this.loadMostActiveData()
            ]);
            
            this.hideLoading();
            this.showSuccess('Data loaded successfully!');
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to load data. Please try again.', error.message);
        }
    }

    async refreshData() {
        if (this.isLoading) return;
        
        const refreshBtn = document.getElementById('refreshBtn');
        const originalText = refreshBtn.innerHTML;
        
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        refreshBtn.disabled = true;
        
        try {
            await this.loadIndicesData();
            this.updateLastRefreshTime();
            this.showSuccess('Data refreshed successfully!');
        } catch (error) {
            this.showError('Failed to refresh data', error.message);
        } finally {
            refreshBtn.innerHTML = originalText;
            refreshBtn.disabled = false;
        }
    }

    async loadIndicesData() {
        this.isLoading = true;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/indices`);
            const result = await response.json();
            
            if (result.success) {
                this.renderIndicesGrid(result.data);
                this.updateLastRefreshTime();
            } else {
                throw new Error(result.error || 'Failed to load indices data');
            }
        } catch (error) {
            console.error('Error loading indices:', error);
            throw error;
        } finally {
            this.isLoading = false;
        }
    }

    async loadTrendingData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/trending`);
            const result = await response.json();
            
            if (result.success) {
                this.renderTrendingStocks(result.data);
            } else {
                console.warn('Failed to load trending data:', result.error);
                this.renderTrendingStocks(null);
            }
        } catch (error) {
            console.error('Error loading trending data:', error);
            this.renderTrendingStocks(null);
        }
    }

    async loadMostActiveData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/most-active`);
            const result = await response.json();
            
            if (result.success) {
                this.renderMostActiveStocks(result.data);
            } else {
                console.warn('Failed to load most active data:', result.error);
                this.renderMostActiveStocks(null);
            }
        } catch (error) {
            console.error('Error loading most active data:', error);
            this.renderMostActiveStocks(null);
        }
    }

    renderIndicesGrid(indices) {
        const grid = document.getElementById('indicesGrid');
        if (!grid) return;

        if (!indices || indices.length === 0) {
            grid.innerHTML = '<div class="text-center">No indices data available</div>';
            return;
        }

        grid.innerHTML = indices.map(index => this.createIndexCard(index)).join('');
        
        // Add animation to cards
        const cards = grid.querySelectorAll('.index-card');
        cards.forEach((card, i) => {
            card.style.animationDelay = `${i * 0.1}s`;
            card.classList.add('fade-in');
        });
    }

    createIndexCard(index) {
        const isPositive = index.change >= 0;
        const changeClass = isPositive ? 'positive' : 'negative';
        const changeIcon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
        const changePrefix = isPositive ? '+' : '';
        
        return `
            <div class="index-card">
                <div class="index-header">
                    <div>
                        <div class="index-name">${this.escapeHtml(index.index_name)}</div>
                        <div class="index-description">${this.escapeHtml(index.description)}</div>
                    </div>
                    <div class="data-source">${this.escapeHtml(index.data_source || 'live')}</div>
                </div>
                
                <div class="index-price">₹${this.formatNumber(index.current_price)}</div>
                
                <div class="index-change ${changeClass}">
                    <div class="change-value">
                        <i class="fas ${changeIcon}"></i>
                        ${changePrefix}₹${this.formatNumber(Math.abs(index.change))}
                    </div>
                    <div class="change-percent">
                        ${changePrefix}${this.formatNumber(Math.abs(index.change_percent), 2)}%
                    </div>
                </div>
                
                <div class="index-details">
                    <div class="detail-item">
                        <div class="detail-label">Day High</div>
                        <div class="detail-value">₹${this.formatNumber(index.day_high)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Day Low</div>
                        <div class="detail-value">₹${this.formatNumber(index.day_low)}</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTrendingStocks(data) {
        const container = document.getElementById('trendingStocks');
        if (!container) return;

        if (!data || !data.trending_stocks) {
            container.innerHTML = '<div class="text-center">Trending stocks data not available</div>';
            return;
        }

        const gainers = data.trending_stocks.top_gainers || [];
        const losers = data.trending_stocks.top_losers || [];
        
        let html = '';
        
        if (gainers.length > 0) {
            html += '<h4 style="margin-bottom: 15px; color: #28a745;"><i class="fas fa-arrow-up"></i> Top Gainers</h4>';
            html += gainers.slice(0, 5).map(stock => this.createStockItem(stock, true)).join('');
        }
        
        if (losers.length > 0) {
            html += '<h4 style="margin: 25px 0 15px 0; color: #dc3545;"><i class="fas fa-arrow-down"></i> Top Losers</h4>';
            html += losers.slice(0, 5).map(stock => this.createStockItem(stock, false)).join('');
        }

        container.innerHTML = html || '<div class="text-center">No trending data available</div>';
    }

    renderMostActiveStocks(data) {
        const container = document.getElementById('activeStocks');
        if (!container) return;

        if (!data || !Array.isArray(data)) {
            container.innerHTML = '<div class="text-center">Most active stocks data not available</div>';
            return;
        }

        container.innerHTML = data.slice(0, 10).map(stock => this.createStockItem(stock)).join('') || 
                             '<div class="text-center">No active stocks data available</div>';
    }

    createStockItem(stock, isGainer = null) {
        const price = stock.price || stock.current_price || 0;
        const change = stock.percent_change || stock.change_percent || 0;
        const isPositive = change >= 0;
        const changeClass = isPositive ? 'positive' : 'negative';
        const changeIcon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
        const changePrefix = isPositive ? '+' : '';
        
        return `
            <div class="stock-item">
                <div class="stock-name">${this.escapeHtml(stock.company_name || stock.company || stock.ticker_id || 'N/A')}</div>
                <div class="stock-price">₹${this.formatNumber(price)}</div>
                <div class="${changeClass}" style="font-size: 0.9rem; margin-top: 5px;">
                    <i class="fas ${changeIcon}"></i>
                    ${changePrefix}${this.formatNumber(Math.abs(change), 2)}%
                </div>
            </div>
        `;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        const targetPane = tabName === 'trending' ? 'trendingTab' : 'activeTab';
        document.getElementById(targetPane).classList.add('active');
    }

    updateMarketStatus() {
        const now = new Date();
        const hour = now.getHours();
        const minute = now.getMinutes();
        const currentTime = hour * 100 + minute;
        
        const marketOpen = 915; // 9:15 AM
        const marketClose = 1530; // 3:30 PM
        const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
        
        const statusElement = document.getElementById('statusText');
        const statusIndicator = document.querySelector('.status-indicator i');
        
        if (isWeekday && currentTime >= marketOpen && currentTime <= marketClose) {
            statusElement.textContent = 'Market Status: Open';
            statusIndicator.style.color = '#28a745';
        } else {
            statusElement.textContent = 'Market Status: Closed';
            statusIndicator.style.color = '#dc3545';
        }
    }

    updateLastRefreshTime() {
        const lastUpdated = document.getElementById('lastUpdated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date().toLocaleTimeString();
        }
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    showLoading() {
        const spinner = document.getElementById('loadingSpinner');
        const errorMsg = document.getElementById('errorMessage');
        const mainContent = document.querySelector('.main-content');
        
        if (spinner) spinner.style.display = 'block';
        if (errorMsg) errorMsg.style.display = 'none';
        if (mainContent) mainContent.style.opacity = '0.5';
    }

    hideLoading() {
        const spinner = document.getElementById('loadingSpinner');
        const mainContent = document.querySelector('.main-content');
        
        if (spinner) spinner.style.display = 'none';
        if (mainContent) mainContent.style.opacity = '1';
    }

    showError(message, details = '') {
        const errorMsg = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorMsg && errorText) {
            errorText.textContent = `${message}${details ? ': ' + details : ''}`;
            errorMsg.style.display = 'block';
        }
        
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea'};
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined || isNaN(num)) return '0.00';
        return parseFloat(num).toLocaleString('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Modal functions
    showApiDocs() {
        const modal = document.getElementById('apiModal');
        if (modal) {
            modal.style.display = 'block';
        }
    }

    closeModal() {
        const modal = document.getElementById('apiModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showAbout() {
        const aboutContent = `
            <div style="text-align: center; padding: 20px;">
                <h3>NSE Indices Dashboard</h3>
                <p>A real-time dashboard for tracking NSE indices values</p>
                <br>
                <p><strong>Features:</strong></p>
                <ul style="text-align: left; max-width: 300px; margin: 0 auto;">
                    <li>Real-time NSE indices data</li>
                    <li>Trending stocks information</li>
                    <li>Most active stocks</li>
                    <li>Auto-refresh functionality</li>
                    <li>Responsive design</li>
                </ul>
                <br>
                <p style="font-size: 0.9rem; color: #666;">
                    Data sources: Multiple APIs with fallback mechanisms
                </p>
            </div>
        `;
        
        // Create and show modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>About</h2>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    ${aboutContent}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
}

// Global functions for HTML onclick handlers
function showApiDocs() {
    if (window.dashboard) {
        window.dashboard.showApiDocs();
    }
}

function showAbout() {
    if (window.dashboard) {
        window.dashboard.showAbout();
    }
}

function closeModal() {
    if (window.dashboard) {
        window.dashboard.closeModal();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new NSEDashboard();
    
    // Handle page visibility change to pause/resume auto-refresh
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            window.dashboard.stopAutoRefresh();
        } else {
            window.dashboard.startAutoRefresh();
            window.dashboard.refreshData();
        }
    });
});

// Handle beforeunload to cleanup
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.stopAutoRefresh();
    }
});