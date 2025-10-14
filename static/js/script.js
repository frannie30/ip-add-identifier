/**
 * IP Address Information Tool - JavaScript
 * Handles UI interactions and API communication
 */

class IPInfoApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentData = null;
    }

    initializeElements() {
        // Buttons
        this.fetchIpBtn = document.getElementById('fetchIpBtn');
        this.refreshBtn = document.getElementById('refreshBtn');

        // Display elements
        this.loadingEl = document.getElementById('loading');
        this.errorEl = document.getElementById('error');
        this.errorMessageEl = document.getElementById('errorMessage');
        this.ipInfoEl = document.getElementById('ipInfo');
        this.toast = document.getElementById('toast');
        this.toastMessage = document.getElementById('toastMessage');

        // Info display elements
        this.ipv4El = document.getElementById('ipv4');
        this.ipv6El = document.getElementById('ipv6');
        this.cityEl = document.getElementById('city');
        this.regionEl = document.getElementById('region');
        this.countryEl = document.getElementById('country');
        this.countryCodeEl = document.getElementById('countryCode');
        this.postalCodeEl = document.getElementById('postalCode');
        this.timezoneEl = document.getElementById('timezone');
        this.coordinatesEl = document.getElementById('coordinates');
        this.ispEl = document.getElementById('isp');
        this.organizationEl = document.getElementById('organization');
        this.asnEl = document.getElementById('asn');
        this.asDescriptionEl = document.getElementById('asDescription');
        this.hostnameEl = document.getElementById('hostname');
        this.localIpEl = document.getElementById('localIp');
        this.timestampEl = document.getElementById('timestamp');

        // Security indicators
        this.mobileIndicator = document.getElementById('mobileIndicator');
        this.proxyIndicator = document.getElementById('proxyIndicator');
        this.hostingIndicator = document.getElementById('hostingIndicator');
    }

    bindEvents() {
        // Button events
        this.fetchIpBtn.addEventListener('click', () => this.fetchIPInfo());
        this.refreshBtn.addEventListener('click', () => this.refreshData());

        // Copy button events
        document.addEventListener('click', (e) => {
            if (e.target.closest('.copy-btn')) {
                const copyType = e.target.closest('.copy-btn').dataset.copy;
                this.copyToClipboard(copyType);
            }
        });

        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && document.activeElement === this.fetchIpBtn) {
                this.fetchIPInfo();
            }
        });

        // Auto-fetch on page load
        window.addEventListener('load', () => {
            setTimeout(() => this.fetchIPInfo(), 500);
        });
    }

    async fetchIPInfo() {
        this.showLoading();
        this.hideError();
        this.hideIPInfo();
        
        try {
            // Fetch IP information and local information in parallel
            const [ipResponse, localResponse] = await Promise.all([
                fetch('/api/ip_info'),
                fetch('/api/local_info')
            ]);

            if (!ipResponse.ok || !localResponse.ok) {
                throw new Error('Failed to fetch IP information');
            }

            const ipData = await ipResponse.json();
            const localData = await localResponse.json();

            this.currentData = { ...ipData, local: localData };
            this.displayIPInfo(this.currentData);
            this.hideLoading();
            this.showIPInfo();

        } catch (error) {
            console.error('Error fetching IP info:', error);
            this.showError(`Error: ${error.message}`);
            this.hideLoading();
        }
    }

    async refreshData() {
        if (this.currentData) {
            await this.fetchIPInfo();
            this.showToast('Data refreshed successfully!');
        } else {
            await this.fetchIPInfo();
        }
    }

    displayIPInfo(data) {
        // IP Addresses
        this.ipv4El.textContent = data.addresses?.ipv4 || 'Not available';
        this.ipv6El.textContent = data.addresses?.ipv6 || 'Not available';

        // Geolocation
        this.cityEl.textContent = data.geolocation?.city || '-';
        this.regionEl.textContent = data.geolocation?.region || '-';
        this.countryEl.textContent = data.geolocation?.country || '-';
        this.countryCodeEl.textContent = data.geolocation?.country_code || '-';
        this.postalCodeEl.textContent = data.geolocation?.postal_code || '-';
        this.timezoneEl.textContent = data.geolocation?.timezone || '-';

        // Coordinates
        if (data.geolocation?.latitude && data.geolocation?.longitude) {
            this.coordinatesEl.textContent = `${data.geolocation.latitude}, ${data.geolocation.longitude}`;
        } else {
            this.coordinatesEl.textContent = '-';
        }

        // Network Information
        this.ispEl.textContent = data.network?.isp || '-';
        this.organizationEl.textContent = data.network?.organization || '-';
        this.asnEl.textContent = data.network?.as_number || '-';
        this.asDescriptionEl.textContent = data.network?.as_description || '-';

        // Security Indicators
        this.updateSecurityIndicator(this.mobileIndicator, data.security?.is_mobile);
        this.updateSecurityIndicator(this.proxyIndicator, data.security?.is_proxy);
        this.updateSecurityIndicator(this.hostingIndicator, data.security?.is_hosting);

        // Local Information
        this.hostnameEl.textContent = data.local?.hostname || '-';
        this.localIpEl.textContent = data.local?.local_ips?.[0] || '-';

        // Timestamp
        if (data.timestamp) {
            const date = new Date(data.timestamp);
            this.timestampEl.textContent = date.toLocaleString();
        } else {
            this.timestampEl.textContent = '-';
        }
    }

    updateSecurityIndicator(element, value) {
        // Reset classes
        element.classList.remove('safe', 'warning', 'danger');
        
        if (value === true) {
            element.classList.add('warning');
        } else if (value === false) {
            element.classList.add('safe');
        } else {
            element.classList.add('safe'); // Default to safe for undefined values
        }
    }



    copyToClipboard(type) {
        let textToCopy = '';
        
        switch(type) {
            case 'ipv4':
                textToCopy = this.ipv4El.textContent;
                break;
            case 'ipv6':
                textToCopy = this.ipv6El.textContent;
                break;
        }

        if (textToCopy && textToCopy !== 'Not available' && textToCopy !== '-') {
            navigator.clipboard.writeText(textToCopy).then(() => {
                this.showToast(`${type.toUpperCase()} copied to clipboard!`);
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showToast(`${type.toUpperCase()} copied to clipboard!`);
            });
        }
    }

    showLoading() {
        this.loadingEl.classList.remove('hidden');
        this.fetchIpBtn.disabled = true;
        this.refreshBtn.disabled = true;
    }

    hideLoading() {
        this.loadingEl.classList.add('hidden');
        this.fetchIpBtn.disabled = false;
        this.refreshBtn.disabled = false;
    }

    showError(message) {
        this.errorMessageEl.textContent = message;
        this.errorEl.classList.remove('hidden');
        
        // Auto-hide error after 10 seconds
        setTimeout(() => {
            this.hideError();
        }, 10000);
    }

    hideError() {
        this.errorEl.classList.add('hidden');
    }

    showIPInfo() {
        this.ipInfoEl.classList.remove('hidden');
    }

    hideIPInfo() {
        this.ipInfoEl.classList.add('hidden');
    }



    showToast(message) {
        this.toastMessage.textContent = message;
        this.toast.classList.remove('hidden');
        
        setTimeout(() => {
            this.toast.classList.add('hidden');
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.startTime = performance.now();
        this.loadTime = null;
    }

    recordLoadTime() {
        this.loadTime = performance.now() - this.startTime;
        console.log(`Application loaded in ${this.loadTime.toFixed(2)}ms`);
    }

    recordApiCall(startTime, endTime, endpoint) {
        const duration = endTime - startTime;
        console.log(`API call to ${endpoint} took ${duration.toFixed(2)}ms`);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const performanceMonitor = new PerformanceMonitor();
    const app = new IPInfoApp();
    
    // Record load time
    window.addEventListener('load', () => {
        performanceMonitor.recordLoadTime();
    });
    
    // Global error handler
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
    });
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
    });
});

// Service Worker registration for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then((registration) => {
                console.log('ServiceWorker registration successful');
            })
            .catch((err) => {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { IPInfoApp, PerformanceMonitor };
}