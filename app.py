#!/usr/bin/env python3
"""
IP Address Information Application
A Flask web application that provides comprehensive IP addressing information
including geolocation, ISP details, and network information.
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import requests
import json
import socket
import subprocess
from datetime import datetime
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Path for local SQLite user database
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database and create users table if missing."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    # Create saved entries table
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT '',
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


def create_user(username, password):
    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, created_at)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def create_saved_entry(user_id, data, title=''):
    created_at = datetime.utcnow().isoformat()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO saved_entries (user_id, title, data, created_at) VALUES (?, ?, ?, ?)",
        (user_id, title, json.dumps(data), created_at)
    )
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return entry_id


def get_saved_entries_for_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at, data FROM saved_entries WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    entries = []
    for r in rows:
        entries.append({
            'id': r['id'],
            'title': r['title'],
            'created_at': r['created_at'],
            'data': json.loads(r['data']) if r['data'] else None
        })
    return entries


def get_saved_entry_for_user(entry_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, data, created_at FROM saved_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        'id': r['id'],
        'title': r['title'],
        'created_at': r['created_at'],
        'data': json.loads(r['data']) if r['data'] else None
    }


def delete_saved_entry_for_user(entry_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM saved_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0

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
    return render_template('index.html', username=session.get('username'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))

        success = create_user(username, password)
        if not success:
            flash('Username already exists. Pick a different one.', 'error')
            return redirect(url_for('register'))

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/saved')
def saved_page():
    # Require login
    if not session.get('user_id'):
        flash('Please log in to view saved entries.', 'error')
        return redirect(url_for('login'))
    return render_template('saved.html', username=session.get('username'))


@app.route('/api/save_entry', methods=['POST'])
def api_save_entry():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400

    title = data.get('title') if isinstance(data, dict) else ''
    # Save the snapshot
    entry_id = create_saved_entry(user_id, data, title or '')
    return jsonify({'success': True, 'id': entry_id}), 201


@app.route('/api/saved_entries')
def api_saved_entries():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    entries = get_saved_entries_for_user(user_id)
    # Remove full data from listing to reduce payload; include short preview
    response = []
    for e in entries:
        preview = None
        if e.get('data') and isinstance(e['data'], dict):
            preview = {
                'ipv4': e['data'].get('addresses', {}).get('ipv4'),
                'city': e['data'].get('geolocation', {}).get('city')
            }
        response.append({
            'id': e['id'],
            'title': e.get('title') or '',
            'created_at': e['created_at'],
            'preview': preview
        })
    return jsonify({'entries': response})


@app.route('/api/saved_entries/<int:entry_id>')
def api_saved_entry(entry_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    entry = get_saved_entry_for_user(entry_id, user_id)
    if not entry:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'entry': entry})


@app.route('/api/saved_entries/<int:entry_id>', methods=['DELETE'])
def api_delete_saved_entry(entry_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    ok = delete_saved_entry_for_user(entry_id, user_id)
    if not ok:
        return jsonify({'error': 'Not found or not authorized'}), 404
    return jsonify({'success': True})

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
    # Ensure database exists
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)