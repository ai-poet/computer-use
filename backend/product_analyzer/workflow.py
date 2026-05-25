"""Workflow state helpers for product-analyzer runs.

The agent still owns product judgment through skill/workflow markdown. This
module only provides deterministic file formats and validation so runs can be
resumed, visualized, and checked by hooks.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any

from .tasks import read_metadata, update_metadata

WORKFLOW_JSON = "workflow.json"
EVENTS_JSONL = "events.jsonl"
STEPS_DIR = "steps"

STEP_DEFINITIONS: list[dict[str, str]] = [
    {
        "id": "linux_sandbox",
        "file": "01_linux_sandbox.md",
        "title": "Linux 沙盒启动",
    },
    {
        "id": "website",
        "file": "02_website.md",
        "title": "官网访问与初步证据",
    },
    {
        "id": "client_discovery",
        "file": "03_client_discovery.md",
        "title": "客户端发现与路由决策",
    },
    {
        "id": "desktop_client",
        "file": "04_desktop_client.md",
        "title": "桌面客户端体验",
    },
    {
        "id": "android_client",
        "file": "05_android_client.md",
        "title": "Android 客户端体验",
    },
    {
        "id": "web_experience",
        "file": "06_web_experience.md",
        "title": "网页体验与补充探索",
    },
    {
        "id": "final_report",
        "file": "07_final_report.md",
        "title": "最终汇总报告",
    },
]

STEP_IDS = {item["id"] for item in STEP_DEFINITIONS}
STEP_FILES = {item["id"]: item["file"] for item in STEP_DEFINITIONS}
SECRET_KEYS = ("password", "passwd", "token", "secret", "credential", "api_key", "apikey")


def workflow_path(out_dir: Path) -> Path:
    return out_dir / WORKFLOW_JSON


def events_path(out_dir: Path) -> Path:
    return out_dir / EVENTS_JSONL


def steps_dir(out_dir: Path) -> Path:
    return out_dir / STEPS_DIR


def step_path(out_dir: Path, step_id: str) -> Path:
    return steps_dir(out_dir) / STEP_FILES[step_id]


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def seed_workflow(out_dir: Path, *, force: bool = False) -> dict[str, Any]:
    """Create ``workflow.json`` and empty step report placeholders."""
    out_dir.mkdir(parents=True, exist_ok=True)
    steps_dir(out_dir).mkdir(parents=True, exist_ok=True)
    path = workflow_path(out_dir)
    if path.exists() and not force:
        return load_workflow(out_dir)

    meta = read_metadata(out_dir) or {}
    data: dict[str, Any] = {
        "version": 1,
        "product_name": meta.get("product_name"),
        "url": meta.get("url"),
        "runtime": meta.get("runtime"),
        "current_step": "linux_sandbox",
        "mode": None,
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "steps": [
            {
                "id": item["id"],
                "title": item["title"],
                "file": f"{STEPS_DIR}/{item['file']}",
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "summary": None,
            }
            for item in STEP_DEFINITIONS
        ],
        "clients": {
            "linux": [],
            "windows": [],
            "android": [],
            "macos": [],
            "ios": [],
            "selected": None,
            "desktop_result": None,
            "android_result": None,
            "web_only_reason": None,
        },
        "credential_requests": [],
        "warnings": [],
    }
    write_workflow(out_dir, data)
    update_metadata(out_dir, workflow={"file": WORKFLOW_JSON, "version": 1})
    return data


def load_workflow(out_dir: Path, *, create: bool = True) -> dict[str, Any]:
    path = workflow_path(out_dir)
    if not path.exists():
        if create:
            return seed_workflow(out_dir)
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        if create:
            return seed_workflow(out_dir, force=True)
        return {}


def write_workflow(out_dir: Path, data: dict[str, Any]) -> None:
    data["updated_at"] = now_iso()
    workflow_path(out_dir).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def mark_step(
    out_dir: Path,
    step_id: str,
    status: str,
    *,
    summary: str | None = None,
) -> dict[str, Any]:
    if step_id not in STEP_IDS:
        raise ValueError(f"unknown step id: {step_id}")
    if status not in {"pending", "in_progress", "completed", "skipped", "failed"}:
        raise ValueError(f"unsupported step status: {status}")
    data = load_workflow(out_dir)
    data["current_step"] = step_id
    stamp = now_iso()
    for step in data.get("steps", []):
        if step.get("id") != step_id:
            continue
        step["status"] = status
        if status == "in_progress" and not step.get("started_at"):
            step["started_at"] = stamp
        if status in {"completed", "skipped", "failed"}:
            if not step.get("started_at"):
                step["started_at"] = stamp
            step["completed_at"] = stamp
        if summary is not None:
            step["summary"] = summary
        break
    write_workflow(out_dir, data)
    return data


def append_event(out_dir: Path, event: dict[str, Any]) -> None:
    safe = sanitize(event)
    safe.setdefault("ts", now_iso())
    events_path(out_dir).parent.mkdir(parents=True, exist_ok=True)
    with events_path(out_dir).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(safe, ensure_ascii=False) + "\n")


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(part in str(key).lower() for part in SECRET_KEYS):
                out[key] = "[REDACTED]"
            else:
                out[key] = sanitize(item)
        return out
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return _redact_text(value)
    return value


def _redact_text(text: str) -> str:
    redacted = text
    patterns = [
        r"(?i)(password|passwd|token|secret|api[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]+",
        r"(?i)(authorization:\s*bearer\s+)[a-z0-9._~+/=-]+",
    ]
    for pattern in patterns:
        redacted = re.sub(pattern, lambda m: m.group(1) + "=[REDACTED]", redacted)
    return redacted


def validate_run(out_dir: Path, *, final: bool = False) -> list[str]:
    issues: list[str] = []
    data = load_workflow(out_dir, create=False)
    if not workflow_path(out_dir).exists():
        issues.append("workflow.json missing")
    if not steps_dir(out_dir).is_dir():
        issues.append("steps/ directory missing")

    steps = data.get("steps") or []
    step_by_id = {step.get("id"): step for step in steps if isinstance(step, dict)}
    required = ["linux_sandbox", "website", "client_discovery"]
    if final:
        required.append("final_report")
    for step_id in required:
        step = step_by_id.get(step_id)
        if not step:
            issues.append(f"workflow step missing: {step_id}")
            continue
        if step.get("status") not in {"completed", "skipped"}:
            issues.append(f"workflow step not finished: {step_id}")
        p = step_path(out_dir, step_id)
        if not p.exists() or p.stat().st_size < 80:
            issues.append(f"step report missing or too short: {STEPS_DIR}/{STEP_FILES[step_id]}")

    if final:
        report = out_dir / "report.md"
        if not report.exists() or report.stat().st_size < 200:
            issues.append("report.md missing or too short")
        meta = read_metadata(out_dir) or {}
        if not meta.get("mode"):
            issues.append("metadata.mode missing")
        if not meta.get("finished_at"):
            issues.append("metadata.finished_at missing")

    return issues


def discover_out_dir_from_env_or_payload(payload: dict[str, Any] | None = None) -> Path | None:
    for key in ("ANALYZER_OUTPUT_DIR", "OUTPUT_DIR"):
        raw = os.environ.get(key)
        if raw:
            return Path(raw).expanduser().resolve()
    payload = payload or {}
    raw = payload.get("out_dir") or payload.get("output_dir")
    if isinstance(raw, str) and raw.strip():
        return Path(raw).expanduser().resolve()
    tool_input = payload.get("tool_input") or payload.get("input") or {}
    if isinstance(tool_input, dict):
        for val in tool_input.values():
            if isinstance(val, str) and "/reports/" in val:
                before, _, after = val.partition("/reports/")
                parts = after.split("/")
                if parts:
                    return Path(before + "/reports/" + parts[0]).expanduser().resolve()
    return None
