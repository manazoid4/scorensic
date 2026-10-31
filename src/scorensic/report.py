"""Static HTML report and baseline comparison. No templates, no JavaScript."""
import json
from html import escape


def html(report):
    s = report["summary"]
    rows = []
    for f in report["findings"]:
        ev = escape(json.dumps(f["evidence"], indent=2, ensure_ascii=False))
        rows.append(f"""<section class="f {escape(f['severity'])}">
<h3><span class="sev">{escape(f['severity'])}</span> {escape(f['title'])}</h3>
<p><b>Check:</b> <code>{escape(f['check'])}</code> &middot; <b>Task:</b> <code>{escape(str(f['task_id']))}</code> &middot; <b>Confidence:</b> {escape(f['confidence'])}</p>
<p>{escape(f['explanation'])}</p>
<p><b>Fix:</b> {escape(f['remediation'])}</p>
<p><b>Reproduce:</b> <code>{escape(f['reproduce'])}</code></p>
<details><summary>Evidence</summary><pre>{ev}</pre></details>
</section>""")
    checks = "".join(f"<li><code>{escape(k)}</code>: {v}</li>" for k, v in sorted(s["by_check"].items())) or "<li>No findings.</li>"
    skipped = "".join(f"<li>{escape(x['check'])} / {escape(str(x['task_id']))}: {escape(x['reason'])}</li>" for x in report["skipped"]) or "<li>None.</li>"
    limits = "".join(f"<li>{escape(x)}</li>" for x in report["limitations"])
    e = report["eval"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eval integrity report: {escape(e['name'])}</title>
<style>
body{{font:16px/1.55 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:24px 16px;color:#1f2928}}
code,pre{{font-family:ui-monospace,Consolas,monospace;font-size:.88em}} pre{{white-space:pre-wrap;background:#f4f5f1;padding:12px;border-radius:6px}}
.f{{border:1px solid #d8dbd3;border-left-width:6px;border-radius:8px;padding:4px 16px;margin:14px 0}}
.high{{border-left-color:#b3261e}} .medium{{border-left-color:#c77700}} .low{{border-left-color:#5d6b66}}
.sev{{font:700 .72rem ui-monospace,monospace;text-transform:uppercase;letter-spacing:.06em}}
.meta{{color:#58615f;font-size:.9rem}}
</style></head><body>
<h1>Eval integrity report</h1>
<p class="meta">{escape(e['name'])} &middot; scorensic {escape(report['version'])} &middot; {escape(report['generated_at'])}</p>
<p>{escape(e['description'])}</p>
<h2>Summary</h2>
<p>{s['tasks']} task(s), {s['probes']} probe(s), {s['grader_calls']} grader call(s), {s['findings']} finding(s) in {s['runtime_s']}s.
This is not a score of the benchmark. Each finding below is a specific input on which the grader behaved differently from what the task says it should.</p>
<ul>{checks}</ul>
<h2>Findings</h2>
{''.join(rows) or '<p>No findings. The grader passed every probe. That is evidence about these probes only, not proof the grader is correct.</p>'}
<h2>Skipped checks</h2><ul>{skipped}</ul>
<h2>Limitations</h2><ul>{limits}</ul>
<h2>Provenance</h2><pre>{escape(json.dumps({'eval': e, 'environment': report['environment'], 'config': report['config']}, indent=2))}</pre>
</body></html>
"""


def compare(baseline, latest):
    """Findings are keyed by their stable id (check + task + probe/location)."""
    old = {f["id"]: f for f in baseline["findings"]}
    new = {f["id"]: f for f in latest["findings"]}
    return {
        "new": [new[k] for k in new.keys() - old.keys()],
        "resolved": [old[k] for k in old.keys() - new.keys()],
        "unchanged": len(new.keys() & old.keys()),
        "grader_changed": baseline["eval"]["grader_sha256"] != latest["eval"]["grader_sha256"],
        "tasks_changed": baseline["eval"]["tasks_sha256"] != latest["eval"]["tasks_sha256"],
    }
