"""Curses dashboard for batch queue: list overview + per-job detail."""

from __future__ import annotations

import curses
import time
from enum import Enum

from .ansi_curses import addstr_ansi
from .batch_store import BatchJobSnapshot, BatchRunStore, JobState


class ViewMode(str, Enum):
    LIST = "list"
    DETAIL = "detail"
    HELP = "help"
    QUIT_CONFIRM = "quit_confirm"
    SUPPLEMENT = "supplement"


def run_dashboard(
    store: BatchRunStore,
    *,
    sandbox_label: str,
    refresh_hz: float = 8.0,
) -> None:
    """Block until batch workers finish; runs on main thread."""
    state = _DashboardState(store=store, sandbox_label=sandbox_label)
    try:
        curses.wrapper(state.main)
    except KeyboardInterrupt:
        from .sandbox_ctl import docker_cleanup_sync_quick

        print("\nCtrl+C: 正在停止沙盒容器…", flush=True)
        docker_cleanup_sync_quick()
        store.request_shutdown(cancel_pending=True)


class _DashboardState:
    def __init__(self, store: BatchRunStore, sandbox_label: str) -> None:
        self.store = store
        self.sandbox_label = sandbox_label
        self.view = ViewMode.LIST
        self.cursor = 0
        self.detail_job_id: int | None = None
        self.detail_scroll = 0
        self.detail_follow_tail = True
        self.help_scroll = 0
        self.supplement_buffer = ""
        self.quit_choice = 0
        self._status_msg = ""
        self._status_until = 0.0

    def main(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.keypad(True)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
            curses.init_pair(4, curses.COLOR_CYAN, -1)
            curses.init_pair(5, curses.COLOR_WHITE, -1)

        interval = 1.0 / 8.0
        while not self.store.wait_until_done(timeout=interval):
            self._handle_input(stdscr)
            self._draw(stdscr)
            if self.view == ViewMode.QUIT_CONFIRM and self.quit_choice == 1:
                self.store.request_shutdown(cancel_pending=True)
                break
        self._handle_input(stdscr)
        self._draw(stdscr)
        stdscr.nodelay(False)
        stdscr.refresh()

    def _set_status(self, msg: str) -> None:
        self._status_msg = msg
        self._status_until = time.time() + 4.0

    def _handle_input(self, stdscr: curses.window) -> None:
        while True:
            try:
                key = stdscr.getch()
            except curses.error:
                break
            if key == -1:
                break
            self._on_key(key)

    def _on_key(self, key: int) -> None:
        if self.view == ViewMode.HELP:
            if key in (ord("?"), ord("q"), 27, ord("\n")):
                self.view = (
                    ViewMode.DETAIL if self.detail_job_id else ViewMode.LIST
                )
            elif key == curses.KEY_DOWN:
                self.help_scroll += 1
            elif key == curses.KEY_UP:
                self.help_scroll = max(0, self.help_scroll - 1)
            return

        if self.view == ViewMode.QUIT_CONFIRM:
            if key in (ord("y"), ord("Y")):
                self.quit_choice = 1
            elif key in (ord("n"), ord("N"), 27):
                self.view = ViewMode.LIST
                self.quit_choice = 0
            return

        if self.view == ViewMode.SUPPLEMENT:
            if key in (27,):  # Esc: back to detail, keep paused (manual intervention window)
                self.view = ViewMode.DETAIL
                self.supplement_buffer = ""
                self._set_status("已暂停,可另开终端人工干预; Esc 再进补充输入")
                return
            if key in (curses.KEY_ENTER, 10, 13):
                if self.detail_job_id is not None:
                    text = self.supplement_buffer.strip()
                    if text:
                        self.store.submit_supplement(self.detail_job_id, text)
                        self._set_status("已提交补充指令,续跑中…")
                        self.store.mark_running_from_pause(self.detail_job_id)
                    else:
                        self._set_status("补充为空,仍暂停; Esc 返回详情")
                self.view = ViewMode.DETAIL
                self.supplement_buffer = ""
                return
            if key in (curses.KEY_BACKSPACE, 127, 8):
                self.supplement_buffer = self.supplement_buffer[:-1]
                return
            if key in (ord("\\"),):
                self.supplement_buffer += "\n"
                return
            if 32 <= key <= 126:
                self.supplement_buffer += chr(key)
            return

        if key == ord("?"):
            self.view = ViewMode.HELP
            return

        if key == ord("q"):
            self.view = ViewMode.QUIT_CONFIRM
            self.quit_choice = 0
            return

        jobs = self.store.snapshot()
        if not jobs:
            return

        if self.view == ViewMode.LIST:
            self._on_key_list(key, jobs)
        elif self.view == ViewMode.DETAIL:
            self._on_key_detail(key, jobs)

    def _on_key_list(self, key: int, jobs: list[BatchJobSnapshot]) -> None:
        if key in (curses.KEY_UP, ord("k")):
            self.cursor = max(0, self.cursor - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.cursor = min(len(jobs) - 1, self.cursor + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            self.detail_job_id = jobs[self.cursor].job_id
            self.detail_scroll = 0
            self.detail_follow_tail = True
            self.view = ViewMode.DETAIL

    def _on_key_detail(self, key: int, jobs: list[BatchJobSnapshot]) -> None:
        job = self._current_job(jobs)
        if job is None:
            self.view = ViewMode.LIST
            return

        if key == ord("b"):
            self.view = ViewMode.LIST
            return

        if key in (curses.KEY_PPAGE,):
            self.detail_follow_tail = False
            self.detail_scroll = max(0, self.detail_scroll - 5)
        elif key in (curses.KEY_NPAGE,):
            self.detail_follow_tail = False
            self.detail_scroll += 5
        elif key in (curses.KEY_UP, ord("k")):
            self.detail_follow_tail = False
            self.detail_scroll = max(0, self.detail_scroll - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.detail_scroll += 1
        elif key in (ord("g"), curses.KEY_END):
            self.detail_follow_tail = True
        elif key in (ord("G"),):
            self.detail_follow_tail = False
            self.detail_scroll = 0

        if key == 27:  # ESC
            if job.state == JobState.RUNNING:
                self.store.request_pause(job.job_id)
                self._set_status(f"正在暂停 #{job.job_id} …")
            elif job.state == JobState.PAUSED:
                self.view = ViewMode.SUPPLEMENT
                self.supplement_buffer = ""
            else:
                self.view = ViewMode.LIST

        if job.state == JobState.PAUSED and self.view == ViewMode.DETAIL:
            pass

    def _current_job(self, jobs: list[BatchJobSnapshot]) -> BatchJobSnapshot | None:
        if self.detail_job_id is None:
            return None
        for j in jobs:
            if j.job_id == self.detail_job_id:
                return j
        return None

    def _draw(self, stdscr: curses.window) -> None:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        if h < 8 or w < 40:
            stdscr.addstr(0, 0, "终端过小,请放大窗口")
            stdscr.refresh()
            return

        jobs = self.store.snapshot()
        counts = self.store.counts()

        if self.view == ViewMode.HELP:
            self._draw_help(stdscr, h, w)
        elif self.view == ViewMode.QUIT_CONFIRM:
            self._draw_quit_confirm(stdscr, h, w)
        elif self.view == ViewMode.SUPPLEMENT:
            self._draw_detail(stdscr, h, w, jobs)
            self._draw_supplement_bar(stdscr, h, w)
        elif self.view == ViewMode.DETAIL:
            self._draw_detail(stdscr, h, w, jobs)
        else:
            self._draw_list(stdscr, h, w, jobs, counts)

        if time.time() < self._status_until and self._status_msg:
            msg = _trunc(self._status_msg, w - 2)
            try:
                stdscr.addstr(h - 1, 0, msg[: w - 1], curses.A_REVERSE)
            except curses.error:
                pass

        stdscr.refresh()

    def _draw_header(self, stdscr: curses.window, w: int, counts) -> int:
        title = f" Batch — {self.store.queue_name} — {self.sandbox_label} "
        line0 = _center(title, w)
        stdscr.addstr(0, 0, line0[: w - 1], curses.A_BOLD)

        bar_w = max(10, min(30, w - 40))
        done = counts.done + counts.failed + counts.cancelled
        filled = int(bar_w * done / counts.total) if counts.total else 0
        bar = "█" * filled + "░" * (bar_w - filled)
        stats = (
            f"并发 {counts.active_slots}/{counts.max_workers}  "
            f"运行 {counts.running}  启动 {counts.starting}  "
            f"收尾 {counts.finishing}  排队 {counts.queued}  "
            f"完成 {counts.done}  失败 {counts.failed}  "
            f"进度 {bar} {done}/{counts.total}"
        )
        stdscr.addstr(1, 0, _trunc(stats, w - 1))
        return 2

    def _draw_list(
        self,
        stdscr: curses.window,
        h: int,
        w: int,
        jobs: list[BatchJobSnapshot],
        counts,
    ) -> None:
        row = self._draw_header(stdscr, w, counts)
        headers = f"{'#':>3}  {'产品':<18} {'状态':<6} {'耗时':>7}  {'最近动作'}"
        stdscr.addstr(row, 0, _trunc(headers, w - 1), curses.A_UNDERLINE)
        row += 1
        stdscr.addstr(row, 0, "─" * max(0, w - 1))
        row += 1

        list_h = h - row - 2
        if self.cursor >= list_h + max(0, len(jobs) - list_h):
            self.cursor = max(0, len(jobs) - 1)

        start = max(0, self.cursor - list_h + 1)
        visible = jobs[start : start + list_h]

        for i, job in enumerate(visible):
            y = row + i
            if y >= h - 2:
                break
            sel = (start + i) == self.cursor
            attr = curses.A_REVERSE if sel else curses.A_NORMAL
            attr |= _state_color(job.state)
            name = _trunc(job.product_name, 18)
            if job.state == JobState.QUEUED:
                action = "—"
            else:
                action = _trunc(job.last_action, max(10, w - 45))
            line = (
                f"{job.job_id:>3}  {name:<18} {job.state_label:<6} "
                f"{job.elapsed_display:>7}  {action}"
            )
            try:
                stdscr.addstr(y, 0, _trunc(line, w - 1), attr)
            except curses.error:
                pass

        footer = "↑/↓ 移动  Enter 详情  q 退出  ? 帮助"
        try:
            stdscr.addstr(h - 2, 0, _trunc(footer, w - 1), curses.A_DIM)
        except curses.error:
            pass

    def _draw_detail(
        self,
        stdscr: curses.window,
        h: int,
        w: int,
        jobs: list[BatchJobSnapshot],
    ) -> None:
        job = self._current_job(jobs)
        if job is None:
            self.view = ViewMode.LIST
            return

        counts = self.store.counts()
        row = self._draw_header(stdscr, w, counts)
        title = f" #{job.job_id} {job.product_name} — b 返回列表 "
        stdscr.addstr(row, 0, _trunc(title, w - 1), curses.A_BOLD | _state_color(job.state))
        row += 1

        meta = (
            f"状态: {job.state_label} · 耗时 {job.elapsed_display} · "
            f"session {(job.session_id or '—')[:12]}"
        )
        stdscr.addstr(row, 0, _trunc(meta, w - 1))
        row += 1
        if job.out_dir:
            stdscr.addstr(row, 0, _trunc(f"out: {job.out_dir}", w - 1))
            row += 1
        if job.log_file:
            stdscr.addstr(row, 0, _trunc(f"log: {job.log_file}", w - 1))
            row += 1

        stdscr.addstr(row, 0, "─" * max(0, w - 1))
        row += 1

        events = job.event_lines
        view_h = max(1, h - row - 3)
        max_scroll = max(0, len(events) - view_h)
        if self.detail_follow_tail:
            self.detail_scroll = max_scroll
        else:
            self.detail_scroll = min(self.detail_scroll, max_scroll)
            self.detail_scroll = max(0, self.detail_scroll)
            if self.detail_scroll >= max_scroll:
                self.detail_follow_tail = True

        visible = events[self.detail_scroll : self.detail_scroll + view_h]
        for i, line in enumerate(visible):
            try:
                addstr_ansi(stdscr, row + i, 0, line, w - 1)
            except curses.error:
                pass

        follow = "跟随底部" if self.detail_follow_tail else "已暂停跟随"
        if job.state == JobState.RUNNING:
            hint = f"Esc 暂停 · b 返回 · j/k 翻阅 · g 回底部({follow})"
        elif job.state == JobState.FINISHING:
            hint = f"claude 已结束,销毁 sandbox 中 · b 返回 · g 回底部({follow})"
        elif job.state == JobState.PAUSED:
            hint = f"Esc 补充指令 · b 返回 · 可另开终端改 out_dir({follow})"
        else:
            hint = f"b 返回 · j/k 翻阅 · g 回底部({follow})"
        try:
            stdscr.addstr(h - 2, 0, _trunc(hint, w - 1), curses.A_DIM)
        except curses.error:
            pass

    def _draw_supplement_bar(self, stdscr: curses.window, h: int, w: int) -> None:
        curses.curs_set(1)
        jobs = self.store.snapshot()
        job = self._current_job(jobs)
        hint = "Enter 提交续跑 · Esc 返回详情(仍暂停) · \\ 换行"
        if job and job.out_dir:
            hint = f"人工干预: 另开终端编辑 {job.out_dir} · {hint}"
        try:
            stdscr.addstr(h - 2, 0, _trunc(hint, w - 1), curses.A_DIM)
        except curses.error:
            pass
        prompt = self.supplement_buffer.replace("\n", " ⏎ ")
        line = f"补充> {prompt}"
        try:
            stdscr.addstr(h - 1, 0, _trunc(line, w - 1), curses.A_REVERSE)
        except curses.error:
            pass

    def _draw_help(self, stdscr: curses.window, h: int, w: int) -> None:
        lines = [
            "快捷键",
            "",
            "列表视图:",
            "  ↑/↓, j/k    移动光标",
            "  Enter       进入任务详情",
            "  q           退出(确认)",
            "  ?           本帮助",
            "",
            "详情视图:",
            "  Esc         运行中:暂停; 已暂停:输入补充指令; 收尾/完成:返回列表",
            "  b           返回列表(暂停仍占并发槽)",
            "  j/k, PgUp/Dn  翻阅历史(暂停自动滚到底)",
            "  g / End       滚到最新并恢复自动跟随",
            "  G             滚到事件顶部",
            "",
            "补充输入:",
            "  Enter       提交并 --resume 续跑",
            "  Esc         返回详情(任务仍暂停,可人工改 out_dir)",
            "  \\           换行(多行补充)",
            "",
            "人工干预(暂停期间):",
            "  另开终端进入详情里显示的 out 目录",
            "  可手动改 report.md / 调 sandbox_ctl / 看 run.log",
            "  完成后回控制台 Esc → 输入补充指令 → Enter 续跑",
            "",
            "放弃本任务: 列表层 q 退出批量,或补充里 Ctrl+C",
            "",
            "状态说明:",
            "  启动 = 已占并发槽,建目录/起 claude 前",
            "  收尾 = claude 已输出 result,正在销毁 sandbox(仍占并发槽)",
            "说明: 暂停/收尾期间仍占用一个并发槽,避免超额启动 claude。",
        ]
        stdscr.addstr(0, 0, " 帮助 ", curses.A_BOLD)
        view_h = h - 2
        start = min(self.help_scroll, max(0, len(lines) - view_h))
        for i, line in enumerate(lines[start : start + view_h]):
            try:
                stdscr.addstr(1 + i, 0, _trunc(line, w - 1))
            except curses.error:
                pass
        try:
            stdscr.addstr(h - 1, 0, "?/Enter 关闭", curses.A_DIM)
        except curses.error:
            pass

    def _draw_quit_confirm(self, stdscr: curses.window, h: int, w: int) -> None:
        msg = "确认退出? 排队任务将取消,运行中任务等当前结束 (y/n)"
        y = h // 2
        x = max(0, (w - len(msg)) // 2)
        try:
            stdscr.addstr(y, x, msg, curses.A_BOLD)
        except curses.error:
            pass


def _state_color(state: JobState) -> int:
    if state == JobState.RUNNING:
        return curses.color_pair(4)
    if state in (JobState.STARTING, JobState.FINISHING):
        return curses.color_pair(2)
    if state == JobState.QUEUED:
        return curses.color_pair(2)
    if state == JobState.DONE:
        return curses.color_pair(1)
    if state in (JobState.FAILED, JobState.CANCELLED):
        return curses.color_pair(3)
    if state == JobState.PAUSED:
        return curses.color_pair(2) | curses.A_BOLD
    return 0


def _trunc(text: str, width: int) -> str:
    text = text or ""
    if width < 1:
        return ""
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _center(text: str, width: int) -> str:
    text = text.strip()
    if len(text) >= width:
        return text[:width]
    pad = (width - len(text)) // 2
    return " " * pad + text
