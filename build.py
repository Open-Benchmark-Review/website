"""Build the Open Benchmark Review website into docs/.

Inputs (all under content/ unless noted):
  site.json           name, tagline, domain, GitHub repository, contact email, and the review sections
  benchmarks.json     one entry per reviewed benchmark: section, verdict, headline claim, footnote, rubric statuses
  pages/*.html        hand-written pages (methodology, about, submit): title, lead, toc and main fragments
  reviews/<slug>.html each benchmark's full review page, in the Epoch review layout
  style.css           the stylesheet
  ../assets/          logo, favicons, ridgeline art and the X banner

Output: docs/, a static site with no build-time dependencies beyond Python 3:
  index.html                     landing page: mission, why, what we do, principles, review sections
  benchmarks/index.html          every reviewed benchmark, grouped by section (ML Benchmarks first)
  benchmarks/<slug>.html         one page per review
  methodology.html, about.html, submit.html, 404.html, sitemap.xml, robots.txt, CNAME
Serve it with `python3 -m http.server -d docs`; GitHub Pages serves it from main /docs.

Share cards (Open Graph images) are rendered by `node render_cards.js` from the HTML this script
writes to build/cards/; run it after this script if Node and Playwright are available.

usage: python3 -I build.py
"""
import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
DIST = os.path.join(ROOT, "docs")
CARDS = os.path.join(ROOT, "build", "cards")

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=Open+Sans:wght@400;600;700;800&display=swap")
SITE = json.load(open(os.path.join(CONTENT, "site.json"), encoding="utf-8"))
BENCH = json.load(open(os.path.join(CONTENT, "benchmarks.json"), encoding="utf-8"))
SECTIONS = SITE["sections"]
NAME, REPO, EMAIL, DOMAIN = SITE["name"], SITE["repo"].rstrip("/"), SITE["email"], SITE["domain"]
BASE_URL = f"https://{DOMAIN}"


def in_section(s):
    return [b for b in BENCH if b["section"] == s["slug"]]


def mark(size, label=True):
    aria = 'role="img" aria-label="OBR*"' if label else 'aria-hidden="true"'
    sw = 20 if size <= 48 else 17
    return (f'<svg viewBox="0 0 400 400" width="{size}" height="{size}" {aria}><circle cx="200" cy="200" r="200" '
            f'fill="#8B1E1A"/><text x="47" y="250" fill="#FFFFFF" font-family="\'Open Sans\', sans-serif" '
            f'font-weight="800" font-size="116" letter-spacing="-4.5">OBR</text><g transform="translate(321 185)" '
            f'stroke="#FFFFFF" stroke-width="{sw}" stroke-linecap="round"><line x1="0" y1="-26" x2="0" y2="26"/>'
            f'<line x1="-22.5" y1="-13" x2="22.5" y2="13"/><line x1="-22.5" y1="13" x2="22.5" y2="-13"/></g></svg>')


def badge(verdict):
    cls = {"Flawed": "flawed", "Verified": "verified", "Not enough info": "nei"}[verdict]
    mk = '<span class="mk" aria-hidden="true">*</span>' if verdict == "Flawed" else ""
    return f'<span class="badge {cls}">{mk}{html.escape(verdict)}</span>'


BENCH_DIR = "benchmarks"


def header(prefix, current):
    links = [(f"{BENCH_DIR}/index.html", "Benchmarks"), ("methodology.html", "Methodology"),
             ("submit.html", "Submit a review"), ("about.html", "About")]
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{prefix}{h}"{cur if t == current else ""}>{t}</a>' for h, t in links)
    return (f'<header class="site-header"><div class="container"><a class="brand" href="{prefix}index.html">'
            f'{mark(40, label=False)}<span>{NAME}</span></a><nav class="site-nav" aria-label="Site">{nav}</nav>'
            f'</div></header>')


