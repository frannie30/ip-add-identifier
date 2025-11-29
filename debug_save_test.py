import requests

BASE='http://127.0.0.1:5000'
s = requests.Session()

def try_register_login():
    try:
        r = s.post(BASE+'/register', data={'username':'debuguser','password':'pw'})
        print('register status', r.status_code)
    except Exception as e:
        print('register error', e)
    r = s.post(BASE+'/login', data={'username':'debuguser','password':'pw'})
    print('login status', r.status_code)
    print('cookies', s.cookies.get_dict())

def save_payload():
    payload={'addresses':{'ipv4':'1.2.3.4'}, 'geolocation':{'city':'TestCity'}, 'timestamp':'2025-01-01T00:00:00'}
    rs = s.post(BASE+'/api/save_entry', json=payload)
    print('save status', rs.status_code, rs.text)

def list_and_fetch():
    r = s.get(BASE+'/api/saved_entries')
    print('list status', r.status_code, r.text[:400])
    if r.ok:
        entries = r.json().get('entries', [])
        if entries:
            eid = entries[0]['id']
            r2 = s.get(BASE+f'/api/saved_entries/{eid}')
            print('fetch id', eid, '->', r2.status_code, r2.text[:400])

if __name__ == '__main__':
    try_register_login()
    save_payload()
    list_and_fetch()
