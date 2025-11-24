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
