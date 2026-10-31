"""scorensic: doctor | demo | audit | report | compare."""
import argparse
import json
import os
import platform
import sys
from pathlib import Path

from . import __version__
from .audit import audit
from .report import card_html, compare, html

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def _write(report, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = report["eval"]["name"]
    for name in (f"{stem}.json", "latest.json"):
        (out_dir / name).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / f"{stem}.html").write_text(html(report), encoding="utf-8")
    return out_dir / f"{stem}.json", out_dir / f"{stem}.html"


def _line(report):
    s = report["summary"]
    checks = ", ".join(f"{k}={v}" for k, v in sorted(s["by_check"].items())) or "none"
    return f"{report['eval']['name']:<22} findings={s['findings']:<3} ({checks})  {s['runtime_s']}s"


def cmd_doctor(_):
    ok = sys.version_info >= (3, 11)
    print(f"scorensic {__version__}")
    print(f"python   {platform.python_version()} {'ok' if ok else 'NEEDS 3.11+'}")
    print(f"platform {platform.platform()}  cpus={os.cpu_count()}")
    print(f"examples {'found at ' + str(EXAMPLES) if EXAMPLES.is_dir() else 'not found (installed without the repo)'}")
    print("network  not required; no API keys used")
    return 0 if ok else 1


def cmd_audit(args):
    report = audit(args.eval_dir, task_filter=args.task, repeats=args.repeats, processes=args.processes)
    jpath, hpath = _write(report, args.out)
    print(_line(report))
    for f in report["findings"]:
        print(f"  [{f['severity']}] {f['check']} task={f['task_id']}: {f['title']}")
    print(f"json: {jpath}\nhtml: {hpath}")
    return 1 if args.fail_on and any(f["severity"] in args.fail_on for f in report["findings"]) else 0


def cmd_demo(args):
    dirs = sorted(p for p in EXAMPLES.iterdir() if (p / "eval.json").is_file()) if EXAMPLES.is_dir() else []
    if not dirs:
        print("error: examples/ not found; run from a clone of the repository", file=sys.stderr)
        return 2
    print("Synthetic demo: deliberately broken toy graders plus a clean control. Not a measurement of any real benchmark.\n")
    for d in dirs:
        report = audit(d)
        _write(report, args.out)
        print(_line(report))
    print(f"\nReports written to {Path(args.out).resolve()} (open the .html files in a browser)")
    return 0


def cmd_report(args):
    report = json.loads(Path(args.json).read_text(encoding="utf-8"))
    out = Path(args.json).with_suffix(".html")
    out.write_text(html(report), encoding="utf-8")
    print(out)
    return 0


def cmd_compare(args):
    base, latest = (json.loads(Path(p).read_text(encoding="utf-8")) for p in (args.baseline, args.latest))
    diff = compare(base, latest)
    print(f"new={len(diff['new'])} resolved={len(diff['resolved'])} unchanged={diff['unchanged']} "
          f"grader_changed={diff['grader_changed']} tasks_changed={diff['tasks_changed']}")
    for f in diff["new"]:
        print(f"  + [{f['severity']}] {f['check']} task={f['task_id']}")
    for f in diff["resolved"]:
        print(f"  - [{f['severity']}] {f['check']} task={f['task_id']}")
    return 1 if diff["new"] else 0


def cmd_check(args):
    from .check import run
    import os
    res = run(args.sheet, args.endpoint, args.model, repeats=args.repeats, api_key=os.environ.get(args.key_env) if args.key_env else None)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(args.sheet).stem
    (out / f"{stem}-card.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / f"{stem}-card.html").write_text(card_html(res), encoding="utf-8")
    mc = res["marking_check"]
    print(f"Marking check: rejected {mc['tricks_caught']}/{mc['tricks_total']} trick answers")
    for m in res["models"]:
        print(f"{m['model']:<28} {m['right']}/{m['total']} right, {m['wrong']} wrong, {m['no_answer']} didn't know, "
              f"{m['consistent']}/{m['total']} consistent, {m['avg_seconds']}s avg")
    print(f"Report card: {out / (stem + '-card.html')}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="scorensic", description="Check that benchmark graders behave correctly.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="check the environment").set_defaults(fn=cmd_doctor)
    d = sub.add_parser("demo", help="audit the bundled synthetic examples")
    d.add_argument("--out", default="results")
    d.set_defaults(fn=cmd_demo)
    a = sub.add_parser("audit", help="audit one eval directory (contains eval.json)")
    a.add_argument("eval_dir")
    a.add_argument("--task", action="append", help="only this task id (repeatable)")
    a.add_argument("--repeats", type=int, help="grader calls per probe per process")
    a.add_argument("--processes", type=int, help="separate grader processes")
    a.add_argument("--out", default="results")
    a.add_argument("--fail-on", nargs="*", choices=["high", "medium", "low"], help="exit 1 if findings at these severities (for CI)")
    a.set_defaults(fn=cmd_audit)
    k = sub.add_parser("check", help="run a sheet of your own questions on one or more models; plain report card")
    k.add_argument("sheet", help="CSV with columns question,right_answer (optional: id,context)")
    k.add_argument("--model", action="append", required=True, help="model name (repeat to compare)")
    k.add_argument("--endpoint", default="http://localhost:11434/v1", help="OpenAI-compatible URL (default: local Ollama)")
    k.add_argument("--key-env", help="name of the environment variable holding an API key (cloud only)")
    k.add_argument("--repeats", type=int, default=2)
    k.add_argument("--out", default="results")
    k.set_defaults(fn=cmd_check)
    r = sub.add_parser("report", help="re-render HTML from a JSON report")
    r.add_argument("json")
    r.set_defaults(fn=cmd_report)
    c = sub.add_parser("compare", help="diff two JSON reports; exit 1 on new findings")
    c.add_argument("baseline")
    c.add_argument("latest")
    c.set_defaults(fn=cmd_compare)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