def footer(prefix):
    sec = f'<a href="{prefix}{BENCH_DIR}/index.html">Benchmarks</a>'
    return (f'<footer class="site-footer"><div class="container"><div class="fb">{mark(32, label=False)}'
            f'<p>{NAME} publishes independent reviews of AI benchmarks against a public rubric, with the evidence '
            f'for every finding.</p></div><nav aria-label="Footer">{sec}'
            f'<a href="{prefix}methodology.html">Methodology</a><a href="{prefix}submit.html">Submit a review</a>'
            f'<a href="{prefix}about.html">About</a><a href="{REPO}">GitHub</a></nav>'
            f'<p class="fine">{NAME} is not affiliated '
            f'with or endorsed by Epoch AI. Contact: <span class="mono">{EMAIL}</span></p></div></footer>')


def document(title, description, body, prefix, path, og_image="assets/og/home.png", page_class=""):
    url = f"{BASE_URL}/{path}" if path else f"{BASE_URL}/"
    img = f"{BASE_URL}/{og_image}"
    t, d = html.escape(title), html.escape(description)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#8B1E1A">
<link rel="icon" href="{prefix}assets/favicon.ico" sizes="any">
<link rel="icon" href="{prefix}assets/obr-mark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body class="{page_class}">
{body}
</body>
</html>
'''


def page_with_toc(prefix, current, head_html, toc, main):
    return (f'{header(prefix, current)}<div class="page-head"><div class="container">{head_html}</div></div>'
            f'<div class="body"><div class="container layout"><nav class="toc" aria-label="On this page">'
            f'<span class="label">On this page</span><ol>{toc}</ol></nav><main>{main}</main></div></div>'
            f'{footer(prefix)}')


def fill(text):
    text = text.replace("{{repo}}", REPO).replace("{{email}}", EMAIL)
    return re.sub(r"\{\{badge:([^}]+)\}\}", lambda m: badge(m.group(1)), text)


def rate(b):
    return 100 * b["defects"] / b["inspected"]


def has_page(b):
    return b.get("page", True)


def creator_html(b, text=None):
    """The creator text with the creator's own website linked, where we know it."""
    out = html.escape(text if text is not None else b["creator"]) if text is None else text
    for name, url in b.get("creator_links", {}).items():
        key = html.escape(name)
        if key in out:
            return out.replace(key, f'<a href="{url}" target="_blank" rel="noopener">{key}</a>', 1)
    return out


def acard(b, href):
    title = (f'<a href="{href}">{b["name"]}</a>' if has_page(b) else b["name"])
    head = (f'<div class="t"><h3>{title}</h3>{badge(b["verdict"])}</div>'
            f'<div class="who">{creator_html(b)} · {html.escape(b["measures"])}</div>')
    if not has_page(b):
        return f'<div class="acard nolink">{head}</div>'
    return (f'<div class="acard">{head}'
            f'<div class="meta"><div class="rate">{b["defects"]}/{b["inspected"]}<small>tasks defective</small>'
            f'</div><a class="go" href="{href}">Read the review →</a></div></div>')


# ---------- landing page ----------

def landing():
    n = len(BENCH)
    nfl = sum(b["verdict"] == "Flawed" for b in BENCH)
    nver = sum(b["verdict"] == "Verified" for b in BENCH)
    tiles = "".join(
        f'<a class="section-tile" href="{BENCH_DIR}/index.html#{s["slug"]}"><div><h3>{s["name"]}</h3>'
        f'<p>{html.escape(s["blurb"])}</p></div><div class="count"><b>{len(in_section(s))}</b><span>reviews</span>'
        f'</div></a>' for s in SECTIONS)
    body = f'''{header("", None)}
<section class="hero"><div class="container"><div class="hero-copy">
  <h1>{SITE["tagline"]}<span class="ast">*</span></h1>
  <p class="sub">We review the benchmarks used to measure AI progress, and publish what we find with the evidence to check it.</p>
  <div class="actions"><a class="btn primary" href="{BENCH_DIR}/index.html">Read the reviews</a><a class="btn" href="#mission">Our mission</a></div>
</div><div class="hero-art"><img src="assets/ridgeline.png" width="1697" height="929" alt="A ridgeline of benchmark score distributions, with one red distribution that does not fit the rest"></div></div></section>

