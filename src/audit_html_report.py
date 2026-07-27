#!/usr/bin/env python3
"""
audit_html_report.py — generate a self-contained HTML report from audit.py JSON.

Usage:
    python3 audit.py --ingest a.sarif b.sarif --json out.json
    python3 audit_html_report.py out.json report.html

No server, no dependencies, no network. Produces one standalone .html file that
opens in any browser. Design target: a security-triage instrument for an auditor
who reads scanner output all day — dense, legible, score-forward, trustworthy.
Not a marketing dashboard.
"""
import json, sys, html, datetime

def esc(s): return html.escape(str(s))

def score_band(score, mx):
    # relative bands for color, not absolute — highest findings read hottest
    if mx <= 0: return "b0"
    r = score / mx
    if r >= 0.85: return "b4"
    if r >= 0.65: return "b3"
    if r >= 0.45: return "b2"
    if r >= 0.25: return "b1"
    return "b0"

def build(data):
    ranked = data.get("ranked", [])
    tools = data.get("tools", [])
    qw = data.get("quality_weighting", {}) or {}
    sig = data.get("signal_assessment", {}) or {}
    raw = data.get("raw_result_count", 0)
    dedup = data.get("deduplicated_count", len(ranked))
    mx = max((f.get("score", 0) for f in ranked), default=0)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    multi = sum(1 for f in ranked if f.get("n_tools", 1) > 1)

    mode = qw.get("mode", "—")
    mode_note = {
        "MEASURED": "Weights computed from ground truth in this ingest.",
        "PRIOR": "Coarse cross-dataset tool-quality priors applied (not measured on this code).",
        "MIXED": "Per-tool: recognized tools weighted by prior, others flat.",
        "INACTIVE": "Flat — all tool agreements weighted equally.",
    }.get(mode, "")

    rows = []
    for f in ranked:
        band = score_band(f.get("score", 0), mx)
        toolchips = "".join(
            f'<span class="chip">{esc(t)}</span>' for t in f.get("tools", []))
        consensus = ('<span class="consensus">%d tools</span>' % f["n_tools"]
                     if f.get("n_tools", 1) > 1 else '')
        noisy = '<span class="noisy" title="location flagged as noisy">noisy loc</span>' if f.get("noisy_loc") else ''
        rows.append(f'''<tr class="{band}">
          <td class="rank">{esc(f.get("rank",""))}</td>
          <td class="score"><span class="sv">{esc(f.get("score",""))}</span></td>
          <td class="rule">{esc(f.get("ruleId",""))}</td>
          <td class="loc"><span class="file">{esc(f.get("uri",""))}</span><span class="ln">:{esc(f.get("line",""))}</span></td>
          <td class="lvl {esc(f.get("level",""))}">{esc(f.get("level",""))}</td>
          <td class="tools">{toolchips}{consensus}</td>
          <td class="msg">{esc(f.get("message",""))}{noisy}</td>
        </tr>''')

    tools_line = ", ".join(esc(t) for t in tools) or "—"
    conf = esc(sig.get("ranking_confidence", "—"))
    informative = ", ".join(esc(s) for s in sig.get("informative_signals", [])) or "none"

    # INDEPENDENCE CAVEATS. These were previously present in the JSON and dropped
    # on the floor here, so on the Action path — the only path most users see —
    # the caveat informed nobody. Consensus is the tool's headline claim, so a
    # reason to doubt a particular consensus count belongs next to it, not in a
    # file nobody opens. Rendered above the table, not below it.
    warnings = list(data.get("path_warnings") or []) + list(data.get("lineage_warnings") or [])
    engines = data.get("distinct_engines")
    warn_html = ""
    if warnings:
        items = "".join(f"<li>{esc(w)}</li>" for w in warnings)
        _has_path = bool(data.get("path_warnings"))
        _title = ("⚠ Scanner paths do not line up" if _has_path
                  else "⚠ Scanner independence")
        warn_html = (f'<div class="warnbox"><b>{_title}</b>'
                     f'<ul>{items}</ul>'
                     f'<div class="warnfoot">Consensus counts distinct analysis '
                     f'ENGINES, not product names. Agreement between two names for '
                     f'one engine is self-agreement, not corroboration.</div></div>')
    # 0c(a): suffix-linkage disclosure. A merge that needed path reconciliation
    # rests on more inference than one where both tools already agreed, so it is
    # surfaced as its own layer rather than folded into the merge count.
    sl = data.get("suffix_linkage") or {}
    link_html = ""
    if sl.get("active") or sl.get("candidate_pairs_refused_ambiguous"):
        _amb = sl.get("ambiguous_examples") or []
        _ambh = ""
        if sl.get("candidate_pairs_refused_ambiguous"):
            _ambh = ('<div class="warnfoot"><b>'
                     f'{sl["candidate_pairs_refused_ambiguous"]} filename(s) refused '
                     'as ambiguous</b> — the same filename appears at several paths, '
                     'so which pairing is correct cannot be determined and no merge '
                     'was made: ' + esc("; ".join(_amb)) + '</div>')
        _act = ""
        if sl.get("active"):
            _act = (f'<div>Reconciled <b>{sl["paths_reconciled"]}</b> path(s) that two '
                    f'scanners reported relative to different roots. '
                    f'<b>{sl["merges_using_suffix_match"]}</b> of '
                    f'{data.get("cross_tool_merged_findings", 0)} cross-tool merges '
                    f'required this reconciliation.</div>')
        link_html = (
            f'<div class="infobox"><b>Cross-scanner path linkage</b>{_act}'
            f'<div class="warnfoot">Matched on a segment-aligned path suffix that is '
            f'unique on both sides. This is deliberately strict: it is '
            f'high-precision and will MISS real matches, because a wrong merge '
            f'would inflate the agreement count this tool reports, while a missed '
            f'one only costs a merge.</div>{_ambh}</div>')

    # 0h: per-run size-correlation disclosure. Same reasoning as the warnings
    # above — a caveat that only reaches audit_result.json informs nobody on the
    # Action path. DISCLOSURE ONLY: nothing here filters or reweights.
    # When the dispersion gate fails we render the NOT-APPLICABLE reason rather
    # than a coefficient, because a number computed on a near-constant variable
    # hides its own instability.
    sc = data.get("size_correlation") or {}
    size_html = ""
    if sc.get("applicable"):
        _ci = sc.get("bootstrap_ci_95") or [None, None]
        _cis = (f"95% CI {_ci[0]:+.3f} to {_ci[1]:+.3f}"
                if isinstance(_ci[0], (int, float)) else "CI unavailable")
        _cls = "warnbox" if sc.get("size_correlated") else "infobox"
        _ttl = ("⚠ Agreement here is tracking file SIZE"
                if sc.get("size_correlated") else "Size-correlation check")
        _proxy = esc(str(sc.get("size_proxy")))
        _weak = ('<div class="warnfoot">Size was estimated from the highest line '
                 'number any scanner reported, because the SARIF input carried no '
                 'file-length information. That is a LOWER BOUND, so this check is '
                 'weaker than it looks and a quiet result is not clearance.</div>'
                 if sc.get("size_proxy_is_weak") else "")
        size_html = (
            f'<div class="{_cls}"><b>{_ttl}</b>'
            f'<div>Spearman(scanners agreeing, file size) = '
            f'<b>{sc["spearman_rho"]:+.3f}</b> ({esc(_cis)}), '
            f'permutation p = {sc["permutation_p"]:.4f}, '
            f'over {sc["n_units"]} files. Size proxy: {_proxy}.</div>'
            f'<div class="warnfoot">{esc(str(sc.get("interpretation")))}</div>'
            f'{_weak}</div>')
    elif sc:
        size_html = (
            f'<div class="infobox"><b>Size-correlation check: not applicable</b>'
            f'<div>{esc(str(sc.get("reason")))}</div>'
            f'<div class="warnfoot">No coefficient is shown on purpose. This run '
            f'does not have enough variation in how many scanners agree to '
            f'support a rank correlation, and a number computed anyway would be '
            f'unstable in a way the number itself would hide.</div></div>')

    # Show the engine count alongside the scanner count whenever they disagree —
    # that difference IS the finding.
    engines_stat = ""
    if isinstance(engines, int) and engines and engines != len(tools):
        engines_stat = (f'<div class="stat"><div class="n warn">{engines}</div>'
                        f'<div class="l">distinct engines</div></div>')

    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>audit — review-worthiness report</title>
