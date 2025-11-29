import pytest

from app import IPInfoCollector, app


def test_ipv4_validator():
    collector = IPInfoCollector()
    # valid IPv4
    assert collector._is_valid_ipv4("192.168.1.1")
    # invalid IPv4
    assert not collector._is_valid_ipv4("999.999.999.999")
    assert not collector._is_valid_ipv4("not.an.ip")


def test_ipv6_validator():
    collector = IPInfoCollector()
    # loopback and a valid full IPv6
    assert collector._is_valid_ipv6("::1")
    assert collector._is_valid_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    # invalid IPv6
    assert not collector._is_valid_ipv6("::gggg")


def test_backlog_endpoint():
    client = app.test_client()
    resp = client.get('/api/backlog')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'backlog_items' in data
    assert data['total_items'] == len(data['backlog_items'])
    # the app defines 10 backlog items
    assert data['total_items'] == 10


def test_index_page():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
    # check that the page includes the app title
    assert b"IP Address Information Tool" in resp.data


def test_save_and_retrieve_snapshot():
    client = app.test_client()

    # create a test user and login via session
    username = 'test_save_user'
    password = 'password123'
    # ensure user exists
    create_ok = None
    try:
        create_ok = app.create_user(username, password)
    except Exception:
        # If create_user isn't accessible through app imported module, skip create
        create_ok = True

    # fetch user id
    user = app.get_user_by_username(username)
    assert user is not None

    with client.session_transaction() as sess:
        sess['user_id'] = user['id']
        sess['username'] = user['username']

    payload = {
        'timestamp': '2025-01-01T00:00:00Z',
        'addresses': {'ipv4': '1.2.3.4', 'ipv6': None},
        'geolocation': {'city': 'TestCity', 'region': 'TestRegion', 'country': 'TestCountry', 'country_code': 'TC', 'postal_code': '0000', 'latitude': 1.2, 'longitude': 3.4, 'timezone': 'UTC'},
        'network': {'isp': 'MyISP', 'organization': 'MyOrg', 'as_number': 'AS123', 'as_description': 'AS 123'},
        'local': {'hostname': 'myhost', 'local_ips': ['192.168.1.5'], 'timestamp': '2025-01-01T00:00:00Z'},
        'additional': {'hostname': 'extra-host'}
    }

    # Save snapshot
    resp = client.post('/api/save_entry', json=payload)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body.get('success') is True
    saved_id = body.get('id')

    # List saved entries
    resp = client.get('/api/saved_entries')
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body.get('entries'), list)
    assert any(e['id'] == saved_id for e in body['entries'])

    # Retrieve the saved entry
    resp = client.get(f'/api/saved_entries/{saved_id}')
    assert resp.status_code == 200
    body = resp.get_json()
    entry = body.get('entry')
    assert entry is not None
    assert isinstance(entry.get('data'), dict)
    assert entry['data']['addresses']['ipv4'] == '1.2.3.4'
    assert entry['data']['geolocation']['city'] == 'TestCity'
