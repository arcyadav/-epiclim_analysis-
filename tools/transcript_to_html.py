"""Convert a Claude Code `/export` transcript into a standalone HTML page.

Each user message becomes "Turn N" with the message always visible; the
response below it is a collapsed block (click to expand). A sidebar lists
every turn as a clickable link, and buttons expand or collapse all
responses at once. The page is a single self-contained file (inline CSS
and JS, no external requests).

How the export is parsed:
  - a user message starts with a line beginning with the prompt marker
    (U+276F). Its continuation lines are padded with trailing spaces to the
    terminal width, which is how they are told apart from the response that
    follows (response lines are not padded).
  - everything after the message, up to the next user message, is the
    response. "Recap" lines (U+203B) are dropped: they are status
    summaries the CLI shows when you return to a session, not replies.

Usage (from the repository root):
  python tools/transcript_to_html.py [transcript.md] [transcript.html] [title] [note]

The optional note is shown in a highlighted box above Turn 1 (e.g. to say
that earlier sessions were not saved).
"""
import html
import re
import sys

USER_MARK = "❯"
RECAP_MARK = "※"
TIMING_RE = re.compile(r"^✻ .+ for .+")


def parse(text):
    lines = text.splitlines()
    first_user = next(i for i, l in enumerate(lines) if l.startswith(USER_MARK))
    header = [l.strip() for l in lines[:first_user] if l.strip()]

    turns = []
    i = first_user
    while i < len(lines):
        line = lines[i]
        width = len(line)
        user = [line[len(USER_MARK):].strip()]
        i += 1
        # Continuation lines: padded to the same width with trailing spaces
        while (i < len(lines) and len(lines[i]) == width
               and lines[i] != lines[i].rstrip() and not lines[i].startswith(USER_MARK)):
            user.append(lines[i][2:].rstrip() if lines[i].startswith("  ") else lines[i].rstrip())
            i += 1
        response = []
        while i < len(lines) and not lines[i].startswith(USER_MARK):
            if not lines[i].startswith(RECAP_MARK):
                response.append(lines[i])
            i += 1
        turns.append({"user": "\n".join(user).strip("\n"),
                      "response": clean_response(response)})
    return header, turns


def clean_response(lines):
    # Drop the 2-space indent the CLI puts on continuation lines, and blank
    # lines at either end
    out = [l[2:] if l.startswith("  ") else l for l in lines]
    out = [l.rstrip() for l in out]
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return out


def render_response(lines):
    parts = []
    for line in lines:
        escaped = html.escape(line)
        if line.startswith("● "):
            parts.append(f'<span class="say">{escaped}</span>')
        elif TIMING_RE.match(line):
            parts.append(f'<span class="timing">{escaped}</span>')
        elif line.lstrip().startswith("⎿"):
            parts.append(f'<span class="tool">{escaped}</span>')
        else:
            parts.append(escaped)
    return "\n".join(parts)


def summary_text(user, limit=70):
    flat = " ".join(user.split())
    return flat if len(flat) <= limit else flat[:limit - 1].rstrip() + "…"


