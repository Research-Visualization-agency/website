#!/usr/bin/env python3
"""Generate the "Our work" page (work.html) and one static page per project (work/<id>.html).

Source of truth: data/cases.json (projects) and the header, menu and footer markup in index.html.
Re-run after editing either:  python3 build.py
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
src = (ROOT / "index.html").read_text(encoding="utf-8")

data = json.loads((ROOT / "data" / "cases.json").read_text(encoding="utf-8"))
GROUPS = {g["id"]: g for g in data["groups"]}
CASES = data["cases"]
SITE = "hice. — Research & information design studio"


def h(v):
    return escape("" if v is None else str(v), quote=True)


def relink(fragment, prefix):
    """Home-page anchors and sibling pages, as seen from a page `prefix` away from the site root."""
    fragment = re.sub(r'href="#', f'href="{prefix}index.html#', fragment)
    return re.sub(r'href="work\.html', f'href="{prefix}work.html', fragment)


# --- shared header / menu / footer, taken from index.html ---------------------------
header_raw = re.search(r'<header class="header".*?</header>', src, re.S).group(0)
menu_raw = re.search(r'<div class="menu" id="menu".*?\n</div>\n', src, re.S).group(0)
footer_raw = re.sub(r'<form class="news".*?</form>', "", re.search(r'<footer class="footer".*?</footer>', src, re.S).group(0), flags=re.S)  # newsletter JS lives on the home page

ARROW_L = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12H4M10 6l-6 6 6 6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
EXT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M7 17L17 7M8 7h9v9"/></svg>'


def art_svg(kind, label):
    return f'<svg data-art="{h(kind)}" viewBox="0 0 640 360" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{h(label)}"></svg>'


def ht(v):
    """Escaped text with the brand name set as "hice." (full stop in the logo colour)."""
    return re.sub(r"\bhice\b", 'hice<span class="brand-dot">.</span>', h(v))


def full(duo, im):
    return ' class="full"' if duo and im[1] < 0.6 else ""


def render_body(c):
    g = GROUPS[c["g"]]
    facts = f'<dl class="dlg-facts"><dt>Client</dt><dd>{h(c["client"])}</dd>'
    if c.get("year"):
        facts += f'<dt>Year</dt><dd>{h(c["year"])}</dd>'
    facts += f'<dt>Direction</dt><dd>{h(g["title"])}</dd><dt>Format</dt><dd>{h(c["badge"])}</dd>'
    if c.get("tags"):
        facts += "<dt>Tags</dt><dd>" + " · ".join(h(t) for t in c["tags"]) + "</dd>"
    facts += "</dl>"
    out = (f'<div class="dlg-head" data-rv><div><p class="label"><b>{h(c["badge"])}</b></p>'
           f'<h1 id="caseTitle">{h(c["title"])}</h1><p class="lead">{h(c["sum"])}</p></div>{facts}</div>')
    if c.get("stats"):
        out += '<ul class="stats">' + "".join(f"<li><b>{h(s[0])}</b><span>{h(s[1])}</span></li>" for s in c["stats"]) + "</ul>"

    txt = ""
    for sec in c.get("sections", []):
        body = "".join(f"<p>{ht(p)}</p>" for p in (sec[1] if len(sec) > 1 else []) or [])
        if len(sec) > 2 and sec[2]:
            tag = "ol" if len(sec) > 3 and sec[3] == "ol" else "ul"
            body += f"<{tag}>" + "".join(f"<li>{ht(li)}</li>" for li in sec[2]) + f"</{tag}>"
        if body:
            txt += f"<div><h3>{h(sec[0])}</h3>{body}</div>"
    if c.get("quote"):
        txt += f'<blockquote class="quote"><p>“{h(c["quote"][0])}”</p><cite>— {h(c["quote"][1])}</cite></blockquote>'
    res = [(l[0], l[1]) for l in c.get("web", [])]
    res += [(l[0] + " (interactive)", l[1]) for l in c.get("links", [])]
    res += [(l[0], l[1]) for l in c.get("files", [])]
    if res:
        title = "Live sites &amp; materials" if c.get("web") else "Materials"
        txt += f'<div><h3>{title}</h3><ul class="res-links">' + "".join(
            f'<li><a href="{h(u)}" target="_blank" rel="noopener">{h(t)} {EXT}</a></li>' for t, u in res) + "</ul></div>"

    imgs = c.get("img", [])
    duo = len(imgs) > 3 and all(i[1] < 1.3 for i in imgs)
    if imgs:
        gal = "".join(
            f'<figure{full(duo, im)}><img src="../{h(im[0])}" '
            f'alt="{h(c["title"])} — image {i + 1} of {len(imgs)}" loading="lazy" decoding="async" '
            f'style="aspect-ratio:{im[1]}"></figure>' for i, im in enumerate(imgs))
    else:
        gal = f'<figure class="art">{art_svg(c.get("art", "bars"), c["title"] + " — illustration")}</figure>'
    out += f'<div class="dlg-body" data-rv style="--rd:1"><div class="dlg-text">{txt}</div><div class="gallery{" duo" if duo else ""}">{gal}</div></div>'
    return out


# fall back to the illustration when a gallery image is missing
PAGE_JS = """<script src="../assets/art.js"></script>
<script>
(function () {
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  document.documentElement.classList.add("js");
  var NS = "http://www.w3.org/2000/svg";
  function draw(root) { $$("svg[data-art]", root).forEach(function (s) { if (!s.childNodes.length) window.HICE_ART[s.getAttribute("data-art")](s); }); }
  draw(document);
  var art = document.body.getAttribute("data-art") || "bars";
  $$(".gallery img").forEach(function (img, i) {
    img.addEventListener("error", function () {
      if (i !== 0) { img.parentNode.remove(); return; }
      var f = img.parentNode; f.className = "art";
      f.innerHTML = '<svg data-art="' + art + '" viewBox="0 0 640 360" preserveAspectRatio="xMidYMid slice" role="img" aria-label="' + img.alt.replace(/"/g, "") + '"></svg>';
      draw(f);
    });
  });
  var menu = document.getElementById("menu"), btn = document.getElementById("menuBtn");
  function setMenu(o) { menu.hidden = !o; btn.setAttribute("aria-expanded", String(o)); document.body.classList.toggle("menu-open", o); }
  btn.addEventListener("click", function () { setMenu(true); });
  document.getElementById("menuClose").addEventListener("click", function () { setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  var header = document.getElementById("header"), lastY = window.scrollY;
  window.addEventListener("scroll", function () { var y = window.scrollY; header.classList.toggle("is-hidden", y > lastY && y > 160); lastY = y; }, { passive: true });

  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var vh = window.innerHeight;
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("rv-in"); en.target.classList.remove("rv-armed"); io.unobserve(en.target); } }); }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    $$("[data-rv]").forEach(function (n) { if (n.getBoundingClientRect().top > vh) { n.classList.add("rv-armed"); io.observe(n); } });
  }
})();
</script>"""


def page(c, i):
    g = GROUPS[c["g"]]
    same = [x for x in CASES if x["g"] == c["g"]]
    prev, nxt = CASES[(i - 1) % len(CASES)], CASES[(i + 1) % len(CASES)]
    title = f'{c["title"]} — {SITE}'
    nav = (f'<nav class="case-pager" aria-label="Projects">'
           f'<a href="{h(prev["id"])}.html" rel="prev">{ARROW_L}<span><small>Previous</small>{h(prev["title"])}</span></a>'
           f'<a href="{h(nxt["id"])}.html" rel="next"><span><small>Next</small>{h(nxt["title"])}</span>{ARROW_R}</a></nav>')
    crumb = (f'<p class="label case-crumb"><a href="../work.html">Our work</a> / '
             f'<a href="../work.html#dir-{h(g["id"])}">{h(g["title"])}</a> / <b>{h(c["title"])}</b></p>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{h(c["sum"])}">
<title>{h(title)}</title>
<link rel="stylesheet" href="../assets/site.css">
<script>document.documentElement.classList.add("js")</script>
<style>
.case-page {{ padding: clamp(112px, 14vw, 160px) 0 var(--space-64, 64px); }}
.case-crumb {{ margin: 0 0 var(--space-24, 24px); }}
.case-crumb a {{ text-decoration: underline; text-underline-offset: 4px; text-decoration-color: var(--line-strong); }}
.case-crumb a:hover {{ color: var(--accent-electric); }}
.case-page .dlg-head h1 {{ margin: var(--space-16, 16px) 0 0; font: 400 clamp(36px, 4.6vw, 64px)/1.06 var(--font-display); letter-spacing: -.02em; text-wrap: balance; }}
.case-pager {{ display: grid; grid-template-columns: 1fr 1fr; gap: var(--gutter, 24px); margin-top: var(--space-64, 64px); padding-top: var(--space-32, 32px); border-top: 1px solid var(--line); }}
.case-pager a {{ display: flex; align-items: center; gap: 14px; padding: 16px 0; }}
.case-pager a:last-child {{ justify-content: flex-end; text-align: right; }}
.case-pager svg {{ width: 22px; height: 22px; flex: none; }}
.case-pager small {{ display: block; font: 600 11px/1.6 var(--font-sans); letter-spacing: .08em; text-transform: uppercase; color: var(--ink-muted); }}
.case-pager a:hover {{ color: var(--accent-electric); }}
@media (max-width: 600px) {{ .case-pager {{ grid-template-columns: 1fr; }} .case-pager a:last-child {{ justify-content: flex-start; text-align: left; flex-direction: row-reverse; }} }}
</style>
</head>
<body data-art="{h(c.get("art", "bars"))}">
<a class="skip" href="#main">Skip to content</a>

{relink(header_raw, "../")}

{relink(menu_raw, "../")}
<main id="main" class="case-page">
  <div class="wrap">
    {crumb}
    {render_body(c)}
    {nav}
  </div>
</main>

{relink(footer_raw, "../")}
{PAGE_JS}
<script src="../assets/logo.js"></script>
</body>
</html>
"""


