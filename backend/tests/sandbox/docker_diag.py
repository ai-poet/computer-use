"""Docker-side diagnostics for local Cua sandboxes."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from ._cli import fail, log, warn


def run_cmd(args: list[str], timeout: float = 15) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"command not found: {args[0]}"
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
        return 124, stdout, stderr or f"timed out after {timeout}s"


def docker_ps() -> list[dict[str, Any]]:
    rc, stdout, stderr = run_cmd(["docker", "ps", "--format", "{{json .}}"])
    if rc != 0:
        warn(f"docker ps failed: {stderr or stdout}")
        return []
    rows: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            warn(f"could not parse docker ps row: {line}")
    return rows


def cua_containers() -> list[dict[str, Any]]:
    rows = docker_ps()
    return [
        row
        for row in rows
        if "cua" in (row.get("Image", "") + " " + row.get("Names", "")).lower()
    ]


def print_docker_summary() -> bool:
    rc, stdout, stderr = run_cmd(["docker", "info", "--format", "{{.ServerVersion}}"])
    if rc != 0:
        fail(f"Docker daemon is not available: {stderr or stdout}")
        return False
    log(f"Docker server version: {stdout}")
    containers = cua_containers()
    if not containers:
        log("No running Cua containers detected")
        return True
    log("Running Cua containers:")
    for row in containers:
        print(
            f"  - {row.get('ID')} {row.get('Image')} {row.get('Status')} "
            f"{row.get('Names')} ports={row.get('Ports')}",
            flush=True,
        )
    return True


def dump_cua_diagnostics(log_tail: int) -> None:
    containers = cua_containers()
    if not containers:
        warn("No running Cua containers to diagnose")
        return
    for row in containers:
        cid = row.get("ID") or row.get("Names")
        if not cid:
            continue
        log(f"Diagnostics for container {cid}")
        for cmd in (
            ["docker", "port", cid],
            ["docker", "logs", "--tail", str(log_tail), cid],
            [
                "docker",
                "exec",
                cid,
                "sh",
                "-lc",
                "ps -ef | sed -n '1,25p'",
            ],
        ):
            rc, stdout, stderr = run_cmd(cmd, timeout=20)
            title = " ".join(cmd)
            print(f"\n--- {title} (rc={rc}) ---", flush=True)
            if stdout:
                print(stdout, flush=True)
            if stderr:
                print(stderr, file=sys.stderr, flush=True)