<section class="band" id="mission" aria-labelledby="h-mission"><div class="container">
  <h2 id="h-mission" class="sr-only">Our mission</h2>
  <div class="mission">
    <p class="statement">Benchmark scores decide which AI models get used, which research gets attention, and how fast people think AI is improving. Most of those scores are never checked by anyone outside the team that built the benchmark. We check them.</p>
    <div class="more">
      <p>Our aim is simple: every headline score should come with what you need to read it. What the benchmark really measures, where its grading goes wrong, and whether its ranking holds up.</p>
      <p>We do this in public. Every review uses a published rubric, cites its evidence, and ships the code that reproduces its numbers, so anyone can check our work too.</p>
    </div>
  </div>
</div></section>

<section class="band page" aria-labelledby="h-why"><div class="container">
  <div class="band-head"><h2 id="h-why">Benchmarks break in quiet ways</h2></div>
  <div class="three">
    <div><h3>Grading goes wrong</h3><p>A grader that rejects correct work, or accepts a shortcut, changes the score and nobody notices. Every benchmark we have been able to fully review so far had this problem.</p></div>
    <div><h3>Agents find the gaps</h3><p>AI agents are good at raising a score without doing the task. If a benchmark allows it, its leaderboard rewards it.</p></div>
    <div><h3>No one is assigned to check</h3><p>Benchmark teams move on to the next release, and readers can't inspect the code behind a leaderboard. Independent review fills that gap.</p></div>
  </div>
</div></section>

<section class="band" aria-labelledby="h-what"><div class="container">
  <div class="band-head"><h2 id="h-what">From leaderboard to evidence</h2></div>
  <ol class="steps">
    <li><h3>Review</h3><p>We read the tasks, the grading code and, where they are released, the agents' own runs, and apply a public rubric to all of it.</p></li>
    <li><h3>Publish</h3><p>Each review gives a verdict, lists every error we count with its evidence, and includes the scripts that reproduce our numbers.</p></li>
    <li><h3>Follow up</h3><p>Benchmark developers can reply, and we link their response. A fixed version of a benchmark gets a new review.</p></li>
  </ol>
</div></section>

<section class="band cream" aria-labelledby="h-principles"><div class="container">
  <div class="band-head"><h2 id="h-principles">Our principles</h2></div>
  <div class="principles">
    <div><h4>A public rubric</h4><p>We apply Epoch AI's published benchmark review rubric as written. <a href="methodology.html">Read the methodology</a>.</p></div>
    <div><h4>Evidence for every finding</h4><p>Every error we count points to a file and line, a reproduction or a log. Suspicions without evidence are listed but not counted.</p></div>
    <div><h4>Reproducible</h4><p>Each review ships the scripts that fetch the public data and rebuild our counts.</p></div>
    <div><h4>A right of reply</h4><p>Developers can respond to any review, and their response is linked from it. Corrections are made in the open.</p></div>
    <div><h4>Independent</h4><p>We don't review benchmarks we helped build, and we are not affiliated with any benchmark we review.</p></div>
    <div><h4>Clear about limits</h4><p>Each review says what we could not inspect and how the reading was divided between people and tools.</p></div>
  </div>
</div></section>

<section class="band" id="reviews" aria-labelledby="h-reviews"><div class="container">
  <div class="band-head"><h2 id="h-reviews">Read the reviews</h2></div>
  {tiles}
  <div class="actions"><a class="btn primary" href="{BENCH_DIR}/index.html">See all benchmarks</a></div>
</div></section>

<section class="band page" aria-labelledby="h-involve"><div class="container">
  <div class="band-head"><h2 id="h-involve">Help us check more benchmarks</h2></div>
  <div class="involve">
    <div><h3>Suggest a benchmark</h3><p>Tell us which benchmark to review next.</p><a href="submit.html#suggest">How to suggest one →</a></div>
    <div><h3>Contribute a review</h3><p>Write a review to our rubric and evidence standard, and we will check it and publish it.</p><a href="submit.html#contribute">How to contribute →</a></div>
    <div><h3>Get in touch</h3><p>Corrections, developer responses and questions welcome at</p><span class="mono">{EMAIL}</span></div>
  </div>
