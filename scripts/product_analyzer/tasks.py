"""任务发现与元数据。

- slug 规则、目录创建
- ``metadata.json`` 的读 / 写 / 增量合并
- 扫 ``reports/`` 列出历史任务,用户菜单选恢复目标
- 跑完后的产物校验
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from .config import BOLD, DIM, GREEN, REPORTS_DIR, RESET, YELLOW
from .preflight import detect_host
from .ui import err, log


# ---------- slug + dirs ----------

def slugify(name: str) -> str:
    """ASCII-fold + kebab-case + 40-char cap. Falls back to ``product-<md5>``
    for fully non-ASCII names so a Chinese product still gets a stable
    filesystem-safe slug."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    folded = re.sub(r'[\\/:*?"<>|]', "", folded)
    folded = re.sub(r"\s+", "-", folded.strip())
    folded = re.sub(r"[^a-zA-Z0-9._-]", "", folded).strip("-_.").lower()
    if not folded:
        digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
        return f"product-{digest}"
    if len(folded) > 40:
        cut = folded[:40]
        last_dash = cut.rfind("-")
        folded = cut[:last_dash] if last_dash > 20 else cut
    return folded


def prepare_output_dir(product_name: str) -> Path:
    """Create ``reports/<slug>-YYYY-MM-DD[-N]/screenshots/`` and return the
    new dir's Path. ``-N`` suffix is appended for same-day reruns."""
    today = dt.date.today().isoformat()
    base = REPORTS_DIR / f"{slugify(product_name)}-{today}"
    n = 1
    while True:
        out = base if n == 1 else base.with_name(f"{base.name}-{n}")
        try:
            out.mkdir(parents=True)
            (out / "screenshots").mkdir()
            (out / "downloads").mkdir()
            return out
        except FileExistsError:
            n += 1


# ---------- metadata I/O ----------

def write_metadata_seed(
    out_dir: Path,
    product_name: str,
    url: str,
    download_url: str | None,
    *,
    runtime: str = "host",
    sandbox_image: str | None = None,
    sandbox_local: bool = True,
    android_enabled: bool = False,
) -> dict:
    host_os, host_arch = detect_host()
    meta = {
        "product_name": product_name,
        "url": url,
        "download_url": download_url,
        "host_os": host_os,
        "host_arch": host_arch,
        "runtime": runtime,
        "sandbox": {
            "image": sandbox_image,
            "local": sandbox_local,
            "name": None,
        },
        "android": {
            "enabled": android_enabled,
            "apk_url": None,
            "apk_file": None,
            "package_name": None,
            "mode": None,
        },
        "started_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "finished_at": None,
        "mode": None,
        "last_session_id": None,
        "screenshots": [],
        "warnings": [],
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return meta


def read_metadata(out_dir: Path) -> dict | None:
    p = out_dir / "metadata.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def update_metadata(out_dir: Path, **fields) -> None:
    """Merge ``fields`` into metadata.json. Best-effort, never raises."""
    p = out_dir / "metadata.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except json.JSONDecodeError:
        data = {}
    data.update(fields)
    try:
        p.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except OSError as e:
        err(f"update_metadata: 写 {p} 失败: {e}")


# ---------- listing + resume picker ----------

def list_tasks() -> list[dict]:
    """Scan ``reports/`` and return ``[{dir, meta, status, mtime}, ...]``,
    newest first.

    ``status`` ∈ {finished, in_progress, stale}:
      - finished     — ``finished_at`` set AND ``report.md`` ≥ 200 bytes
      - in_progress  — has metadata + ``last_session_id``, no ``finished_at``
      - stale        — metadata exists but no ``last_session_id``
                       (claude never actually started)
    """
    if not REPORTS_DIR.exists():
        return []
    rows: list[dict] = []
    for entry in sorted(REPORTS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        meta = read_metadata(entry)
        if meta is None:
            continue
        report_md = entry / "report.md"
        if meta.get("finished_at") and report_md.exists() and report_md.stat().st_size > 200:
            status = "finished"
        elif meta.get("last_session_id"):
            status = "in_progress"
        else:
            status = "stale"
        rows.append({
            "dir": entry,
            "meta": meta,
            "status": status,
            "mtime": entry.stat().st_mtime,
        })
    return rows


def pick_resume_target() -> dict | None:
    """Show a menu of past runs; let the user pick one. Returns the chosen
    row, or None if there's nothing to resume / user aborted."""
    rows = list_tasks()
    if not rows:
        err("reports/ 下没有历史任务")
        return None

    print(f"\n{BOLD}已有任务列表(最新在前):{RESET}")
    print(f"{DIM}状态: ✓=已完成, ⏸=未完成可续跑, ⚠=未真正启动过{RESET}")
    glyphs = {
        "finished": (f"{GREEN}✓{RESET}", "已完成"),
        "in_progress": (f"{YELLOW}⏸{RESET}", "未完成"),
        "stale": (f"{DIM}⚠{RESET}", "未启动"),
    }
    for i, row in enumerate(rows, 1):
        meta = row["meta"]
        glyph, _ = glyphs[row["status"]]
        product = meta.get("product_name", "?")
        url = meta.get("url", "")
        sid = meta.get("last_session_id") or "—"
        when = meta.get("started_at", "")[:16].replace("T", " ")
        print(f"  {i:>2}. {glyph} {BOLD}{product}{RESET}  {DIM}{when}  session={sid[:8]}…  {url}{RESET}")
        print(f"      {DIM}{row['dir']}{RESET}")
    print("   q. 退出")

    while True:
        try:
            choice = input("选择编号(或 q 退出): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None
        if choice in ("q", "quit", "exit", ""):
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(rows):
                return rows[idx - 1]
        print("  无效输入,请重试")


# ---------- post-run sanity check ----------

def post_check(out_dir: Path) -> None:
    """Warn (don't fail) about any obviously missing artifacts."""
    report = out_dir / "report.md"
    meta = out_dir / "metadata.json"
    issues: list[str] = []
    if not report.exists() or report.stat().st_size < 200:
        issues.append(f"{report} 缺失或过短")
    if not meta.exists():
        issues.append(f"{meta} 缺失")
    else:
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            if not data.get("finished_at"):
                issues.append("metadata.json 中 finished_at 未补齐")
            if not data.get("mode"):
                issues.append("metadata.json 中 mode 未补齐")
        except json.JSONDecodeError as e:
            issues.append(f"metadata.json 解析失败: {e}")
    if issues:
        err("产物校验发现问题:")
        for x in issues:
            err(f"  - {x}")
    else:
        log(f"产物校验通过: {out_dir}")
