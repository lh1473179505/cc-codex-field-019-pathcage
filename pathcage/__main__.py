"""CLI. inspect already works; admit is the piece to implement."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pathcage.parse import PathError, load_path, probe_path, probe_to_dict
from pathcage.policy import PolicyError, load_policy


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pathcage")
    sub = p.add_subparsers(dest="cmd", required=True)
    ins = sub.add_parser("inspect", help="print a lexical probe of a candidate path")
    ins.add_argument("--path", required=True)
    adm = sub.add_parser("admit", help="fail-closed lexical path admission")
    adm.add_argument("--path", required=True)
    adm.add_argument("--policy", required=True)
    adm.add_argument("--report", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        raw = load_path(args.path)
        probe = probe_path(raw)
    except (PathError, OSError) as exc:
        print(f"failed to read path: {exc}", file=sys.stderr)
        return 2

    if args.cmd == "inspect":
        print(json.dumps(probe_to_dict(probe), ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "admit":
        try:
            policy = load_policy(args.policy)
        except (PolicyError, OSError) as exc:
            print(f"failed to load policy: {exc}", file=sys.stderr)
            return 2
        from pathcage.engine import admit_path
        try:
            report = admit_path(probe, policy)
        except NotImplementedError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"admit failed unexpectedly: {exc}", file=sys.stderr)
            return 2
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        decision = str(report.get("decision", "")).lower()
        if decision == "allow":
            return 0
        if decision == "deny":
            return 1
        print("report is missing a decision of allow or deny", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
