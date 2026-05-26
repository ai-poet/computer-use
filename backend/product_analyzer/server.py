"""Local FastAPI console for product-analyzer runs."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from .batch import run_single
from .config import REPORTS_DIR
from .credentials import store_credential
from .preflight import check_local_sandbox_prereqs
from .sandbox_runtime import build_sandbox_context
from .tasks import list_tasks, read_metadata
from .workflow import load_workflow, workflow_path


class CreateRunRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1)
    download_url: str | None = None
    sandbox_image: str = "linux"
    android: bool = True


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
        rows.append(
            {
                "id": _run_id(entry),
                "out_dir": str(entry),
                "product_name": meta.get("product_name") or wf.get("product_name") or entry.name,
                "url": meta.get("url") or wf.get("url"),
                "queue": meta.get("queue"),
                "mode": meta.get("mode"),
                "runtime": meta.get("runtime"),
                "finished_at": meta.get("finished_at"),
                "current_step": wf.get("current_step"),
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
    warnings = check_local_sandbox_prereqs(req.sandbox_image, android_enabled=req.android)
    holder: dict[str, Any] = {}

    def _worker() -> None:
        result = run_single(
            {
                "product_name": req.product_name,
                "url": req.url,
                "download_url": req.download_url,
            },
            sandbox_ctx=ctx,
            sandbox_warnings=warnings,
            plain=True,
        )
        holder.update(result)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    run_key = f"pending-{id(thread)}"
    _RUN_THREADS[run_key] = thread
    return {"id": run_key, "state": "starting", "warnings": warnings}


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
        raise api_error(404, "report not found", f"{path.name} missing in run directory")
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
    ref = store_credential(req.label, req.fields)
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
                await websocket.send_json({"file": path.name, "chunk": chunk})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
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


def main() -> int:
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Product Analyzer Console Server")
    parser.add_argument("--host", default=os.environ.get("ANALYZER_SERVER_HOST", "127.0.0.1"), help="bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("ANALYZER_SERVER_PORT", "8765")), help="bind port (default: 8765)")
    parser.add_argument("--reload", action="store_true", help="enable uvicorn auto-reload")
    args = parser.parse_args()

    uvicorn.run("product_analyzer.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