</div></section>
{footer("")}'''
    desc = (f"{SITE['tagline']}. Independent reviews of AI benchmarks: {n} reviewed, {nfl} flawed. "
            "Evidence for every finding.")
    return document(f"{NAME}: {SITE['tagline']}", desc, body, "", "", page_class="landing")


# ---------- section page ----------

def chart(bs, prefix):
    rows = []
    for b in sorted(bs, key=lambda b: -rate(b)):
        lb = f'<div class="lb" style="left:{100 * b["lower_bound"]:.1f}%"></div>' if b.get("lower_bound") else ""
        rows.append(f'<div class="crow"><div class="name"><a href="{prefix}{b["slug"]}.html">{b["name"]}</a></div>'
                    f'<div class="track"><div class="bar" style="width:{rate(b):.1f}%"></div>{lb}<div class="thr"></div>'
                    f'</div><div class="val">{rate(b):.1f}%</div></div>')
    label = "; ".join(f'{b["name"]} {rate(b):.1f} percent' for b in bs)
    lbs = "".join(f'<span><i class="k-lb"></i>{b["name"]} lower bound: {b["lower_bound_note"]}</span>'
                  for b in bs if b.get("lower_bound"))
    return (f'<div class="chart" role="img" aria-label="Share of checked tasks with a confirmed grading defect: '
            f'{label}. Flawed threshold 20 percent."><div><div class="title">Share of checked tasks with a confirmed '
            f'grading defect</div><div class="src">From each review\'s task log.</div></div>{"".join(rows)}<div class="axis" aria-hidden="true"><div></div><div class="ticks">'
            f'<span style="left:0">0%</span><span style="left:20%">20%</span><span class="mid" style="left:40%">40%</span>'
            f'<span class="mid" style="left:60%">60%</span><span class="mid" style="left:80%">80%</span>'
            f'<span style="left:100%">100%</span></div><div></div></div><div class="legend"><span><i class="k-bar"></i>'
            f'Defect rate</span><span><i class="k-thr"></i>Flawed threshold, 20%</span>{lbs}</div></div>')


def benchmarks_page():
    """One page listing every reviewed benchmark, grouped by section (ML Benchmarks first)."""
    blocks, toc = [], []
    for sec in SECTIONS:
        bs = in_section(sec)
        rubric_rows = "".join(
            (f'<tr><th scope="row"><a href="{b["slug"]}.html">{b["name"]}</a></th>' if has_page(b)
             else f'<tr><th scope="row">{b["name"]}</th>') + "".join(
                f'<td title="{html.escape(b["rubric"][k][2])}"><span class="rs {b["rubric"][k][0]}">'
                f'{b["rubric"][k][1]}</span></td>'
                for k in ("reviewability", "scoring", "consistency", "elicitation", "bias")) + "</tr>" for b in bs)
        cards = "".join(acard(b, f'{b["slug"]}.html') for b in bs)
        sid = sec["slug"]
        blocks.append(f'''
<section id="{sid}" aria-labelledby="h-{sid}">
  <h2 id="h-{sid}">{sec["name"]}</h2>
  <p>{html.escape(sec["blurb"])}</p>
  <div class="cards">{cards}</div>
  <h3 id="{sid}-rates">How much of each benchmark is affected</h3>
  {chart([b for b in bs if b.get("defects") is not None], "")}
  <h3 id="{sid}-rubric">Rubric results</h3>
  <p>Failing any check makes a benchmark Flawed. <a href="../methodology.html">Methodology</a>.</p>
  <div class="tbl"><table class="rubric"><thead><tr><th>Benchmark</th><th>Open to inspect</th><th>Grading</th><th>Consistency</th><th>Model setup</th><th>Fairness</th></tr></thead><tbody>{rubric_rows}</tbody></table></div>
