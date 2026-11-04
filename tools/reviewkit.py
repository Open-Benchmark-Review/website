"""Shared pieces for the short-form review pages in content/reviews/.

Every review page has the same five sections: Summary, Errors, Case studies, Disclaimer, Notes.
A benchmark's own script (tools/<slug>.py) supplies the words, the errors, the case studies and any
charts, and calls `write_page()`. The styles live in content/style.css; the scripts are inlined here.

House rules (see PRODUCT.md): plain human voice; attempt IDs and step numbers only in the folded
"Where" lists, quote footers and hover citations; steps written "#X"; no all-caps labels or numbered
headings.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWS = os.path.join(ROOT, 'content', 'reviews')
REPO = json.load(open(os.path.join(ROOT, 'content', 'site.json'), encoding='utf-8'))['repo'].rstrip('/')

# Chart colours: one highlight, one comparison, one neutral. Validated for contrast on white.
RED, BLUE, GRAY, DARK = '#B5432F', '#3B6FB6', '#958E86', '#5A5A5A'  # GRAY is 3.2:1 on white

_cfg = {'attempt_url': lambda task, trial: '#', 'models': {}}
_ids = [0]


def configure(attempt_url, models):
    """attempt_url(task, trial) -> link to that attempt; models: {trial_id: model name}."""
    _cfg['attempt_url'] = attempt_url
    _cfg['models'] = models


def model(trial):
    return _cfg['models'].get(trial, '')


def c(x):
    return f'<code>{x}</code>'


# --- Hover citations -------------------------------------------------------------------------

def E(task, trial, steps=None, file=None, note=None):
    """One attempt: shown in the hover box as its link, model and steps (file and note are source data only)."""
    return dict(task=task, trial=trial, steps=steps, file=file, note=note)


def X(label, url=None, note=None):
    """A source that is not an attempt (a file in the repo, a registry page, a blog post)."""
    return dict(label=label, url=url, note=note)


def _entry(e):
    if 'trial' in e:
        head = (f'<a class="att" href="{_cfg["attempt_url"](e["task"], e["trial"])}">{e["trial"]}</a>'
                f'<span class="xm">{model(e["trial"])}</span>')
        lines = []
        if e['steps']:
            s = e['steps']
            fmt = lambda x: '–'.join('#' + p for p in str(x).split('–'))
            lines.append(('Step ' if len(s) == 1 and '–' not in str(s[0]) else 'Steps ') +
                         ', '.join(fmt(x) for x in s))
    else:
        head = f'<a href="{e["url"]}">{e["label"]}</a>' if e['url'] else f'<span>{e["label"]}</span>'
        lines = []
    return ('<span class="xe"><span class="xh">' + head + '</span>'
            + ''.join(f'<span class="xl">{ln}</span>' for ln in lines) + '</span>')


def A(task, trial):
    """A plain link to one attempt, for quote footers."""
    return f'<a class="att" href="{_cfg["attempt_url"](task, trial)}">{trial}</a>'


def cite(text, *entries):
    """Underline `text`; hovering (mouse), tapping, or Enter shows its sources."""
    _ids[0] += 1
    pid = f'src{_ids[0]}'
    return (f'<span class="xref"><span class="xref-t" tabindex="0" role="button" aria-expanded="false" '
            f'aria-controls="{pid}">{text}</span><span class="xref-pop" id="{pid}">'
            + ''.join(_entry(e) for e in entries) + '</span></span>')


def quote(text, who, task, trial, step, caption=None, code=None):
    """An agent quote with a 'Model · attempt · step #X' footer. `code` puts a code block inside the quote."""
    cap = f'<p class="qcap">{caption}</p>' if caption else ''
    body = f'<pre>{html.escape(code)}</pre>' if code else f'<p>{text}</p>'
    st = f' · step #{step}' if step is not None else ''
    return f'<blockquote class="agent">{cap}{body}<footer>{who} · {A(task, trial)}{st}</footer></blockquote>'


# --- Errors list -----------------------------------------------------------------------------

def ev(task, trial, detail):
    """One attempt source in a Where list: attempt link, model, then what to look at."""
    return dict(trial=trial, html=(f'<a class="att" href="{_cfg["attempt_url"](task, trial)}">{trial}</a> '
                                   f'<span class="mdl">{model(trial)}</span> · {detail}'))


def src(text, label=None):
    """A source that is not an attempt (a file and line, a commit, a README). `label` names it in the summary."""
    return dict(trial=None, label=label, html=text)


def _where(sources):
    groups, labels = [], []
    for s in sources:
        t = s['trial']
        if not t:
            if s.get('label') and s['label'] not in labels:
                labels.append(s['label'])
            continue
        if groups and groups[-1][0] == model(t):
            if t not in groups[-1][1]:
                groups[-1][1].append(t)
        elif not any(t in g[1] for g in groups):
            groups.append((model(t), [t]))
    parts = [', '.join(ts) + (f' ({m})' if m else '') for m, ts in groups] + labels
    n = len(sources)
    return 'Where: ' + (', '.join(parts) + ' · ' if parts else '') + f'{n} source{"s" if n != 1 else ""}'


SHOW_FIRST = 3  # errors shown before "Show N more errors"


def errors_list(rows, h='h3', start=0):
    """rows: dicts with id, title, desc, meta (html line under the description) and sources.

    `start` is the number of errors already listed above (in earlier groups); errors past SHOW_FIRST get class
    "more" and are folded behind the "Show N more errors" button when scripts run."""
    items = ''
    for i, r in enumerate(rows):
        meta = f'<p class="emeta">{r["meta"]}</p>' if r.get('meta') else ''
        more = ' class="more"' if start + i >= SHOW_FIRST else ''
        items += (f'<li id="{r["id"]}"{more}><{h} class="et">{r["title"]}</{h}><p class="ed">{r["desc"]}</p>{meta}'
                  f'<details class="ew"><summary>{_where(r["sources"])}</summary><ul>'
                  + ''.join(f'<li>{s["html"]}</li>' for s in r['sources']) + '</ul></details></li>\n')
    return f'<ol class="errlist">\n{items}</ol>'


def errors_html(errors, noun='error'):
    """errors: a list of rows, or a list of groups dict(title, lead, rows) shown under subheads."""
    if errors and 'rows' in errors[0]:
        out, n = '', 0
        for g in errors:
            lead = f'<p class="elead">{g["lead"]}</p>' if g.get('lead') else ''
            more = ' more' if n >= SHOW_FIRST else ''
            out += (f'<div class="egrp{more}"><h3 class="egroup">{g["title"]}</h3>{lead}'
                    f'{errors_list(g["rows"], "h4", n)}</div>')
            n += len(g['rows'])
    else:
        n = len(errors)
        out = errors_list(errors)
    if n > SHOW_FIRST:
        k = n - SHOW_FIRST
        pl = 's' if k != 1 else ''
        out += (f'<button type="button" class="moreerr" aria-expanded="false" data-more="Show {k} more '
                f'{noun}{pl}" data-less="Show fewer {noun}s">Show {k} more {noun}{pl}</button>')
    return out


# --- Charts ----------------------------------------------------------------------------------

def figure(title, svg, caption, legend=None, fid=None, extra='', narrow=None):
    """Wrap an <svg> in the standard chart frame. `legend` is a list of (colour, label).

    `narrow` is a second <svg> laid out for phones (viewBox about 380 wide, labels above rows, no right gutter);
    it replaces the wide one below 640px. Without it, the wide chart scrolls sideways on phones.
    """
    leg = ''
    if legend:
        leg = '<div class="viz-legend">' + ''.join(
            f'<span><i style="background:{col}"></i>{lab}</span>' for col, lab in legend) + '</div>'
    idattr = f' id="{fid}"' if fid else ''
    return (f'<figure class="viz"{idattr}><div class="viz-title">{title}</div>{leg}'
            + (f'<div class="viz-wrap"><div class="wide">{svg}</div><div class="narrow">{narrow}</div></div>' if narrow
               else '<div class="viz-wrap scroll" tabindex="0" role="group" aria-label="Chart, scrolls sideways on '
                    f'small screens">{svg}</div>')
            + f'<figcaption>{caption}</figcaption>{extra}</figure>')


# --- Page ------------------------------------------------------------------------------------

SCRIPT = '''<script>
(function () {
  var refs = document.querySelectorAll('.xref'), timer = null;
  function place(r) {
    var btn = r.querySelector('.xref-t'), pop = r.querySelector('.xref-pop');
    var b = btn.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight, pad = 12;
    var left = Math.min(Math.max(pad, b.left + b.width / 2 - w / 2), innerWidth - pad - w);
    var top = b.top - h - 6; if (top < pad) top = b.bottom + 6;
    pop.style.left = left + 'px'; pop.style.top = top + 'px';
  }
  function open(r) {
    clearTimeout(timer);
    refs.forEach(function (o) { if (o !== r) { o.classList.remove('open'); o.querySelector('.xref-t').setAttribute('aria-expanded', 'false'); } });
    r.classList.add('open'); r.querySelector('.xref-t').setAttribute('aria-expanded', 'true'); place(r);
  }
  function close(r) { r.classList.remove('open'); r.querySelector('.xref-t').setAttribute('aria-expanded', 'false'); }
  refs.forEach(function (r) {
    var btn = r.querySelector('.xref-t');
    r.addEventListener('pointerenter', function (ev) { if (ev.pointerType === 'mouse') open(r); });
    r.addEventListener('pointerleave', function (ev) { if (ev.pointerType === 'mouse') { clearTimeout(timer); timer = setTimeout(function () { close(r); }, 180); } });
    btn.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); r.classList.contains('open') ? close(r) : open(r); } });
    btn.addEventListener('blur', function () { setTimeout(function () { if (!r.contains(document.activeElement)) close(r); }, 0); });
    btn.addEventListener('click', function (ev) {
      ev.stopPropagation();
      if (ev.pointerType === 'mouse') { open(r); return; }
      r.classList.contains('open') ? close(r) : open(r);
    });
  });
  document.addEventListener('click', function (ev) { if (!ev.target.closest('.xref')) refs.forEach(close); });
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return;
    var o = document.querySelector('.xref.open'); refs.forEach(close); if (o) o.querySelector('.xref-t').focus();
  });
  addEventListener('scroll', function () { refs.forEach(function (r) { if (r.classList.contains('open')) place(r); }); }, true);
  addEventListener('resize', function () { refs.forEach(function (r) { if (r.classList.contains('open')) place(r); }); });

  var sec = document.getElementById('errors'), mb = document.querySelector('.moreerr');
  function fold(on) {
    if (!sec || !mb) return;
    sec.classList.toggle('folded', on);
    mb.setAttribute('aria-expanded', on ? 'false' : 'true');
    mb.textContent = on ? mb.getAttribute('data-more') : mb.getAttribute('data-less');
  }
  function reveal() {
    var t = location.hash && document.getElementById(location.hash.slice(1));
    if (t && sec && sec.contains(t) && t.closest('.more')) { fold(false); t.scrollIntoView(); }
  }
  if (mb) {
    fold(true);
    mb.addEventListener('click', function () {
      var opening = sec.classList.contains('folded');
      fold(!opening);
      if (opening) { var first = sec.querySelector('.more .et, li.more .et'); if (first) { first.setAttribute('tabindex', '-1'); first.focus({ preventScroll: true }); } }
      else { mb.scrollIntoView({ block: 'nearest' }); }
    });
    reveal(); addEventListener('hashchange', reveal);
  }
  var btn = document.querySelector('.showall'), all = [].slice.call(document.querySelectorAll('details.ew'));
  if (btn) btn.addEventListener('click', function () {
    var on = btn.getAttribute('aria-pressed') !== 'true';
    if (on) fold(false);
    all.forEach(function (d) { d.open = on; });
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.textContent = on ? 'Hide all sources' : 'Show all sources';
  });

  var nav = document.querySelector('nav.toc'); if (!nav) return;
  var lab = nav.querySelector('.label'), list = nav.querySelector('ol'); if (!lab || !list) return;
  var t = document.createElement('button'); t.type = 'button'; t.className = 'toc-btn'; t.textContent = lab.textContent;
  t.setAttribute('aria-expanded', 'false'); lab.replaceWith(t);
  var mq = matchMedia('(max-width: 720px)');
  function apply() {
    if (mq.matches) { list.hidden = t.getAttribute('aria-expanded') !== 'true'; t.removeAttribute('tabindex'); }
    else { list.hidden = false; t.setAttribute('tabindex', '-1'); }
  }
  t.addEventListener('click', function () {
    if (!mq.matches) return;
    t.setAttribute('aria-expanded', t.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'); apply();
  });
  list.addEventListener('click', function (e) { if (mq.matches && e.target.closest('a')) { t.setAttribute('aria-expanded', 'false'); apply(); } });
  (mq.addEventListener ? mq.addEventListener('change', apply) : mq.addListener(apply)); apply();
})();
</script>'''


def write_page(slug, name, reviewed, creator, version, lede, found, errors, cases, disclaimer, notes,
               extra_script='', cases_intro='', verdict='Flawed', errors_heading='All errors'):
    """Write content/reviews/<slug>.html.

    lede: one paragraph (html) saying what the benchmark is.
    found: list of bullet strings (html) for "What we found".
    errors: rows for errors_list(), or groups dict(title, lead, rows) for errors_html().
    cases: list of (id, heading, body html); cases_intro: optional one or two sentences under the heading.
    disclaimer: one paragraph (html).
    notes: list of (id, html); cite them in the text with <sup><a href="#id">a</a></sup>.
    """
    found_html = ''.join(f'<li>{f}</li>' for f in found)
    cases_html = ''.join(f'<div class="case" id="{cid}"><h3>{head}</h3>{body}</div>' for cid, head, body in cases)
    notes_html = ''.join(f'<li id="{nid}">{txt}</li>' for nid, txt in notes)
    case_toc = '<li><a href="#case-studies">Case studies</a></li>' if cases else ''
    intro = f'<p class="cintro">{cases_intro}</p>' if cases_intro else ''
    case_sec = (f'<section id="case-studies" aria-label="Case studies"><h2>Case studies</h2>{intro}{cases_html}</section>'
                if cases else '')
    page = f'''<title>{name} Review</title>
<div class="wrap">
  <header class="mast">
    <h1>{name}</h1>
    <dl class="meta">
      <div><dt>Reviewed</dt><dd>{reviewed}</dd></div>
      <div><dt>Benchmark creator</dt><dd>{creator}</dd></div>
      <div><dt>Version reviewed</dt><dd>{version}</dd></div>
      <div><dt>Verdict</dt><dd><span class="verdict">{verdict}</span></dd></div>
    </dl>
  </header>
  <div class="layout">
    <nav class="toc" aria-label="Contents">
      <ol>
        <li><a href="#summary">Summary</a></li>
        {case_toc}
        <li><a href="#errors">{errors_heading}</a></li>
        <li><a href="#disclaimer">Disclaimer</a></li>
        <li><a href="#notes">Notes</a></li>
      </ol>
    </nav>
    <main>
      <section id="summary" aria-label="Summary">
        <h2 class="vh">Summary</h2>
        <p class="lede">{lede}</p>
        <h3 class="sumh">What we found</h3>
        <ul class="found">{found_html}</ul>
      </section>
      {case_sec}
      <section id="errors" aria-label="{errors_heading}">
        <div class="errhead"><h2>{errors_heading}</h2><button type="button" class="showall" aria-pressed="false">Show all sources</button></div>
        {errors_html(errors, "issue" if errors_heading == "All issues" else "error")}
      </section>
      <section id="disclaimer" aria-label="Disclaimer">
        <h2>Disclaimer</h2>
        <p>{disclaimer}</p>
      </section>
      <section id="notes" aria-label="Notes">
        <h2>Notes</h2>
        <ol class="notes" style="list-style-type: lower-alpha">{notes_html}</ol>
        <h3>Cite</h3>
        <div class="cite">Open Benchmark Review (2026), "{name}: Benchmark Review". Reviewed {reviewed}. {REPO.replace("https://", "")}</div>
      </section>
{SCRIPT}
{extra_script}
    </main>
  </div>
</div>
'''
    out = os.path.join(REVIEWS, f'{slug}.html')
    open(out, 'w', encoding='utf-8').write(page)
    return out