ARROW_UR = EXT.replace('width="14" height="14" ', "")


def media(c):
    art = c.get("art", "bars")
    if c.get("cover"):
        inner = f'<img src="{h(c["cover"])}" alt="{h(c["title"])} — preview" loading="lazy" decoding="async" data-fallback="{h(art)}">'
    else:
        inner = art_svg(art, c["title"] + " — illustration")
    return f'<div class="card-media"><span class="badge">{h(c["badge"])}</span>{inner}</div>'


def card_meta(c, with_tags):
    tags = ""
    if with_tags and c.get("tags"):
        tags = '<ul class="tags" aria-label="Tags">' + "".join(f"<li>{h(t)}</li>" for t in c["tags"]) + "</ul>"
    year = f'<span class="year">{h(c["year"])}</span>' if c.get("year") else ""
    return f'<div class="card-meta"><span class="client">{h(c["client"])}</span>{year}{tags}</div>'


def card(c, n=0):
    title = f'<h3 class="card-title">{h(c["title"])} {ARROW_UR}</h3>'
    href = f'work/{h(c["id"])}.html'
    if c.get("featured"):
        tags = "".join(f"<li>{h(t)}</li>" for t in c.get("tags", []))
        return (f'<a class="card wide" href="{href}" data-rv style="--rd:{n % 3}">{media(c)}<div class="card-body">{card_meta(c, False)}{title}'
                f'<p class="card-sum">{h(c["sum"])}</p><ul class="card-meta tags" aria-label="Tags">{tags}</ul></div></a>')
    return f'<a class="card" href="{href}" data-rv style="--rd:{n % 3}">{media(c)}{card_meta(c, True)}{title}<p class="card-sum">{h(c["sum"])}</p></a>'