</section>''')
        toc.append(f'<li><a href="#{sid}">{sec["name"]}</a><ol><li><a href="#{sid}-rates">How much is affected</a></li>'
                   f'<li><a href="#{sid}-rubric">Rubric results</a></li></ol></li>')
    coming = ('<section id="coming" aria-labelledby="h-coming" class="coming"><h2 id="h-coming">More benchmarks coming soon</h2>'
              '<p>Math, Reasoning and Multimodal reviews are on the way. <a href="../submit.html#suggest">'
              'Suggest one</a>.</p></section>')
    toc.append('<li><a href="#coming">Coming soon</a></li>')
    head = (f'<div class="crumbs"><a href="../index.html">{NAME}</a></div><h1>Benchmarks</h1>'
            f'<p class="lead">Every benchmark we have reviewed, by area.</p>')
    desc = f"Every benchmark {NAME} has reviewed, grouped by area, with verdicts and evidence."
    return document(f"Benchmarks · {NAME}", desc,
                    page_with_toc("../", "Benchmarks", head, "".join(toc), "".join(blocks) + coming), "../",
                    f"{BENCH_DIR}/")


# ---------- other pages ----------

def fragment(path, current, out_name):
    t = fill(open(path, encoding="utf-8").read())
    title = re.search(r"<!-- title: (.*?) -->", t).group(1)
    lead = re.search(r"<!-- lead: (.*?) -->", t, re.S).group(1)
    toc = t.split("<!-- toc -->", 1)[1].split("<!-- main -->", 1)[0]
    main = t.split("<!-- main -->", 1)[1]
    head = (f'<div class="crumbs"><a href="index.html">{NAME}</a></div><h1>{title}</h1>'
            + (f'<p class="lead">{lead}</p>' if lead.strip() else ""))
    if not toc.strip():
        body = (f'{header("", current)}<div class="page-head"><div class="container">{head}</div></div>'
                f'<div class="body"><div class="container"><main class="solo">{main}</main></div></div>{footer("")}')
        return document(f"{title} · {NAME}", lead.strip() or title, body, "", out_name)
    return document(f"{title} · {NAME}", lead, page_with_toc("", current, head, toc, main), "", out_name)



LEVEL_CLASS = {"Full": "pass", "Partial": "warn", "Inadequate": "neutral"}
BOILERPLATE = [
    r"<p>This is the minimum standard required to be Verified;[^<]*</p>",
    r"<p>This is the standard we would like all benchmarks to meet[^<]*</p>",
    r"<p>This review uses the format and rubric of Epoch AI's Benchmark Reviews\.[^<]*</p>",
]


DROP_SECTIONS = ("methodology",)          # covered by the standalone Methodology page
DROP_ANCHORS = ("methodology", "research-vs-gaming")


# Evaluation quality, in plain words: one row per check that applies, with a short bold answer.
QUALITY_ROWS = [  # (label in the review, plain label)
    ("Statistical adequacy", "Runs per model"),
    ("Elicitation and resource adequacy", "Enough time and compute"),
    ("Scaffold fairness", "Same agent setup for every model"),
    ("Is there evidence or risk of contamination?", "Test data exposure"),
    ("Construct validity", "Measures what it claims"),
]
QUALITY_SHORT = {
    "Sufficient": "Yes", "Constraining": "Mostly", "Unreasonably constraining": "No", "Unknown": "Unknown",
    "Shared common scaffold": "Yes", "Mix": "Partly", "Model-specific scaffolds": "No, each model uses its own",
    "Measures stated capabilities": "Yes", "Partially measures stated capabilities": "Partly",
    "Does not measure stated capabilities": "No",
}


def simple_quality(m):
    rows = {}
    for label, cell in re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", m.group(0), re.S):
        rows[re.sub(r":.*", "", label, flags=re.S).strip()] = cell
    out = []
    for key, plain in QUALITY_ROWS:
        cell = rows.get(key)
        if cell is None:
            continue
        chip = re.search(r'<span class="opt on [a-z]+">([^<]+)</span>', cell)
        note = re.sub(r'<div class="opts"[^>]*>.*?</div>', "", cell, flags=re.S).strip()
        if chip:
            note = f"<strong>{QUALITY_SHORT.get(chip.group(1), chip.group(1))}.</strong> {note}"
        out.append(f"<tr><td>{plain}</td><td>{note}</td></tr>")
    return ('<table class="eq"><thead><tr><th>Check</th><th>What we found</th></tr></thead><tbody>'
            + "".join(out) + "</tbody></table>")


def trim_review(main):
    """Strip rubric boilerplate that repeats in every review; keep each review's own statuses and notes."""
    for sid in DROP_SECTIONS:
        main = re.sub(r'\s*<section id="%s".*?</section>' % sid, "", main, flags=re.S)
    main = re.sub(r'\s*<h3 id="research-vs-gaming">.*?(?=\s*</section>)', "", main, flags=re.S)
    main = re.sub(r'<div><span class="lbl">Examples</span>.*?</div>\s*', "", main, flags=re.S)
    main = re.sub(r'<div><span class="lbl">Default threshold for Flawed</span>[^<]*</div>\s*', "", main)
    for pat in BOILERPLATE:
        main = re.sub(r"\s*" + pat, "", main)

    def level(m):
        on = re.search(r'<tr class="on"><td>([^<]+)</td>', m.group(0))
        name = on.group(1) if on else "Unknown"
        return f'<div class="opts"><span class="opt on {LEVEL_CLASS.get(name, "neutral")}">{name}</span></div>'
    main = re.sub(r'<div class="tbl">\s*<table class="levels">.*?</table>\s*</div>', level, main, flags=re.S)
    main = re.sub(r'<span class="opt">[^<]*</span>', "", main)
    main = main.replace("Flag [stop → Flawed]", "Flag")
    main = re.sub(r'<table class="eq">.*?</table>', simple_quality, main, flags=re.S)
    main = main.replace("3. Evaluation Quality", "3. Evaluation quality")
    return main


def review(b):
    s = next(x for x in SECTIONS if x["slug"] == b["section"])
    t = open(os.path.join(CONTENT, "reviews", f'{b["slug"]}.html'), encoding="utf-8").read()
    meta = dict((re.sub(r"<[^>]+>", "", dt).strip(), dd.strip())
                for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", t, re.S))
    toc = re.search(r'<nav class="toc"[^>]*>.*?<ol>(.*)</ol>\s*</nav>', t, re.S).group(1)
    for a in DROP_ANCHORS:
        toc = re.sub(r'\s*<li><a href="#%s">[^<]*</a></li>' % a, "", toc)
    main = re.search(r"<main>(.*)</main>", t, re.S).group(1)
    base = f"{REPO}/blob/main/audits/{b['slug']}/"
    main = re.sub(r'href="(?!https?:|#|mailto:)([^"]+)"', lambda m: f'href="{base}{m.group(1)}"', main)
    main = trim_review(main)
    head = (f'<div class="crumbs"><a href="../index.html">{NAME}</a> · <a href="index.html">Benchmarks</a> · '
            f'<a href="index.html#{s["slug"]}">{s["name"]}</a></div>'
            f'<h1>{html.escape(b["name"])}</h1>'
            f'<div class="facts"><p><strong>Benchmark creator:</strong> {creator_html(b, meta.get("Benchmark creator", ""))}</p>'
            f'<p><strong>Original benchmark:</strong> <a href="{b["benchmark_url"]}" target="_blank" rel="noopener">'
            f'{html.escape(b["benchmark_label"])}</a></p>'
            f'<p><strong>Version reviewed:</strong> {meta.get("Version reviewed", "")}</p>'
            f'<p><strong>Verdict:</strong> {badge(b["verdict"])}</p>'
            f'<p><a href="{REPO}/tree/main/audits/{b["slug"]}">Full report, task log and scripts</a></p></div>')
    desc = f'{b["name"]} is rated {b["verdict"]}. {b["summary"]}'
    return document(f'{b["name"]} review · {NAME}', desc, page_with_toc("../", "Benchmarks", head, toc, main), "../",
                    f'{BENCH_DIR}/{b["slug"]}.html', og_image=f'assets/og/{b["slug"]}.png')


def not_found():
    head = (f'<div class="eyebrow">404</div><h1>This page has an asterisk<span class="ast">*</span></h1>'
            f'<p class="claim-note">* It does not exist. Try the <a href="/index.html">home page</a> or the '
            f'<a href="/{BENCH_DIR}/index.html">benchmarks</a>.</p>')
    body = f'{header("/", None)}<div class="page-head"><div class="container">{head}</div></div>{footer("/")}'
    return document(f"Not found · {NAME}", "Page not found.", body, "/", "404.html")


# ---------- share cards ----------

def card_html(title_html, note, kicker):
    return f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}">
<style>html,body{{margin:0}}body{{width:1200px;height:630px;background:#FBF8EF;font-family:'Open Sans',sans-serif;
color:#1B1B1B;display:grid;grid-template-columns:520px 1fr;align-items:center;overflow:hidden;border-top:10px solid #8B1E1A;box-sizing:border-box}}
.art{{height:100%;display:flex;align-items:center}}.art img{{width:560px;margin-left:-40px}}
.copy{{padding:0 64px 0 24px;display:grid;gap:22px}}.k{{font-family:'IBM Plex Mono',monospace;font-size:20px;letter-spacing:.14em;
text-transform:uppercase;color:#8B1E1A}}h1{{margin:0;font-size:50px;line-height:1.1;font-weight:700;letter-spacing:-.01em}}
.a{{color:#8B1E1A;font-weight:800}}.n{{font-family:'IBM Plex Mono',monospace;font-size:22px;line-height:1.45;color:#8B1E1A}}
.brand{{display:flex;align-items:center;gap:14px;font-size:24px;font-weight:700}}</style></head><body>
<div class="art"><img src="../../assets/ridgeline.png" alt=""></div>
<div class="copy"><div class="k">{kicker}</div><h1>{title_html}</h1>{f'<div class="n">* {html.escape(note)}</div>' if note else ''}
<div class="brand">{mark(52, label=False)}<span>{DOMAIN}</span></div></div></body></html>'''


