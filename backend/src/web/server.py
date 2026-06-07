"""Local FastAPI console for product-analyzer runs."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from batch.batch import run_rows, run_single
from settings import app_config
from core.config import REPORTS_DIR
from settings.credentials import delete_credential, list_credentials, store_credential
from analysis.email_otp import resolve_config as resolve_email_config
from core.preflight import check_local_sandbox_prereqs
from core.renderer import render_event
from sandbox.sandbox_runtime import build_sandbox_context
from core.tasks import list_tasks, prepare_output_dir, read_metadata, write_metadata_seed
from analysis.workflow import load_workflow, workflow_path
from analysis.workflow import seed_workflow


class CreateRunRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1)
    download_url: str | None = None
    sandbox_image: str = "linux"
    android: bool = True
    email_registration: bool | None = None
    email_overrides: dict[str, str] | None = None


class CreateBatchRunRow(BaseModel):
    product_name: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1)
    download_url: str | None = None
    category: str | None = None


class CreateBatchRunsRequest(BaseModel):
    rows: list[CreateBatchRunRow] = Field(min_length=1, max_length=200)
    max_workers: int = Field(default=2, ge=1, le=20)
    queue_name: str | None = None
    sandbox_image: str = "linux"
    android: bool = True
    email_registration: bool | None = None
    email_overrides: dict[str, str] | None = None


class SettingsUpdateRequest(BaseModel):
    # 非敏感字段
    provider: str | None = None
    mailosaur_server_id: str | None = None
    mailosaur_server_domain: str | None = None
    imap_host: str | None = None
    imap_port: str | None = None
    imap_username: str | None = None
    imap_ssl: str | None = None
    imap_folder: str | None = None
    email_address: str | None = None
    alias_mode: str | None = None
    # 敏感字段(写 keyring;空字符串=清除,缺省=保持不变)
    mailosaur_api_key: str | None = None
    imap_password: str | None = None


class CredentialSubmitRequest(BaseModel):
    request_id: str
    label: str
    fields: dict[str, str]


class APIErrorResponse(BaseModel):
    error: str
    detail: str | None = None


def api_error(status_code: int, message: str, detail: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=APIErrorResponse(error=message, detail=detail).model_dump(),
    )


def _cors_origins() -> list[str]:
    env = os.environ.get("ANALYZER_CORS_ORIGINS", "")
    if env:
        return [o.strip() for o in env.split(",") if o.strip()]
    return [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]


def _resolve_email_registration(
    flag: bool | None, overrides: dict[str, str] | None = None
) -> tuple[bool, str | None, str | None]:
    if flag is False:
        return False, None, "disabled"
    env = app_config.effective_email_env(overrides)
    cfg = resolve_email_config(env)
    if flag is True:
        return cfg.enabled, cfg.selected_provider, cfg.reason
    if cfg.enabled:
        return True, cfg.selected_provider, None
    return False, None, cfg.reason or "not_configured"


app = FastAPI(title="Product Analyzer Console")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_RUN_THREADS: dict[str, threading.Thread] = {}


@app.get("/api/runs")
def list_runs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in list_tasks():
        entry = task["dir"]
        meta = read_metadata(entry) or {}
        wf = _safe_load_workflow(entry)
        steps = wf.get("steps") if isinstance(wf.get("steps"), list) else []
        rows.append(
            {
                "id": _run_id(entry),
                "out_dir": str(entry),
                "product_name": meta.get("product_name") or wf.get("product_name") or entry.name,
                "url": meta.get("url") or wf.get("url"),
                "queue": meta.get("queue"),
                "mode": meta.get("mode"),
                "runtime": meta.get("runtime"),
                "status": _run_status(entry, meta, wf),
                "started_at": meta.get("started_at") or wf.get("started_at"),
                "finished_at": meta.get("finished_at"),
                "current_step": wf.get("current_step"),
                "progress": _workflow_progress(steps),
            }
        )
    return rows


@app.post("/api/runs")
def create_run(req: CreateRunRequest) -> dict[str, Any]:
    ctx = build_sandbox_context(
        req.sandbox_image,
        mode="local",
        android_enabled=req.android,
    )
    email_enabled, email_provider, email_reason = _resolve_email_registration(
        req.email_registration, req.email_overrides
    )
    warnings = check_local_sandbox_prereqs(req.sandbox_image, android_enabled=req.android)
    out_dir = prepare_output_dir(req.product_name)
    meta = write_metadata_seed(
        out_dir,
        req.product_name,
        req.url,
        req.download_url,
        runtime=ctx.runtime,
        sandbox_image=ctx.image,
        sandbox_local=ctx.local,
        sandbox_mode=ctx.mode,
        android_enabled=ctx.android_enabled,
        email_registration_enabled=email_enabled,
        email_registration_provider=email_provider,
    )
    seed_workflow(out_dir)
    run_id = _run_id(out_dir)

    def _worker() -> None:
        run_single(
            {
                "product_name": req.product_name,
                "url": req.url,
                "download_url": req.download_url,
                "out_dir": str(out_dir),
            },
            sandbox_ctx=ctx,
            sandbox_warnings=warnings,
            plain=True,
            email_registration_enabled=email_enabled,
            email_registration_provider=email_provider,
            email_overrides=req.email_overrides,
        )

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    _RUN_THREADS[run_id] = thread
    response_warnings = meta.get("warnings", []) + warnings
    if not email_enabled and email_reason not in (None, "disabled"):
        response_warnings.append(f"email registration unavailable: {email_reason}")
    return {"id": run_id, "state": "starting", "warnings": response_warnings}


@app.post("/api/runs/batch")
def create_batch_runs(req: CreateBatchRunsRequest) -> dict[str, Any]:
    ctx = build_sandbox_context(
        req.sandbox_image,
        mode="local",
        android_enabled=req.android,
    )
    email_enabled, email_provider, email_reason = _resolve_email_registration(
        req.email_registration, req.email_overrides
    )
    warnings = check_local_sandbox_prereqs(req.sandbox_image, android_enabled=req.android)
    queue_name = (req.queue_name or "web-import").strip() or "web-import"
    batch_id = f"web-{uuid.uuid4().hex[:8]}"
    rows: list[dict[str, str | None]] = []
    ids: list[str] = []

    for index, item in enumerate(req.rows, start=1):
        category = (item.category or queue_name).strip() or "web-import"
        out_dir = prepare_output_dir(item.product_name, category=category)
        write_metadata_seed(
            out_dir,
            item.product_name,
            item.url,
            item.download_url,
            runtime=ctx.runtime,
            sandbox_image=ctx.image,
            sandbox_local=ctx.local,
            sandbox_mode=ctx.mode,
            android_enabled=ctx.android_enabled,
            email_registration_enabled=email_enabled,
            email_registration_provider=email_provider,
            queue_category=category,
            queue_file=queue_name,
        )
        seed_workflow(out_dir)
        ids.append(_run_id(out_dir))
        rows.append(
            {
                "product_name": item.product_name,
                "url": item.url,
                "download_url": item.download_url,
                "queue_category": category,
                "queue_file": queue_name,
                "out_dir": str(out_dir),
            }
        )

    def _worker() -> None:
        run_rows(
            rows,
            max_workers=req.max_workers,
            sandbox_ctx=ctx,
            queue_name=queue_name,
            sandbox_warnings=warnings,
            plain=True,
            email_registration_enabled=email_enabled,
            email_registration_provider=email_provider,
            email_overrides=req.email_overrides,
        )

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    _RUN_THREADS[batch_id] = thread
    response_warnings = list(warnings)
    if not email_enabled and email_reason not in (None, "disabled"):
        response_warnings.append(f"email registration unavailable: {email_reason}")
    return {
        "batch_id": batch_id,
        "ids": ids,
        "state": "starting",
        "warnings": response_warnings,
    }


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    out_dir = _resolve_run(run_id)
    meta = read_metadata(out_dir) or {}
    return {
        "id": _run_id(out_dir),
        "out_dir": str(out_dir),
        "metadata": meta,
        "workflow": _safe_load_workflow(out_dir),
    }


@app.get("/api/runs/{run_id}/steps/{step_file}", response_class=PlainTextResponse)
def get_step(run_id: str, step_file: str) -> str:
    out_dir = _resolve_run(run_id)
    path = out_dir / "steps" / step_file
    if not _inside(path, out_dir / "steps") or not path.is_file():
        raise api_error(404, "step not found", f"{step_file} not found in steps/")
    return path.read_text(encoding="utf-8")


@app.get("/api/runs/{run_id}/report", response_class=PlainTextResponse)
def get_report(run_id: str) -> str:
    out_dir = _resolve_run(run_id)
    path = out_dir / "report.md"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


@app.get("/api/runs/{run_id}/screenshots")
def list_screenshots(run_id: str) -> list[str]:
    out_dir = _resolve_run(run_id)
    ss_dir = out_dir / "screenshots"
    if not ss_dir.is_dir():
        return []
    return sorted(
        p.name for p in ss_dir.iterdir() if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")
    )


@app.get("/api/runs/{run_id}/screenshots/{name}")
def get_screenshot(run_id: str, name: str) -> FileResponse:
    out_dir = _resolve_run(run_id)
    path = out_dir / "screenshots" / name
    if not _inside(path, out_dir / "screenshots") or not path.is_file():
        raise api_error(404, "screenshot not found", f"{name} not found in screenshots/")
    return FileResponse(path)


@app.post("/api/runs/{run_id}/credentials")
def submit_credential(run_id: str, req: CredentialSubmitRequest) -> dict[str, Any]:
    out_dir = _resolve_run(run_id)
    meta = read_metadata(out_dir) or {}
    ref = store_credential(
        req.label,
        req.fields,
        source_run=run_id,
        product=str(meta.get("product_name") or out_dir.name),
    )
    wf = _safe_load_workflow(out_dir)
    requests = wf.setdefault("credential_requests", [])
    for item in requests:
        if isinstance(item, dict) and item.get("id") == req.request_id:
            item["status"] = "submitted"
            item["credential_id"] = ref.credential_id
            break
    workflow_path(out_dir).write_text(
        json.dumps(wf, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {"ok": True, "credential_id": ref.credential_id}


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
    return app_config.settings_status()


@app.put("/api/settings")
def update_settings(req: SettingsUpdateRequest) -> dict[str, Any]:
    data = req.model_dump(exclude_unset=True)
    non_secret = {k: v for k, v in data.items() if k in app_config.FIELD_TO_ENV}
    if non_secret:
        app_config.save_settings(non_secret)
    for field in app_config.SECRET_FIELD_TO_ENV:
        if field in data:
            app_config.set_secret(field, data[field])
    return app_config.settings_status()


@app.get("/api/credentials")
def get_credentials(product: str | None = None) -> list[dict[str, Any]]:
    return list_credentials(product=product)


@app.delete("/api/credentials/{credential_id}")
def remove_credential(credential_id: str) -> dict[str, Any]:
    delete_credential(credential_id)
    return {"ok": True}


@app.websocket("/api/runs/{run_id}/stream")
async def stream_run(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    try:
        out_dir = _resolve_run(run_id)
    except HTTPException:
        await websocket.close(code=1008)
        return
    log_path = out_dir / "run.log"
    events_path = out_dir / "events.jsonl"
    positions = {log_path: 0, events_path: 0}
    render_state: dict[str, Any] = {"session_id": None, "last_action": "starting"}
    seq = 0
    try:
        while True:
            for path in (log_path, events_path):
                if not path.exists():
                    continue
                size = path.stat().st_size
                if size < positions[path]:
                    positions[path] = 0
                if size == positions[path]:
                    continue
                with path.open("r", encoding="utf-8", errors="replace") as fh:
                    fh.seek(positions[path])
                    chunk = fh.read()
                    positions[path] = fh.tell()
                if path == log_path:
                    lines: list[dict[str, Any]] = []
                    for raw in chunk.splitlines():
                        rendered = render_event(raw, render_state)
                        if rendered is None:
                            seq += 1
                            lines.append(
                                {
                                    "id": f"{path.name}:{positions[path]}:{seq}",
                                    "source": path.name,
                                    "kind": "raw",
                                    "text": raw,
                                    "tone": "normal",
                                    "indent": 0,
                                    "raw": raw,
                                }
                            )
                            continue
                        for item in rendered:
                            seq += 1
                            line = item.to_dict()
                            line["id"] = f"{path.name}:{positions[path]}:{seq}"
                            line["source"] = path.name
                            line.setdefault("raw", _truncate_raw(raw))
                            lines.append(line)
                    await websocket.send_json(
                        {"source": path.name, "chunk": chunk, "lines": lines}
                    )
                else:
                    events = []
                    for raw in chunk.splitlines():
                        try:
                            event = json.loads(raw)
                        except json.JSONDecodeError:
                            event = {"event": "raw", "message": raw}
                        events.append(event)
                    await websocket.send_json(
                        {"source": path.name, "chunk": chunk, "events": events}
                    )
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return


def _safe_load_workflow(out_dir: Path) -> dict[str, Any]:
    try:
        return load_workflow(out_dir, create=False)
    except Exception:
        return {}


def _resolve_run(run_id: str) -> Path:
    candidate = (REPORTS_DIR / run_id.replace("~", "/")).resolve()
    if not _inside(candidate, REPORTS_DIR.resolve()) or not candidate.is_dir():
        raise api_error(404, "run not found", f"no run directory for id: {run_id}")
    return candidate


def _run_id(out_dir: Path) -> str:
    try:
        return out_dir.resolve().relative_to(REPORTS_DIR.resolve()).as_posix().replace("/", "~")
    except ValueError:
        return out_dir.name


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _truncate_raw(raw: str, limit: int = 2000) -> str:
    if len(raw) <= limit:
        return raw
    return raw[:limit] + "…"


def _workflow_progress(steps: list[Any]) -> dict[str, int]:
    total = len(steps)
    completed = 0
    for step in steps:
        if isinstance(step, dict) and step.get("status") in {"completed", "skipped"}:
            completed += 1
    percent = round((completed / total) * 100) if total else 0
    return {"completed": completed, "total": total, "percent": percent}


def _run_status(out_dir: Path, meta: dict[str, Any], workflow: dict[str, Any]) -> str:
    report_md = out_dir / "report.md"
    steps = workflow.get("steps") if isinstance(workflow.get("steps"), list) else []
    if meta.get("finished_at") and report_md.exists() and report_md.stat().st_size > 200:
        return "completed"
    if any(isinstance(step, dict) and step.get("status") == "failed" for step in steps):
        return "failed"
    if meta.get("last_session_id") or any(
        isinstance(step, dict) and step.get("status") == "in_progress" for step in steps
    ):
        return "running"
    return "pending"


def main() -> int:
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Product Analyzer Console Server")
    parser.add_argument("--host", default=os.environ.get("ANALYZER_SERVER_HOST", "127.0.0.1"), help="bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("ANALYZER_SERVER_PORT", "8765")), help="bind port (default: 8765)")
    parser.add_argument("--reload", action="store_true", help="enable uvicorn auto-reload")
    args = parser.parse_args()

    uvicorn.run("web.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