WORK_JS = """<script src="assets/art.js"></script>
<script>
(function () {
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  document.documentElement.classList.add("js");
  function draw(root) { $$("svg[data-art]", root).forEach(function (s) { if (!s.childNodes.length) window.HICE_ART[s.getAttribute("data-art")](s); }); }
  draw(document);
  $$("img[data-fallback]").forEach(function (img) {
    img.addEventListener("error", function () {
      var w = document.createElement("div");
      w.innerHTML = '<svg data-art="' + img.getAttribute("data-fallback") + '" viewBox="0 0 640 360" preserveAspectRatio="xMidYMid slice" role="img" aria-label="' + img.alt.replace(/"/g, "") + '"></svg>';
      var sv = w.firstChild; img.replaceWith(sv); draw(sv.parentNode);
    });
  });
  var filters = document.getElementById("caseFilters"), groups = $$(".case-group");
  function setFilter(id) {
    $$("button", filters).forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-f") === id)); });
    groups.forEach(function (g) { g.hidden = !(id === "all" || g.getAttribute("data-group") === id); });
  }
  filters.addEventListener("click", function (e) { var b = e.target.closest("button[data-f]"); if (b) setFilter(b.getAttribute("data-f")); });
  function fromHash() {
    var m = location.hash.match(/^#dir-(.+)$/);
    if (m && groups.some(function (g) { return g.getAttribute("data-group") === m[1]; })) setFilter(m[1]);
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();
  var menu = document.getElementById("menu"), btn = document.getElementById("menuBtn");
  function setMenu(o) { menu.hidden = !o; btn.setAttribute("aria-expanded", String(o)); document.body.classList.toggle("menu-open", o); }
  btn.addEventListener("click", function () { setMenu(true); });
  document.getElementById("menuClose").addEventListener("click", function () { setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  var header = document.getElementById("header"), lastY = window.scrollY;
  window.addEventListener("scroll", function () { var y = window.scrollY; header.classList.toggle("is-hidden", y > lastY && y > 160); lastY = y; }, { passive: true });

  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var vh = window.innerHeight;
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("rv-in"); en.target.classList.remove("rv-armed"); io.unobserve(en.target); } }); }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    $$("[data-rv]").forEach(function (n) { if (n.getBoundingClientRect().top > vh) { n.classList.add("rv-armed"); io.observe(n); } });
  }
})();
</script>"""


