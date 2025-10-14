#!/usr/bin/env python3
"""
IP Address Information Application
A Flask web application that provides comprehensive IP addressing information
including geolocation, ISP details, and network information.
"""

from flask import Flask, render_template, jsonify, request
import requests
import json
import socket
import subprocess
from datetime import datetime

app = Flask(__name__)

class IPInfoCollector:
    """Collects IP information from multiple free APIs"""
    
    def __init__(self):
        self.apis = {
            'ipapi': 'http://ip-api.com/json/',
            'ipify': 'https://api.ipify.org?format=json',
            'ipinfo': 'https://ipinfo.io/json',
            'freegeoip': 'https://freegeoip.app/json/',
        }
    
    def get_public_ipv4(self):
        """Get public IPv4 address using multiple fallback APIs"""
        ipv4_apis = [
            'https://api.ipify.org',
            'https://ipv4.icanhazip.com',
            'https://checkip.amazonaws.com',
            'https://api.my-ip.io/ip'
        ]
        
        for api in ipv4_apis:
            try:
                response = requests.get(api, timeout=3)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if self._is_valid_ipv4(ip):
                        return ip
            except:
                continue
        return None
    
    def get_public_ipv6(self):
        """Get public IPv6 address"""
        try:
            response = requests.get('https://api6.ipify.org', timeout=3)
            if response.status_code == 200:
                ipv6 = response.text.strip()
                if self._is_valid_ipv6(ipv6):
                    return ipv6
        except:
            pass
        return None
    
    def get_detailed_ip_info(self, ip=None):
        """Get comprehensive IP information from ip-api.com (free, no key required)"""
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'ip': data.get('query'),
                        'city': data.get('city'),
                        'region': data.get('regionName'),
                        'region_code': data.get('region'),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'postal_code': data.get('zip'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'as': data.get('as'),
                        'asn': data.get('as', '').split(' ')[0] if data.get('as') else None,
                        'mobile': data.get('mobile', False),
                        'proxy': data.get('proxy', False),
                        'hosting': data.get('hosting', False),
                        'source': 'ip-api.com'
                    }
        except Exception as e:
            print(f"Error getting IP info: {e}")
        return None
    
    def get_ipinfo_data(self):
        """Get information from ipinfo.io (free tier)"""
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def _is_valid_ipv4(self, ip):
        """Validate IPv4 address"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def _is_valid_ipv6(self, ip):
        """Validate IPv6 address"""
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except socket.error:
            return False

# Initialize IP collector
ip_collector = IPInfoCollector()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/ip_info')
def get_ip_info():
    """API endpoint to get comprehensive IP information"""
    try:
        # Get IPv4 and IPv6 addresses
        ipv4 = ip_collector.get_public_ipv4()
        ipv6 = ip_collector.get_public_ipv6()
        
        # Get detailed information for IPv4
        detailed_info = ip_collector.get_detailed_ip_info()
        
        # Get additional info from ipinfo.io
        ipinfo_data = ip_collector.get_ipinfo_data()
        
        # Compile comprehensive response
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'addresses': {
                'ipv4': ipv4,
                'ipv6': ipv6
            },
            'geolocation': {},
            'network': {},
            'security': {},
            'additional': {}
        }
        
        # Add detailed information if available
        if detailed_info:
            response_data['geolocation'] = {
                'city': detailed_info.get('city'),
                'region': detailed_info.get('region'),
                'country': detailed_info.get('country'),
                'country_code': detailed_info.get('country_code'),
                'postal_code': detailed_info.get('postal_code'),
                'latitude': detailed_info.get('latitude'),
                'longitude': detailed_info.get('longitude'),
                'timezone': detailed_info.get('timezone')
            }
            
            response_data['network'] = {
                'isp': detailed_info.get('isp'),
                'organization': detailed_info.get('org'),
                'as_number': detailed_info.get('asn'),
                'as_description': detailed_info.get('as')
            }
            
            response_data['security'] = {
                'is_mobile': detailed_info.get('mobile', False),
                'is_proxy': detailed_info.get('proxy', False),
                'is_hosting': detailed_info.get('hosting', False)
            }
        
        # Add ipinfo.io data if available
        if ipinfo_data:
            if not response_data['geolocation'].get('city'):
                response_data['geolocation']['city'] = ipinfo_data.get('city')
            if not response_data['geolocation'].get('region'):
                response_data['geolocation']['region'] = ipinfo_data.get('region')
            
            response_data['additional']['hostname'] = ipinfo_data.get('hostname')
            if ipinfo_data.get('loc'):
                coords = ipinfo_data['loc'].split(',')
                if len(coords) == 2 and not response_data['geolocation'].get('latitude'):
                    response_data['geolocation']['latitude'] = float(coords[0])
                    response_data['geolocation']['longitude'] = float(coords[1])
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve IP information: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/local_info')
def get_local_info():
    """Get local network information"""
    try:
        # Get local hostname
        hostname = socket.gethostname()
        
        # Get local IP addresses
        local_ips = []
        try:
            # Connect to a remote server to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            local_ips.append(local_ip)
        except:
            pass
        
        return jsonify({
            'hostname': hostname,
            'local_ips': local_ips,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve local information: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/backlog')
def get_backlog():
    """Get project backlog items for future enhancements"""
    backlog_items = [
        {
            'id': 1,
            'title': 'IPv6 Geolocation Support',
            'description': 'Implement comprehensive IPv6 geolocation lookup and display',
            'priority': 'High',
            'category': 'Enhancement',
            'estimated_effort': '3 days'
        },
        {
            'id': 2,
            'title': 'VPN/Proxy Detection',
            'description': 'Enhanced detection and categorization of VPN, proxy, and Tor connections',
            'priority': 'Medium',
            'category': 'Security',
            'estimated_effort': '2 days'
        },
        {
            'id': 3,
            'title': 'Historical IP Tracking',
            'description': 'Store and display historical IP address changes with timestamps',
            'priority': 'Medium',
            'category': 'Feature',
            'estimated_effort': '5 days'
        },
        {
            'id': 4,
            'title': 'Speed Test Integration',
            'description': 'Integrate network speed testing capabilities',
            'priority': 'Low',
            'category': 'Enhancement',
            'estimated_effort': '4 days'
        },
        {
            'id': 5,
            'title': 'Interactive Map Display',
            'description': 'Show IP location on an interactive world map',
            'priority': 'Medium',
            'category': 'UI/UX',
            'estimated_effort': '3 days'
        },
        {
            'id': 6,
            'title': 'API Rate Limiting',
            'description': 'Implement rate limiting and caching to handle high traffic',
            'priority': 'High',
            'category': 'Performance',
            'estimated_effort': '2 days'
        },
        {
            'id': 7,
            'title': 'Multi-Language Support',
            'description': 'Add support for multiple languages in the UI',
            'priority': 'Low',
            'category': 'Internationalization',
            'estimated_effort': '4 days'
        },
        {
            'id': 8,
            'title': 'DNS Information',
            'description': 'Display DNS server information and reverse DNS lookup',
            'priority': 'Medium',
            'category': 'Network',
            'estimated_effort': '2 days'
        },
        {
            'id': 9,
            'title': 'Bulk IP Lookup',
            'description': 'Allow batch processing of multiple IP addresses',
            'priority': 'Medium',
            'category': 'Feature',
            'estimated_effort': '3 days'
        },
        {
            'id': 10,
            'title': 'Export Functionality',
            'description': 'Export IP information to JSON, CSV, or PDF formats',
            'priority': 'Low',
            'category': 'Feature',
            'estimated_effort': '2 days'
        }
    ]
    
    return jsonify({
        'backlog_items': backlog_items,
        'total_items': len(backlog_items),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting IP Information Application...")
    print("Available endpoints:")
    print("  - / : Main application interface")
    print("  - /api/ip_info : Get public IP information")
    print("  - /api/local_info : Get local network information") 
    print("  - /api/backlog : Get project backlog items")
    print("\nAccess the application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)