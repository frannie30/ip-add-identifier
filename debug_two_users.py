import requests

BASE='http://127.0.0.1:5000'
s1 = requests.Session()
s2 = requests.Session()

def register(sess, uname):
    try:
        r = sess.post(BASE + '/register', data={'username': uname, 'password': 'pw'})
        print('register', uname, r.status_code)
    except Exception as e:
        print('register error', uname, e)

def login(sess, uname):
    r = sess.post(BASE + '/login', data={'username': uname, 'password': 'pw'})
    print('login', uname, r.status_code)

def save(sess, ip):
    payload={'addresses':{'ipv4': ip}, 'geolocation':{'city':'City-'+ip}, 'timestamp':'2025-01-01T00:00:00'}
    rs = sess.post(BASE + '/api/save_entry', json=payload)
    print('save', ip, rs.status_code, rs.text[:200])

def list_entries(sess, name):
    r = sess.get(BASE + '/api/saved_entries')
    print(name, 'list', r.status_code, r.text[:400])

if __name__ == '__main__':
    register(s1, 'userA')
    register(s2, 'userB')
    login(s1, 'userA')
    save(s1, '10.0.0.1')
    login(s2, 'userB')
    list_entries(s2, 'userB after login')
    list_entries(s1, 'userA after save')