def work_page():
    groups = []
    for gi, g in enumerate(data["groups"]):
        lst = [c for c in CASES if c["g"] == g["id"]]
        label = f'<b>0{gi + 1}</b> · {len(lst)} {"project" if len(lst) == 1 else "projects"}'
        groups.append(
            f'<div class="case-group" data-group="{h(g["id"])}" id="dir-{h(g["id"])}"><div class="case-group-head" data-rv>'
            f'<p class="label">{label}</p><h2>{h(g["title"])}</h2><p>{h(g["desc"])}</p></div>'
            f'<div class="cards cases{" compact" if g["id"] == "ai" else ""}">{"".join(card(c, n) for n, c in enumerate(lst))}</div></div>')
    entries = [("all", "All", len(CASES))] + [(g["id"], g["title"], sum(1 for c in CASES if c["g"] == g["id"])) for g in data["groups"]]
    filters = "".join(
        f'<li><button type="button" data-f="{h(fid)}" aria-pressed="{"true" if k == 0 else "false"}">{h(name)} <span>{n}</span></button></li>'
        for k, (fid, name, n) in enumerate(entries))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Selected research, dashboard, presentation, data-visualisation and brand projects by hice.">
<title>Our work — {h(SITE)}</title>
<link rel="stylesheet" href="assets/site.css">
<script>document.documentElement.classList.add("js")</script>
<style>.work-page {{ padding: clamp(112px, 14vw, 160px) 0 var(--space-64, 64px); }}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

{relink(header_raw, "")}

{relink(menu_raw, "")}
<main id="main" class="work-page">
  <section id="work" aria-labelledby="workTitle">
    <div class="wrap">
      <div class="sec-head" data-rv><p class="label">Our work</p><p class="label action">{len(CASES)} projects · {len(data["groups"])} directions</p></div>
      <div class="grid">
        <div class="work-intro" data-rv><h1 class="h2" id="workTitle">Evidence, made visible. Built for the people who decide.</h1></div>
        <p class="work-note" data-rv>Case studies across five directions: from live BI systems and executive decks to maps, brand platforms and AI-built tools.</p>
        <ul class="filters" id="caseFilters" aria-label="Filter projects by direction" data-rv>{filters}</ul>
        <div class="case-groups" id="caseGroups">{"".join(groups)}</div>
      </div>
    </div>
  </section>
</main>

{relink(footer_raw, "")}
{WORK_JS}
<script src="assets/logo.js"></script>
</body>
</html>
"""


(ROOT / "work.html").write_text(work_page(), encoding="utf-8")


out_dir = ROOT / "work"
out_dir.mkdir(exist_ok=True)
for i, c in enumerate(CASES):
    (out_dir / f'{c["id"]}.html').write_text(page(c, i), encoding="utf-8")
print(f"built work.html + {len(CASES)} project pages")