def build_html(header, turns, title, note=""):
    toc = "\n".join(
        f'<li><a href="#turn-{n}"><span class="n">{n}</span>'
        f'{html.escape(summary_text(t["user"], 48))}</a></li>'
        for n, t in enumerate(turns, 1))
    articles = "\n".join(
        f'''<article class="turn" id="turn-{n}">
  <h2><a href="#turn-{n}">Turn {n}</a></h2>
  <div class="user"><div class="who">User</div><p>{html.escape(t["user"])}</p></div>
  <details>
    <summary>Response <span class="count">{len(t["response"])} lines</span></summary>
    <pre>{render_response(t["response"])}</pre>
  </details>
</article>''' for n, t in enumerate(turns, 1))
    meta = html.escape(" · ".join(h for h in header if "Claude Code" in h or "·" in h))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  :root {{
    --surface: #fcfcfb; --card: #ffffff; --ink: #0b0b0b; --text: #2b2a27;
    --muted: #6f6d67; --grid: #e1e0d9; --soft: #f3f2ee; --accent: #2a78d6;
    --user: #eef4fc; --user-edge: #2a78d6; --pre: #f7f6f2;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --surface: #161614; --card: #1f1f1c; --ink: #f4f3ef; --text: #dcdad3;
      --muted: #a3a097; --grid: #34332f; --soft: #262622; --accent: #6aa5ee;
      --user: #1c2633; --user-edge: #6aa5ee; --pre: #1a1a18;
    }}
  }}
  :root[data-theme="dark"] {{
    --surface: #161614; --card: #1f1f1c; --ink: #f4f3ef; --text: #dcdad3;
    --muted: #a3a097; --grid: #34332f; --soft: #262622; --accent: #6aa5ee;
    --user: #1c2633; --user-edge: #6aa5ee; --pre: #1a1a18;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{ margin: 0; background: var(--surface); color: var(--text);
    font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  .layout {{ display: grid; grid-template-columns: 280px minmax(0, 1fr); max-width: 1280px; margin: 0 auto; }}
  aside {{ position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 24px 16px;
    border-right: 1px solid var(--grid); }}
  aside h3 {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; margin: 0 0 8px; }}
  aside ol {{ list-style: none; margin: 0; padding: 0; }}
  aside a {{ display: flex; gap: 8px; padding: 5px 8px; border-radius: 6px; color: var(--text);
    text-decoration: none; font-size: 13px; line-height: 1.35; }}
  aside a:hover {{ background: var(--soft); color: var(--ink); }}
  aside .n {{ color: var(--muted); min-width: 22px; font-variant-numeric: tabular-nums; }}
  main {{ padding: 32px 24px 64px; min-width: 0; }}
  header h1 {{ color: var(--ink); font-size: clamp(24px, 4vw, 32px); margin: 0 0 6px; }}
  header p {{ color: var(--muted); margin: 0 0 16px; font-size: 14px; }}
  .note {{ background: var(--card); border: 1px solid var(--grid); border-left: 4px solid #eb6834;
    border-radius: 8px; padding: 12px 16px; margin: 0 0 16px; font-size: 14px; }}
  .controls {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }}
  button {{ background: var(--card); color: var(--ink); border: 1px solid var(--grid); border-radius: 999px;
    padding: 6px 14px; font: inherit; font-size: 13px; cursor: pointer; }}
  button:hover {{ background: var(--soft); }}
  .turn {{ background: var(--card); border: 1px solid var(--grid); border-radius: 12px;
    padding: 16px 18px; margin: 0 0 16px; scroll-margin-top: 16px; }}
  .turn h2 {{ font-size: 15px; margin: 0 0 10px; }}
  .turn h2 a {{ color: var(--accent); text-decoration: none; }}
  .user {{ background: var(--user); border-left: 3px solid var(--user-edge); border-radius: 6px;
    padding: 10px 14px; }}
  .who {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; }}
  .user p {{ margin: 2px 0 0; white-space: pre-wrap; color: var(--ink); overflow-wrap: anywhere; }}
  details {{ margin-top: 10px; }}
  summary {{ cursor: pointer; color: var(--accent); font-size: 14px; font-weight: 600; padding: 4px 0; }}
  summary .count {{ color: var(--muted); font-weight: 400; font-size: 12px; margin-left: 6px; }}
  pre {{ background: var(--pre); border: 1px solid var(--grid); border-radius: 8px; padding: 14px;
    margin: 8px 0 0; white-space: pre-wrap; overflow-wrap: anywhere;
    font: 12.5px/1.5 ui-monospace, SFMono-Regular, Consolas, "Cascadia Mono", monospace; color: var(--text); }}
  pre .say {{ color: var(--ink); font-weight: 600; }}
  pre .tool {{ color: var(--muted); }}
  pre .timing {{ color: var(--muted); font-style: italic; }}
  @media (max-width: 860px) {{
    .layout {{ grid-template-columns: 1fr; }}
    aside {{ position: static; height: auto; max-height: 40vh; border-right: none;
      border-bottom: 1px solid var(--grid); }}
    main {{ padding: 20px 16px 48px; }}
  }}
</style>
</head>
<body>
<div class="layout">
<aside aria-label="Turns">
  <h3>{len(turns)} turns</h3>
  <ol>
{toc}
  </ol>
</aside>
<main>
<header>
  <h1>{html.escape(title)}</h1>
  <p>{meta} · {len(turns)} turns. User messages are shown; click a response to expand it.</p>
</header>
{f'<div class="note">{html.escape(note)}</div>' if note else ""}
<div class="controls">
  <button type="button" id="expand">Expand all responses</button>
  <button type="button" id="collapse">Collapse all</button>
  <button type="button" id="theme">Toggle theme</button>
</div>
{articles}
</main>
</div>
<script>
  (function () {{
    var all = document.querySelectorAll("details");
    document.getElementById("expand").onclick = function () {{ all.forEach(function (d) {{ d.open = true; }}); }};
    document.getElementById("collapse").onclick = function () {{ all.forEach(function (d) {{ d.open = false; }}); }};
    var root = document.documentElement;
    try {{ var saved = localStorage.getItem("theme"); if (saved) root.setAttribute("data-theme", saved); }} catch (e) {{}}
    document.getElementById("theme").onclick = function () {{
      var cur = root.getAttribute("data-theme") ||
        (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {{ localStorage.setItem("theme", next); }} catch (e) {{}}
    }};
    // Opening a turn from the sidebar also expands its response
    function openHash() {{
      var el = location.hash && document.querySelector(location.hash);
      if (el) {{ var d = el.querySelector("details"); if (d) d.open = true; }}
    }}
    window.addEventListener("hashchange", openHash);
    openHash();
  }})();
</script>
</body>
</html>
'''


def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "transcript.md"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "transcript.html"
    title = sys.argv[3] if len(sys.argv) > 3 else "Project 1 (EpiClim): Claude Code transcript"
    note = sys.argv[4] if len(sys.argv) > 4 else ""
    with open(in_path, encoding="utf-8") as f:
        header, turns = parse(f.read())
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_html(header, turns, title, note))
    print(f"{len(turns)} turns -> {out_path}")


if __name__ == "__main__":
    main()
