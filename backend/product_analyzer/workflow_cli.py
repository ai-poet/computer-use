"""Small CLI for agents/hooks to update workflow artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .workflow import (
    append_event,
    mark_step,
    seed_workflow,
    validate_run,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workflow_cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed")
    p_seed.add_argument("out_dir", type=Path)

    p_mark = sub.add_parser("mark-step")
    p_mark.add_argument("out_dir", type=Path)
    p_mark.add_argument("step_id")
    p_mark.add_argument("status")
    p_mark.add_argument("--summary", default=None)

    p_event = sub.add_parser("event")
    p_event.add_argument("out_dir", type=Path)
    p_event.add_argument("--type", default="manual")
    p_event.add_argument("--json", default=None)

    p_check = sub.add_parser("validate")
    p_check.add_argument("out_dir", type=Path)
    p_check.add_argument("--final", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "seed":
        seed_workflow(args.out_dir)
        return 0
    if args.cmd == "mark-step":
        mark_step(args.out_dir, args.step_id, args.status, summary=args.summary)
        return 0
    if args.cmd == "event":
        payload = {"event": args.type}
        if args.json:
            payload.update(json.loads(args.json))
        append_event(args.out_dir, payload)
        return 0
    if args.cmd == "validate":
        issues = validate_run(args.out_dir, final=args.final)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("ok")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
