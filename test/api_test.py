import requests
import os
import socket

from dotenv import load_dotenv
load_dotenv()

# Fix this shit
import urllib3
urllib3.disable_warnings()


addr = os.getenv('INFO_ADDR')
port = os.getenv('INFO_PORT')

base_url = f"https://{addr}:{port}"

s = requests.Session()

# should succeed despite no login
r = s.get(base_url + '/status', verify=False)
print(r.status_code)
print(r.text)
print()

# should fail due to no login
r = s.get(base_url + '/api/s/default/stat/health', verify=False)
print(r.status_code)
print(r.text)
print()

# should login correctly
usr = os.getenv('INFO_USR')
key = os.getenv('INFO_KEY')
r = s.post(base_url + '/api/login', verify=False, json=dict(username=usr, password=key, remeber=True, strict=True))
print(r.status_code)
print(r.text)
print(r.cookies)
print()

# 
r = s.get(base_url + '/api/s/default/stat/health', verify=False)
print(r.status_code)
print(r.text)


def retriveIp():
    ip = None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


print(retriveIp())