<style>
  :root {{
    --ink:#14171c; --ink2:#3a4048; --line:#d6d3cb; --paper:#faf9f6;
    --panel:#ffffff; --accent:#1f5c4d; --mut:#7c8188;
    --b0:#f4f2ee; --b1:#fbeede; --b2:#f7d9b0; --b3:#eeb27a; --b4:#e08a54;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font:14px/1.5 "SF Mono",ui-monospace,"Cascadia Code",Menlo,Consolas,monospace; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:32px 28px 80px; }}
  header {{ border-bottom:2px solid var(--ink); padding-bottom:18px; margin-bottom:6px; }}
  h1 {{ font-size:15px; letter-spacing:.14em; text-transform:uppercase; margin:0 0 3px;
    font-weight:700; }}
  .sub {{ color:var(--mut); font-size:12px; letter-spacing:.03em; }}
  .stats {{ display:flex; gap:0; margin:22px 0 8px; border:1px solid var(--line);
    background:var(--panel); }}
  .stat {{ flex:1; padding:14px 16px; border-right:1px solid var(--line); }}
  .stat:last-child {{ border-right:none; }}
  .stat .n {{ font-size:26px; font-weight:700; letter-spacing:-.02em; line-height:1; }}
  .stat .l {{ font-size:10.5px; text-transform:uppercase; letter-spacing:.11em;
    color:var(--mut); margin-top:6px; }}
  .stat .n.accent {{ color:var(--accent); }}
  .band {{ display:flex; gap:14px; flex-wrap:wrap; margin:16px 0 4px;
    font-size:11.5px; color:var(--ink2); }}
  .warnbox {{ border:1px solid #b7791f; border-left:4px solid #b7791f;
    background:rgba(183,121,31,.10); padding:12px 14px; margin:14px 0;
    border-radius:4px; font-size:14px; }}
  .warnbox ul {{ margin:8px 0 6px 20px; padding:0; }}
  .warnbox li {{ margin:4px 0; }}
  .warnfoot {{ opacity:.85; font-size:13px; margin-top:6px; }}
  /* 0h size-correlation disclosure when it is NOT an alarm: same shape as
     .warnbox but neutral, so a routine disclosure does not read as a
     warning and a real warning keeps its force. */
  .infobox {{ border:1px solid var(--line); border-left:4px solid var(--ink2);
    background:var(--panel); padding:12px 14px; margin:14px 0;
    border-radius:4px; font-size:14px; }}
  .stat .n.warn {{ color:#b7791f; }}
  .band .pill {{ border:1px solid var(--line); padding:7px 11px; background:var(--panel); }}
  .band .pill b {{ color:var(--ink); font-weight:700; }}
  .modebar {{ margin:14px 0 26px; padding:12px 15px; border-left:3px solid var(--accent);
    background:var(--panel); border-top:1px solid var(--line);
    border-right:1px solid var(--line); border-bottom:1px solid var(--line);
    font-size:12.5px; color:var(--ink2); }}
  .modebar b {{ color:var(--ink); letter-spacing:.05em; }}
  table {{ width:100%; border-collapse:collapse; background:var(--panel);
    border:1px solid var(--line); font-size:12.5px; }}
  thead th {{ text-align:left; font-size:10px; text-transform:uppercase;
    letter-spacing:.1em; color:var(--mut); padding:10px 12px;
    border-bottom:1.5px solid var(--ink); position:sticky; top:0; background:var(--panel); }}
  tbody td {{ padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
  tbody tr.b4 {{ background:var(--b4); }} tbody tr.b3 {{ background:var(--b3); }}
  tbody tr.b2 {{ background:var(--b2); }} tbody tr.b1 {{ background:var(--b1); }}
  tbody tr.b0 {{ background:var(--panel); }}
  tbody tr.b3, tbody tr.b4 {{ color:#2a1a0e; }}
  .rank {{ color:var(--mut); font-variant-numeric:tabular-nums; width:34px; }}
  .score {{ width:52px; }}
  .sv {{ font-weight:700; font-size:14px; font-variant-numeric:tabular-nums; }}
  .rule {{ font-weight:600; white-space:nowrap; }}
  .loc .file {{ color:var(--ink); }} .loc .ln {{ color:var(--mut); }}
  .lvl {{ text-transform:uppercase; font-size:10px; letter-spacing:.08em; width:70px; }}
  .lvl.error {{ color:#a8321e; font-weight:700; }}
  .lvl.warning {{ color:#9a6b12; }} .lvl.note {{ color:var(--mut); }}
  .chip {{ display:inline-block; border:1px solid currentColor; opacity:.75;
    padding:1px 6px; margin:0 4px 2px 0; font-size:10.5px; border-radius:2px; }}
  .consensus {{ display:inline-block; background:var(--accent); color:#fff;
    padding:1px 7px; font-size:10.5px; font-weight:700; border-radius:2px; }}
  .noisy {{ display:inline-block; margin-left:8px; color:var(--mut);
    font-size:10px; font-style:italic; }}
  .msg {{ color:var(--ink2); }}
  footer {{ margin-top:22px; font-size:11px; color:var(--mut); line-height:1.7; }}
  footer b {{ color:var(--ink2); }}
  .controls {{ margin:0 0 10px; font-size:11.5px; color:var(--mut); }}
  .controls input {{ font:inherit; padding:6px 9px; border:1px solid var(--line);
    background:var(--panel); width:260px; }}
  @media (max-width:720px) {{ .stats {{ flex-wrap:wrap; }} .stat {{ min-width:50%; }}
    .msg {{ display:none; }} }}
</style></head><body><div class="wrap">
<header>
  <h1>Review-Worthiness Report</h1>
  <div class="sub">audit.py deterministic re-rank · generated {now}</div>
</header>
<div class="stats">
  <div class="stat"><div class="n">{dedup}</div><div class="l">findings ranked</div></div>
  <div class="stat"><div class="n">{raw}</div><div class="l">raw (pre-dedup)</div></div>
  <div class="stat"><div class="n accent">{multi}</div><div class="l">multi-tool consensus</div></div>
  <div class="stat"><div class="n">{len(tools)}</div><div class="l">scanners</div></div>
  {engines_stat}
</div>
{warn_html}
{link_html}
{size_html}
<div class="band">
  <span class="pill">scanners: <b>{tools_line}</b></span>
  <span class="pill">ranking confidence: <b>{conf}</b></span>
  <span class="pill">informative signals: <b>{informative}</b></span>
</div>
<div class="modebar"><b>Weighting: {esc(mode)}</b> — {esc(mode_note)}</div>
<div class="controls">
  <input id="q" placeholder="filter by file, rule, or message…" oninput="flt()">
</div>
<table id="t"><thead><tr>
  <th>#</th><th>Score</th><th>Rule</th><th>Location</th><th>Level</th><th>Flagged by</th><th>Message</th>
</tr></thead><tbody>
{"".join(rows)}
</tbody></table>
<footer>
  <b>What this is:</b> findings from your scanners, deduplicated and ordered by
  review-worthiness (location + multi-tool agreement + tool quality + severity).
  Higher = look first. <b>What this is not:</b> a ranking by exploitability, and
  not a substitute for human review — it orders what to examine, it doesn't
  decide what's real. Ranking is deterministic: same input, same order.
</footer>
</div>
<script>
function flt(){{
  var q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('#t tbody tr').forEach(function(r){{
    r.style.display = r.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none';
  }});
}}
</script>
</body></html>'''

def main():
    if len(sys.argv) < 3:
        print("usage: python3 audit_html_report.py <audit_json> <output_html>")
        sys.exit(1)
    data = json.load(open(sys.argv[1]))
    open(sys.argv[2], "w").write(build(data))
    print(f"wrote {sys.argv[2]} ({len(data.get('ranked',[]))} findings)")

if __name__ == "__main__":
    main()
