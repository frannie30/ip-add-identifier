# IP Address Information Tool

A comprehensive web application that provides detailed IP addressing information for network technicians. This prototype application retrieves and displays public IPv4/IPv6 addresses, geolocation data, ISP information, ASN details, and security analysis.

## Features

### Current Features
- **Public IP Address Detection**: Retrieves both IPv4 and IPv6 addresses
- **Geolocation Information**: City, region, country, postal code, coordinates, and timezone
- **Network Details**: ISP, organization, ASN (Autonomous System Number), and AS description
- **Security Analysis**: Detection of mobile connections, proxy/VPN usage, and hosting providers
- **Local Network Info**: Hostname and local IP addresses
- **Responsive Design**: Modern, mobile-friendly interface
- **Copy to Clipboard**: Easy copying of IP addresses
- **Real-time Updates**: Refresh functionality for current data
- **Error Handling**: Comprehensive error handling and user feedback

### Technical Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **APIs Used**: 
  - ip-api.com (primary geolocation data)
  - ipify.org (IPv4/IPv6 address detection)
  - ipinfo.io (additional data validation)
- **Styling**: Custom CSS with modern design principles
- **Icons**: Font Awesome 6.0

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   cd /path/to/your/workspace
   # Files should be in the project directory
   ```

2. **Set up Python Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Required Dependencies**
   ```bash
   pip install flask requests
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your web browser
   - Navigate to: `http://127.0.0.1:5000`

## Usage

1. **Getting IP Information**
   - Click the "Get IP Information" button
   - The application will automatically fetch your public IP addresses and related data
   - Information is displayed in organized cards

2. **Copying IP Addresses**
   - Click the copy icon next to IPv4 or IPv6 addresses
   - The address will be copied to your clipboard
   - A confirmation toast will appear

3. **Refreshing Data**
   - Click the "Refresh" button to get updated information
   - Useful when your IP address changes (e.g., after reconnecting to internet)

4. **Viewing Project Backlog**
   - Click "View Backlog" to see planned future enhancements
   - The backlog contains items for Project Activity 4

## API Endpoints

The application provides RESTful API endpoints:

- `GET /api/ip_info` - Comprehensive IP information
- `GET /api/local_info` - Local network information
- `GET /api/backlog` - Project backlog items

### Example API Response (`/api/ip_info`):
```json
{
  "timestamp": "2025-10-14T10:30:00",
  "addresses": {
    "ipv4": "192.168.1.100",
    "ipv6": "2001:db8::1"
  },
  "geolocation": {
    "city": "New York",
    "region": "New York",
    "country": "United States",
    "country_code": "US",
    "postal_code": "10001",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  },
  "network": {
    "isp": "Example ISP",
    "organization": "Example Org",
    "as_number": "AS12345",
    "as_description": "AS12345 Example ISP"
  },
  "security": {
    "is_mobile": false,
    "is_proxy": false,
    "is_hosting": false
  }
}
```

## Project Backlog (Future Enhancements)

### High Priority Items
1. **IPv6 Geolocation Support** (3 days)
   - Implement comprehensive IPv6 geolocation lookup and display

2. **API Rate Limiting** (2 days)
   - Implement rate limiting and caching to handle high traffic

### Medium Priority Items
3. **VPN/Proxy Detection** (2 days)
   - Enhanced detection and categorization of VPN, proxy, and Tor connections

4. **Historical IP Tracking** (5 days)
   - Store and display historical IP address changes with timestamps

5. **Interactive Map Display** (3 days)
   - Show IP location on an interactive world map

6. **DNS Information** (2 days)
   - Display DNS server information and reverse DNS lookup

7. **Bulk IP Lookup** (3 days)
   - Allow batch processing of multiple IP addresses

### Low Priority Items
8. **Speed Test Integration** (4 days)
   - Integrate network speed testing capabilities

9. **Multi-Language Support** (4 days)
   - Add support for multiple languages in the UI

10. **Export Functionality** (2 days)
    - Export IP information to JSON, CSV, or PDF formats

## File Structure

```
devasc/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       ├── script.js     # Main JavaScript functionality
│       └── sw.js         # Service Worker for offline support
├── .venv/                # Python virtual environment
└── README.md            # This documentation file
```

## Architecture Notes

### Backend Architecture
- **Flask Framework**: Lightweight web framework for Python
- **Modular Design**: Separated concerns with dedicated classes
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Multiple API Integration**: Fallback mechanisms for reliability

### Frontend Architecture
- **Progressive Web App**: Service Worker for offline functionality
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Modern JavaScript**: ES6+ features with async/await patterns
- **Accessibility**: Semantic HTML and ARIA attributes

### Security Considerations
- **No API Keys Required**: Uses free-tier APIs to avoid key management
- **Client-Side Security**: No sensitive data stored in frontend
- **CORS Handling**: Proper cross-origin request handling
- **Input Validation**: Server-side validation of all inputs

## Testing

### Manual Testing
1. Test on different devices (desktop, tablet, mobile)
2. Test with different network connections (WiFi, mobile data, VPN)
3. Test offline functionality (disconnect internet, refresh page)
4. Test error scenarios (block API requests, simulate network errors)

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Troubleshooting

### Common Issues

1. **"Failed to fetch IP information" Error**
   - Check internet connection
   - Verify firewall settings
   - Try refreshing the page

2. **IPv6 Shows "Not available"**
   - IPv6 might not be enabled on your network
   - Contact your ISP for IPv6 support

3. **Geolocation Data Inaccurate**
   - Geolocation is based on IP address and may not be precise
   - Accuracy varies by ISP and location

4. **Application Won't Start**
   - Verify Python version (3.8+)
   - Check if port 5000 is available
   - Ensure all dependencies are installed

### Performance Optimization
- The application uses multiple APIs in parallel for faster loading
- Caching mechanisms reduce redundant API calls
- Service Worker provides offline functionality
- CSS and JavaScript are optimized for performance

## Contributing

This is a prototype application for the engineering department. Future enhancements should follow the backlog items outlined above.

### Development Guidelines
1. Maintain the modular architecture
2. Add comprehensive error handling
3. Follow responsive design principles
4. Document all new API endpoints
5. Update the backlog with new enhancement ideas

## License

This is a prototype application developed for internal use by the engineering department.

---

**Contact**: Network Engineering Department  
**Version**: 1.0.0  
**Last Updated**: October 2025