def write_cards():
    shutil.rmtree(os.path.join(ROOT, "build"), ignore_errors=True)
    os.makedirs(CARDS)
    jobs = {"home": card_html(f'{SITE["tagline"]}<span class="a">*</span>', "", NAME)}
    for b in [b for b in BENCH if has_page(b)]:
        jobs[b["slug"]] = card_html(f'{html.escape(b["name"])} is rated {b["verdict"]}<span class="a">*</span>',
                                    f'{b["defects"]} of {b["inspected"]} {b["unit"]} have grading defects.',
                                    "Benchmark review")
    for k, v in jobs.items():
        open(os.path.join(CARDS, f"{k}.html"), "w", encoding="utf-8").write(v)


# ---------- build ----------

def main():
    # Keep previously rendered share cards, so a rebuild without Playwright does not lose them.
    og = os.path.join(DIST, "assets", "og")
    cards = {f: open(os.path.join(og, f), "rb").read() for f in os.listdir(og)} if os.path.isdir(og) else {}
    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    os.makedirs(og, exist_ok=True)
    for f, data in cards.items():
        with open(os.path.join(og, f), "wb") as fh:
            fh.write(data)
    shutil.copy(os.path.join(CONTENT, "style.css"), os.path.join(DIST, "style.css"))
    out = {"index.html": landing(), "404.html": not_found(),
           "methodology.html": fragment(os.path.join(CONTENT, "pages", "methodology.html"), "Methodology",
                                        "methodology.html"),
           "about.html": fragment(os.path.join(CONTENT, "pages", "about.html"), "About", "about.html"),
           "submit.html": fragment(os.path.join(CONTENT, "pages", "submit.html"), "Submit a review", "submit.html")}
    os.makedirs(os.path.join(DIST, BENCH_DIR), exist_ok=True)
    out[f"{BENCH_DIR}/index.html"] = benchmarks_page()
    for b in BENCH:
        if has_page(b):
            out[f'{BENCH_DIR}/{b["slug"]}.html'] = review(b)
    for path, text in out.items():
        open(os.path.join(DIST, path), "w", encoding="utf-8").write(text)
    open(os.path.join(DIST, "CNAME"), "w").write(DOMAIN + "\n")
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    open(os.path.join(DIST, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    locs = [re.sub(r"(^|/)index\.html$", r"\1", p) for p in out if p != "404.html"]
    open(os.path.join(DIST, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{BASE_URL}/{u}</loc></url>\n" for u in locs) + "</urlset>\n")
    write_cards()
    print(f"built {len(out)} pages into docs/")
    if "todo" in SITE:
        print("NOTE:", SITE["todo"])


if __name__ == "__main__":
    main()
