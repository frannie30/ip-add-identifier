import time
import requests

BASE = 'http://127.0.0.1:5000'


def wait_for_server(timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(BASE + '/')
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    return False


def register(session, username, password):
    data = {'username': username, 'password': password}
    r = session.post(BASE + '/register', data=data, allow_redirects=True)
    return r.status_code, r.url


def login(session, username, password):
    data = {'username': username, 'password': password}
    r = session.post(BASE + '/login', data=data, allow_redirects=True)
    return r.status_code, r.url


def main():
    if not wait_for_server(15):
        print('Server did not become available.')
        return

    s = requests.Session()
    username = 'smoketest'
    password = 'TestPass123!'

    status, url = register(s, username, password)
    print('Register attempt:', status, url)

    # If user already exists the app redirects back to /register, otherwise to /login
    status, url = login(s, username, password)
    print('Login attempt:', status, url)

    # Check if session cookie present
    print('Cookies after login:', s.cookies.get_dict())

    # Fetch ip info and save it
    r = s.get(BASE + '/api/ip_info')
    if r.ok:
        payload = r.json()
        payload['title'] = 'smoketest snapshot'
        save_resp = s.post(BASE + '/api/save_entry', json=payload)
        print('Save response:', save_resp.status_code, save_resp.text)
        if save_resp.ok:
            try:
                saved = save_resp.json()
                entry_id = saved.get('id')
                if entry_id:
                    r2 = s.get(BASE + f'/api/saved_entries/{entry_id}')
                    print('Fetch saved entry:', r2.status_code)
                    if r2.ok:
                        print('Saved entry data keys:', list(r2.json().get('entry', {}).get('data', {}).keys()))
            except Exception as e:
                print('Error reading save response', e)
    else:
        print('Failed to fetch ip info for save test')


if __name__ == '__main__':
    main()
