"""Thread-safe batch job state for queue visualization and dashboard."""

from __future__ import annotations

import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class JobState(str, Enum):
    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    FINISHING = "finishing"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


STATE_LABEL: dict[JobState, str] = {
    JobState.QUEUED: "排队",
    JobState.STARTING: "启动",
    JobState.RUNNING: "运行",
    JobState.FINISHING: "收尾",
    JobState.PAUSED: "已暂停",
    JobState.DONE: "完成",
    JobState.FAILED: "失败",
    JobState.CANCELLED: "已取消",
}

_RESULT_LINE = re.compile(r"── result:\s*(\S+)")


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text or "")


@dataclass
class BatchJob:
    job_id: int
    product_name: str
    url: str
    download_url: str | None
    state: JobState = JobState.QUEUED
    out_dir: str | None = None
    log_file: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    rc: int | None = None
    error: str | None = None
    claude_rc: int | None = None
    last_action: str = "—"
    session_id: str | None = None
    esc_flag: dict = field(default_factory=lambda: {"esc": False})
    events: deque = field(default_factory=lambda: deque(maxlen=200))
    _supplement_event: threading.Event = field(default_factory=threading.Event, repr=False)
    _supplement_value: str | None = field(default=None, repr=False)
    _supplement_cancelled: bool = field(default=False, repr=False)

    def elapsed_seconds(self) -> float | None:
        if self.started_at is None:
            return None
        end = self.finished_at if self.finished_at is not None else time.time()
        return max(0.0, end - self.started_at)

    def elapsed_display(self) -> str:
        secs = self.elapsed_seconds()
        if secs is None:
            return "—"
        total = int(secs)
        m, s = divmod(total, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


@dataclass(frozen=True)
class BatchJobSnapshot:
    job_id: int
    product_name: str
    url: str
    state: JobState
    state_label: str
    out_dir: str | None
    log_file: str | None
    elapsed_display: str
    last_action: str
    rc: int | None
    error: str | None
    session_id: str | None
    event_lines: list[str]


@dataclass(frozen=True)
class BatchCounts:
    total: int
    queued: int
    starting: int
    running: int
    finishing: int
    paused: int
    done: int
    failed: int
    cancelled: int
    finished: int
    active_slots: int
    max_workers: int


class BatchRunStore:
    """Shared state between asyncio batch workers and the curses dashboard."""

    def __init__(
        self,
        rows: list[dict[str, str | None]],
        *,
        max_workers: int,
        queue_name: str,
        dashboard_active: bool = False,
    ) -> None:
        self.max_workers = max_workers
        self.queue_name = queue_name
        self.dashboard_active = dashboard_active
        self._lock = threading.Lock()
        self._jobs: dict[int, BatchJob] = {}
        self._shutdown = False
        self._cancel_pending = False
        self._done_event = threading.Event()
        self._results: list[dict[str, Any]] | None = None
        self._batch_error: BaseException | None = None

        for index, row in enumerate(rows, start=1):
            self._jobs[index] = BatchJob(
                job_id=index,
                product_name=row["product_name"] or "",
                url=row["url"] or "",
                download_url=row.get("download_url"),
            )

    def job_ids(self) -> list[int]:
        with self._lock:
            return sorted(self._jobs.keys())

    def esc_flag(self, job_id: int) -> dict:
        with self._lock:
            return self._jobs[job_id].esc_flag

    def request_pause(self, job_id: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.esc_flag["esc"] = True

    def mark_queued(self, job_id: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.state in (
                JobState.CANCELLED,
                JobState.STARTING,
                JobState.RUNNING,
                JobState.FINISHING,
                JobState.PAUSED,
                JobState.DONE,
                JobState.FAILED,
            ):
                return
            job.state = JobState.QUEUED
            job.last_action = "—"
            job.started_at = None
            job.out_dir = None
            job.log_file = None

    def mark_starting(self, job_id: int, *, msg: str = "占用并发槽,准备中…") -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.state == JobState.CANCELLED:
                return
            job.state = JobState.STARTING
            job.last_action = msg[:80]
            if job.started_at is None:
                job.started_at = time.time()

    def mark_running(self, job_id: int, *, out_dir: str, log_file: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.state == JobState.CANCELLED:
                return
            job.state = JobState.RUNNING
            job.out_dir = out_dir
            job.log_file = log_file
            job.started_at = time.time()
            job.esc_flag["esc"] = False

    def mark_paused(self, job_id: int, *, session_id: str | None) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.state = JobState.PAUSED
            if session_id:
                job.session_id = session_id

    def mark_running_from_pause(self, job_id: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.state == JobState.PAUSED:
                job.state = JobState.RUNNING
                job.esc_flag["esc"] = False

    def mark_finishing(self, job_id: int, *, msg: str | None = None) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.state in (JobState.RUNNING, JobState.PAUSED):
                job.state = JobState.FINISHING
            elif job.state not in (JobState.FINISHING, JobState.DONE, JobState.FAILED):
                job.state = JobState.FINISHING
            if msg:
                job.last_action = msg[:80]

    def mark_done(self, job_id: int, *, rc: int, error: str | None = None) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.finished_at = time.time()
            job.rc = rc
            job.error = error
            job.state = JobState.DONE if rc == 0 else JobState.FAILED

    def mark_cancelled(self, job_id: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.state = JobState.CANCELLED
            job.finished_at = time.time()
            job.rc = 130

    def update_action(self, job_id: int, action: str | None) -> None:
        if not action:
            return
        plain = _strip_ansi(action)
        with self._lock:
            self._jobs[job_id].last_action = plain[:80]

    def update_session(self, job_id: int, session_id: str | None) -> None:
        if session_id:
            with self._lock:
                self._jobs[job_id].session_id = session_id

    def append_event(self, job_id: int, lines: list[str], state: dict) -> None:
        sid = state.get("session_id")
        with self._lock:
            job = self._jobs[job_id]
            for line in lines:
                if line:
                    job.events.append(line)
            # 列表「最近动作」= 详情事件流最新一行(与 renderer 输出一致)
            for line in reversed(lines):
                plain = _strip_ansi(line).strip()
                if plain:
                    if job.state != JobState.QUEUED:
                        job.last_action = plain[:80]
                    m = _RESULT_LINE.search(plain)
                    if m and job.state == JobState.RUNNING:
                        job.state = JobState.FINISHING
                        job.claude_rc = 0 if m.group(1) == "success" else 1
                    break
            if sid:
                job.session_id = sid

    def is_cancelled(self, job_id: int) -> bool:
        with self._lock:
            return self._jobs[job_id].state == JobState.CANCELLED

    def should_skip_job(self, job_id: int) -> bool:
        with self._lock:
            if self._cancel_pending and self._jobs[job_id].state == JobState.QUEUED:
                self._jobs[job_id].state = JobState.CANCELLED
                self._jobs[job_id].finished_at = time.time()
                self._jobs[job_id].rc = 130
                return True
            return self._jobs[job_id].state == JobState.CANCELLED

    def request_shutdown(self, *, cancel_pending: bool = True) -> None:
        with self._lock:
            self._shutdown = True
            self._cancel_pending = cancel_pending
            if cancel_pending:
                for job in self._jobs.values():
                    if job.state == JobState.QUEUED:
                        job.state = JobState.CANCELLED
                        job.finished_at = time.time()
                        job.rc = 130

    def shutdown_requested(self) -> bool:
        with self._lock:
            return self._shutdown

    def wait_supplement(self, job_id: int) -> str | None:
        """Block until dashboard submits supplement text or cancels."""
        with self._lock:
            job = self._jobs[job_id]
            job._supplement_event.clear()
            job._supplement_value = None
            job._supplement_cancelled = False
        while True:
            with self._lock:
                job = self._jobs[job_id]
                if job._supplement_value is not None:
                    return job._supplement_value
                if job._supplement_cancelled:
                    return None
            if not job._supplement_event.wait(timeout=0.2):
                continue
            with self._lock:
                job = self._jobs[job_id]
                if job._supplement_value is not None:
                    return job._supplement_value
                if job._supplement_cancelled:
                    return None

    def submit_supplement(self, job_id: int, text: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job._supplement_value = text
            job._supplement_event.set()

    def cancel_supplement(self, job_id: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job._supplement_cancelled = True
            job._supplement_event.set()

    def make_supplement_provider(self, job_id: int) -> Callable[[], str | None]:
        def _provider() -> str | None:
            sid = None
            with self._lock:
                sid = self._jobs[job_id].session_id
            self.mark_paused(job_id, session_id=sid)
            return self.wait_supplement(job_id)

        return _provider

    def counts(self) -> BatchCounts:
        with self._lock:
            jobs = list(self._jobs.values())
        c = {s: 0 for s in JobState}
        for job in jobs:
            c[job.state] += 1
        active = (
            c[JobState.STARTING]
            + c[JobState.RUNNING]
            + c[JobState.FINISHING]
            + c[JobState.PAUSED]
        )
        finished = c[JobState.DONE] + c[JobState.FAILED] + c[JobState.CANCELLED]
        return BatchCounts(
            total=len(jobs),
            queued=c[JobState.QUEUED],
            starting=c[JobState.STARTING],
            running=c[JobState.RUNNING],
            finishing=c[JobState.FINISHING],
            paused=c[JobState.PAUSED],
            done=c[JobState.DONE],
            failed=c[JobState.FAILED],
            cancelled=c[JobState.CANCELLED],
            finished=finished,
            active_slots=active,
            max_workers=self.max_workers,
        )

    def snapshot(self) -> list[BatchJobSnapshot]:
        with self._lock:
            jobs = [self._jobs[jid] for jid in sorted(self._jobs.keys())]
            return [
                BatchJobSnapshot(
                    job_id=j.job_id,
                    product_name=j.product_name,
                    url=j.url,
                    state=j.state,
                    state_label=STATE_LABEL[j.state],
                    out_dir=j.out_dir,
                    log_file=j.log_file,
                    elapsed_display=j.elapsed_display(),
                    last_action=j.last_action,
                    rc=j.rc,
                    error=j.error,
                    session_id=j.session_id,
                    event_lines=list(j.events),
                )
                for j in jobs
            ]

    def set_batch_complete(
        self, results: list[dict[str, Any]], error: BaseException | None = None
    ) -> None:
        self._results = results
        self._batch_error = error
        self._done_event.set()

    def wait_until_done(self, timeout: float | None = None) -> bool:
        return self._done_event.wait(timeout=timeout)

    def to_batch_result(self) -> Any:
        from .batch import BatchResult

        if self._results is None:
            raise RuntimeError("batch not finished")
        return BatchResult(total=len(self._results), results=self._results)

    def write_status_json(self, path: Path) -> None:
        import json

        p = path
        data = {
            "queue": self.queue_name,
            "max_workers": self.max_workers,
            "counts": self.counts().__dict__,
            "jobs": [
                {
                    "job_id": s.job_id,
                    "product_name": s.product_name,
                    "state": s.state.value,
                    "out_dir": s.out_dir,
                    "rc": s.rc,
                    "error": s.error,
                }
                for s in self.snapshot()
            ],
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
