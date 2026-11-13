#!/usr/bin/env python3
"""Static site builder for the Aetheria Funeral Homes redesign.

Reads /workspace/obituaries.json and /workspace/content_pages.json and renders
all HTML pages into this directory (the folder containing build.py).
Hand-authored assets live in ./assets (tokens.css, site.css, site.js, obits.js).

    python3 build.py            # regenerates every page
"""
import html
import json
import os
import re
import shutil
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)  # /workspace
OBITS_JSON = os.path.join(SRC, "obituaries.json")
PAGES_JSON = os.path.join(SRC, "content_pages.json")
YEAR = datetime.now().year

esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)

# --------------------------------------------------------------------------
# Contact / locations (verbatim from brief)
# --------------------------------------------------------------------------
PHONE_MAIN = "1 (800) 990-0890"
PHONE_TEXT = "1 (323) 987-5025"
PHONE_FAX = "1 (800) 604-4590"
EMAIL = "Counseling@funeralcaregroup.com"
SITE_NAME = "Aetheria Funeral Homes"
LEGACY_NAME = "Continental Funeral Home"  # brand name used in the source content JSON

LOCATIONS = [
    dict(key="east-los-angeles", name="East Los Angeles", lic="FD 1915",
         street="5353 East Beverly Blvd.", city="East Los Angeles, CA 90022", phone="1 (800) 990-0890"),
    dict(key="santa-ana", name="Santa Ana", lic="FD 2079",
         street="2525 N Grand Ave, Suite K", city="Santa Ana, CA 92705", phone="1-714-771-1238"),
    dict(key="ontario", name="Ontario", lic="FD 2111",
         street="2442 S. Euclid Ave", city="Ontario, CA 91762", phone="1-909-509-5909"),
    dict(key="hawthorne", name="Hawthorne", lic="FD 2022",
         street="13806 Hawthorne Blvd", city="Hawthorne, CA 90250", phone="1-424-888-7919"),
    dict(key="oakland", name="Oakland", lic="FD 837",
         street="5500 Foothill Blvd", city="Oakland, CA 94605", phone="1-510-261-1105"),
]
LOC_BY_LIC = {l["lic"]: l for l in LOCATIONS}


def tel(num):
    digits = re.sub(r"\D", "", num)
    return "tel:+" + digits


def maps_url(loc):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(
        f"{SITE_NAME} {loc['street']} {loc['city']}")


# --------------------------------------------------------------------------
# Icons (inline SVG, stroke-based)
# --------------------------------------------------------------------------
ICON_PATHS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5M11 18l-6-6 6-6"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "flower": '<circle cx="12" cy="12" r="3"/><path d="M12 16.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 1 1 12 7.5a4.5 4.5 0 1 1 4.5 4.5 4.5 4.5 0 1 1-4.5 4.5"/><path d="M12 7.5V9M7.5 12H9M16.5 12H15M12 16.5V15"/>',
    "tree": '<path d="M12 22v-6"/><path d="M17 8A5 5 0 0 0 7 8a4 4 0 0 0-1 7.87h12A4 4 0 0 0 17 8Z"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "flag": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><path d="M4 22v-7"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "feather": '<path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/><path d="M16 8 2 22M17.5 15H9"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "star": '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "box": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36z"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.59 13.51 6.83 3.98M15.41 6.51l-6.82 3.98"/>',
    "hand": '<path d="M11 14h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 16"/><path d="m7 20 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9"/><path d="m2 15 6 6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            f'{ICON_PATHS[name]}</svg>')


# --------------------------------------------------------------------------
# Content pages → sections
# --------------------------------------------------------------------------
def load_pages():
    with open(PAGES_JSON, encoding="utf-8") as f:
        pages = json.load(f)
    return {p["path"]: p for p in pages}


def is_heading(block):
    if "\n" not in block and len(block) < 60 and block.rstrip().endswith("..."):
        return True
    return ("\n" not in block and len(block) < 95 and not block.rstrip().endswith((".", ":", "?")) ) or (
        "\n" not in block and len(block) < 70 and block.rstrip().endswith("?"))


def sections(page):
    """Split page main_text into an ordered list of (heading, [paragraphs])."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", page.get("main_text") or "") if b.strip()]
    out = [("", [])]
    for b in blocks:
        lines = b.split("\n")
        if len(lines) > 1 and len(lines[0]) < 60 and not lines[0].endswith(".") and len(" ".join(lines[1:])) > 80:
            out.append((lines[0].strip(), [" ".join(l.strip() for l in lines[1:])]))
        elif is_heading(b):
            out.append((b, []))
        else:
            out[-1][1].append(" ".join(l.strip() for l in lines))
    return out


class Content:
    def __init__(self):
        self.pages = load_pages()
        self._secs = {p: sections(v) for p, v in self.pages.items()}

    def sec(self, path, heading):
        for h, paras in self._secs[path]:
            if h.lower().strip() == heading.lower().strip():
                if not paras:
                    raise KeyError(f"empty section {heading!r} in {path}")
                return paras
        raise KeyError(f"heading {heading!r} not found in {path}")

    def first(self, path, heading):
        return self.sec(path, heading)[0]

    def items_after(self, path, heading):
        """Short list items that follow a heading (parsed as headings themselves)."""
        secs = self._secs[path]
        for i, (h, paras) in enumerate(secs):
            if h.lower() == heading.lower():
                items = list(paras)
                j = i + 1
                while j < len(secs) and not secs[j][1]:
                    items.append(secs[j][0]); j += 1
                if j < len(secs):
                    items.append(secs[j][0])
                return items
        raise KeyError(heading)


# --------------------------------------------------------------------------
# Obituaries
# --------------------------------------------------------------------------
def parse_date(s):
    try:
        return datetime.strptime((s or "").strip(), "%B %d, %Y")
    except ValueError:
        return None


def initials(name):
    words = [w for w in re.split(r"\s+", name or "") if w and w[0].isalpha()]
    if not words:
        return "CF"
    if len(words) == 1:
        return words[0][0].upper()
    # Use first given name + first surname (Hispanic naming: 2nd-to-last word is paternal surname
    # when there are 4+ words); keep simple: first + last word.
    return (words[0][0] + words[-1][0]).upper()


def load_obits():
    with open(OBITS_JSON, encoding="utf-8") as f:
        raw = json.load(f)
    obits = []
    for r in raw:
        o = dict(r)
        o["id"] = str(r.get("obituary_id") or "").strip()
        o["name"] = (r.get("full_name") or "").strip() or "Name unavailable"
        o["is_stock"] = str(r.get("is_stock_image", "")).strip().lower() == "true"
        o["photo"] = (r.get("image_url") or "").strip()
        o["has_photo"] = bool(o["photo"]) and not o["is_stock"]
        o["is_placeholder"] = str(r.get("obituary_is_placeholder", "")).strip().lower() == "true"
        text = (r.get("obituary_text") or "").strip()
        if "not available at this time" in text.lower():
            o["is_placeholder"] = True
        o["text"] = "" if o["is_placeholder"] else text
        o["birth"] = parse_date(r.get("birth_date"))
        o["death"] = parse_date(r.get("death_date"))
        o["birth_str"] = (r.get("birth_date") or "").strip()
        o["death_str"] = (r.get("death_date") or "").strip()
        age = str(r.get("age") or "").strip()
        o["age"] = age if age.isdigit() else ""
        sj = r.get("services_json")
        events = []
        if isinstance(sj, str) and sj.strip():
            try:
                events = json.loads(sj)
            except json.JSONDecodeError:
                events = []
        elif isinstance(sj, list):
            events = sj
        o["events"] = [e for e in events if isinstance(e, dict)]
        o["notes"] = (r.get("service_notes") or "").strip()
        fh = (r.get("funeral_home") or "").strip()
        m = re.search(r"FD\s*(\d+)", fh)
        o["loc"] = LOC_BY_LIC.get(f"FD {m.group(1)}") if m else None
        pub = r.get("date_published") or ""
        o["pub_key"] = re.sub(r"\D", "", pub)[:12] or "0"
        o["death_key"] = o["death"].strftime("%Y%m%d") if o["death"] else "0"
        o["years"] = " – ".join(
            x for x in [o["birth"].strftime("%Y") if o["birth"] else "", o["death"].strftime("%Y") if o["death"] else ""] if x)
        o["href"] = f"obituary/{o['id']}.html"
        obits.append(o)
    obits.sort(key=lambda o: (o["death_key"], o["pub_key"]), reverse=True)
    return obits


def monogram(o_or_name, variant=None, dark=False):
    name = o_or_name if isinstance(o_or_name, str) else o_or_name["name"]
    if variant is None and not isinstance(o_or_name, str):
        variant = int(re.sub(r"\D", "", o_or_name["id"]) or 0) % 3
    cls = "monogram" + (" monogram--dark" if dark else (f" monogram--v{variant}" if variant else ""))
    return f'<div class="{cls}" aria-hidden="true"><span>{esc(initials(name))}</span></div>'


def portrait_inner(o, lazy=True):
    """Monogram base layer with photo overlaid; if photo fails it is removed."""
    mono = monogram(o)
    if not o["has_photo"]:
        return mono
    lz = ' loading="lazy" decoding="async"' if lazy else ""
    return (mono + f'<img src="{esc(o["photo"])}" alt="Photo of {esc(o["name"])}"{lz} '
            f'referrerpolicy="no-referrer" onerror="this.remove()">')


def obit_card(o, root="", lazy=True):
    loc = o["loc"]
    tag = f'<span class="pill-tag">{icon("pin")}{esc(loc["name"])}</span>' if loc else ""
    dates = esc(o["years"]) if o["years"] else "&nbsp;"
    age = f'Age {esc(o["age"])}' if o["age"] else ("Obituary" if o["text"] else "Obituary pending")
    alt_note = "" if o["has_photo"] else f'<span class="sr-only">Monogram for {esc(o["name"])}</span>'
    return f'''<a class="card obit-card" href="{root}{o["href"]}" data-name="{esc(o["name"])}" data-death="{o["death_key"]}" data-pub="{o["pub_key"]}" data-loc="{loc["key"] if loc else "other"}">
  <div class="obit-card__media">{tag}{portrait_inner(o, lazy)}{alt_note}</div>
  <div class="obit-card__body">
    <h3 class="obit-card__name">{esc(o["name"])}</h3>
    <div class="obit-card__dates">{dates}</div>
    <div class="obit-card__foot"><span>{age}</span><span class="go"><span>View tribute</span>{icon("arrow")}</span></div>
  </div>
</a>'''


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
NAV = [("index.html", "Home"), ("obituaries.html", "Obituaries"), ("services.html", "Services"),
       ("about.html", "About"), ("contact.html", "Contact")]


def brand(root, light=False):
    logo = "aetheria-logo-light.png" if light else "aetheria-logo.png"
    return f'''<a class="brand" href="{root}index.html" aria-label="{SITE_NAME} — home">
  <img class="brand__logo" src="{root}assets/img/{logo}" alt="{SITE_NAME}" width="1313" height="280">
</a>'''


def header(root, active):
    items = "".join(
        f'<li><a class="nav__link" href="{root}{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a></li>'
        for href, label in NAV)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar"><div class="container">
  <div class="topbar__items"><span><span class="live-dot" aria-hidden="true"></span>Available 24 hours a day, 7 days a week</span><span class="hide-sm">Text <a href="sms:+13239875025">{PHONE_TEXT}</a> (no calls)</span></div>
  <div class="topbar__items"><a href="mailto:{EMAIL}">{EMAIL}</a></div>
</div></div>
<header class="site-header">
  <div class="container nav-wrap">
    {brand(root)}
    <nav class="nav" aria-label="Primary">
      <ul>{items}</ul>
      <div class="nav__cta">
        <a class="btn btn--ghost btn--sm" href="{tel(PHONE_MAIN)}">{icon("phone")}Call 24/7</a>
        <a class="btn btn--primary btn--sm" href="{root}contact.html"><span class="lbl-long">Plan a Service</span><span class="lbl-short">Plan</span></a>
      </div>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-label="Open menu">{icon("menu")}</button>
    </nav>
  </div>
</header>'''


def footer(root):
    locs = "".join(f'''<div><h3>{esc(l["name"])}</h3><address>{esc(l["street"])}<br>{esc(l["city"])}</address>
<a class="ph" href="{tel(l["phone"])}">{esc(l["phone"])}</a></div>''' for l in LOCATIONS)
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-about">
        {brand(root, light=True)}
        <p>Dedicated to providing services with integrity, respect, professionalism, care, and the compassion that defines us.</p>
        <div class="footer-contact">
          <div><small>24/7</small><a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a></div>
          <div><small>Text</small><span><a href="sms:+13239875025">{PHONE_TEXT}</a> · no calls, please</span></div>
          <div><small>Fax</small><span>{PHONE_FAX}</span></div>
          <div><small>Email</small><a href="mailto:{EMAIL}">{EMAIL}</a></div>
        </div>
      </div>
      <div>
        <div class="footer-locs">{locs}
          <div class="footer-hours"><h3>Hours</h3>We are available to serve you 24 hours a day, 7 days a week — call us any time, day or night.</div>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {YEAR} {SITE_NAME}. All rights reserved.</span>
      <nav aria-label="Footer">{"".join(f'<a href="{root}{h}">{l}</a>' for h, l in NAV)}</nav>
    </div>
  </div>
</footer>'''


def page(title, desc, body, root="", active="", scripts=()):
    js = "".join(f'<script src="{root}assets/{s}" defer></script>' for s in ("site.js",) + tuple(scripts))
    body = body.replace(LEGACY_NAME, SITE_NAME)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#4a2c59">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&amp;family=Outfit:wght@300;400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="{root}assets/tokens.css">
<link rel="stylesheet" href="{root}assets/site.css">
{js}
</head>
<body>
{header(root, active)}
<main id="main">
{body}
</main>
{footer(root)}
</body>
</html>
'''


def loc_card(l, cls="card loc-card", with_btn=False):
    btn = (f'<a class="btn btn--secondary btn--sm" href="{esc(maps_url(l))}" target="_blank" rel="noopener">'
           f'{icon("compass")}Get directions</a>') if with_btn else ""
    return f'''<article class="{cls}">
  <span class="lic">{esc(l["lic"])}</span>
  <h3>{esc(l["name"])}</h3>
  <address>{esc(l["street"])}<br>{esc(l["city"])}</address>
  <a class="tel" href="{tel(l["phone"])}">{icon("phone")}{esc(l["phone"])}</a>
  {btn}
</article>'''


def cta_band(root, eyebrow="We are here for you", heading="Whenever you need us, <em>day or night</em>",
             lead="You are welcome to call us any time of the day, any day of the week, for immediate assistance. Or, visit one of our funeral homes in person at your convenience."):
    return f'''<section class="section section--tight" aria-labelledby="cta-h">
  <div class="container">
    <div class="cta-band">
      <div class="cta-band__grid">
        <div>
          <span class="eyebrow">{eyebrow}</span>
          <h2 id="cta-h">{heading}</h2>
          <p class="lead">{lead}</p>
          <div class="btn-row" style="margin-top:2rem">
            <a class="btn btn--light" href="{tel(PHONE_MAIN)}">{icon("phone")}Call {PHONE_MAIN}</a>
            <a class="btn btn--outline-light" href="{root}contact.html">Plan a Service {icon("arrow")}</a>
          </div>
        </div>
        <div class="contact-tiles">
          <div class="contact-tile"><small>Call 24/7</small><a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a></div>
          <div class="contact-tile"><small>Text</small><a href="sms:+13239875025">{PHONE_TEXT}</a><em>No calls, please</em></div>
          <div class="contact-tile"><small>Fax</small><span>{PHONE_FAX}</span><em>No calls, please</em></div>
          <div class="contact-tile"><small>Email</small><a href="mailto:{EMAIL}">{EMAIL}</a></div>
        </div>
      </div>
    </div>
  </div>
</section>'''


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def service_summaries(C):
    def trim(s, n=210):
        if len(s) <= n:
            return s
        cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
        return cut + "…"
    return [
        ("Funeral Services", "leaf", "services.html#funeral",
         trim(C.first("/", "Burial Options"))),
        ("Cremation", "flame", "services.html#cremation",
         trim(C.first("/", "Cremation Options"))),
        ("Veterans Services", "flag", "services.html#veterans",
         trim(C.sec("/veterans", "VETERANS")[0])),
        ("Pre-Planning", "calendar", "services.html#pre-planning",
         trim(" ".join(C.sec("/pre-arrangements", "Pre-Arrangements")[:1]))),
        ("Grief Support", "heart", "services.html#grief",
         C.first("/grief-support", "A year of daily grief support").split(" Enter your email")[0] + " We also share helpful grief support resources for every stage of healing."),
    ]


def build_index(C, obits):
    svc = "".join(f'''<a class="card svc-card" href="{href}">
  <span class="icon-badge">{icon(ic)}</span>
  <h3>{esc(t)}</h3>
  <p>{esc(d)}</p>
  <span class="more">Learn more {icon("arrow")}</span>
</a>''' for t, ic, href, d in service_summaries(C))
    recent = [o for o in obits if o["has_photo"]][:8]
    cards = "".join(obit_card(o, lazy=False) for o in recent)
    locs = "".join(loc_card(l) for l in LOCATIONS)
    welcome = C.sec("/", "Welcome to Continental Funeral Home FD 1915")[0]
    loss = C.first("/", "If you suffered a loss...")
    loss_short = loss.split(". This form")[0] + "."
    body = f'''
<section class="hero" aria-labelledby="hero-h">
  <div class="container hero__grid">
    <div>
      <span class="eyebrow fade-up">{SITE_NAME}</span>
      <h1 id="hero-h" class="fade-up d1">Honoring lives, <em>with dignity</em> and care</h1>
      <p class="lead fade-up d2">{esc(welcome.split(". At Continental")[0] + ".")}</p>
      <div class="btn-row fade-up d3">
        <a class="btn btn--primary" href="contact.html">Plan a Service {icon("arrow")}</a>
        <a class="btn btn--secondary" href="obituaries.html">{icon("search")}Find an Obituary</a>
      </div>
      <div class="hero__meta fade-up d3">
        <div><strong>25+</strong><span>Years of experience</span></div>
        <div><strong>5</strong><span>California locations</span></div>
        <div><strong>24/7</strong><span>Compassionate support</span></div>
      </div>
    </div>
    <aside class="glass care-card fade-up d2" aria-labelledby="care-h">
      <span class="eyebrow">If you suffered a loss</span>
      <h2 id="care-h">We are ready to serve you</h2>
      <p>{esc(loss_short)}</p>
      <ul class="care-list">
        <li><span class="ic">{icon("phone")}</span><div><small>Call 24/7</small><a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a></div></li>
        <li><span class="ic">{icon("message")}</span><div><small>Text · no calls</small><a href="sms:+13239875025">{PHONE_TEXT}</a></div></li>
        <li><span class="ic">{icon("mail")}</span><div><small>Email</small><a href="mailto:{EMAIL}">{EMAIL}</a></div></li>
      </ul>
      <a class="btn btn--glow" href="contact.html" style="width:100%">At-need contact {icon("arrow")}</a>
    </aside>
  </div>
</section>

<section class="section section--tight" aria-labelledby="svc-h">
  <div class="container">
    <div class="section-head section-head--split">
      <div><span class="eyebrow">Our Services</span><h2 id="svc-h">A meaningful farewell, <em>your way</em></h2>
      <p class="lead">Every life is unique. We offer a full spectrum of funeral services and products to honor the memory of your loved one.</p></div>
      <a class="btn btn--ghost" href="services.html">All services {icon("arrow")}</a>
    </div>
    <div class="svc-grid">{svc}</div>
  </div>
</section>

<section class="section section--wash" aria-labelledby="obit-h">
  <div class="container">
    <div class="section-head section-head--split">
      <div><span class="eyebrow">In Loving Memory</span><h2 id="obit-h">Recent obituaries</h2>
      <p class="lead">Remember those we have recently had the honor of serving, and leave a memory for their families.</p></div>
      <a class="btn btn--secondary" href="obituaries.html">View all obituaries {icon("arrow")}</a>
    </div>
    <div class="obit-grid">{cards}</div>
  </div>
</section>

<section class="section section--tight" aria-labelledby="loc-h">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow eyebrow--center">Our Locations</span>
      <h2 id="loc-h">Close to the families <em>we serve</em></h2>
      <p class="lead">Visit one of our funeral homes in person at your convenience, or call any time.</p>
    </div>
    <div class="loc-grid">{locs}</div>
  </div>
</section>
{cta_band("")}
'''
    return page("Aetheria Funeral Homes — Honoring lives with dignity and care",
                "Aetheria Funeral Homes offers funeral, cremation, veterans and pre-planning services across five California locations. Available 24/7 at 1 (800) 990-0890.",
                body, "", "index.html")


def build_obituaries(obits):
    cards = "\n".join(obit_card(o) for o in obits)
    counts = {l["key"]: sum(1 for o in obits if o["loc"] and o["loc"]["key"] == l["key"]) for l in LOCATIONS}
    chips = '<button class="chip" type="button" data-loc="all" aria-pressed="true">All locations</button>' + "".join(
        f'<button class="chip" type="button" data-loc="{l["key"]}" aria-pressed="false">{esc(l["name"])} <span class="muted">({counts[l["key"]]})</span></button>'
        for l in LOCATIONS if counts[l["key"]])
    body = f'''
<section class="page-hero" aria-labelledby="ob-h">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">Obituaries</span></nav>
    <span class="eyebrow">In Loving Memory</span>
    <h1 id="ob-h">Obituaries &amp; <em>tributes</em></h1>
    <p class="lead">Celebrate and remember the lives of those we have been entrusted to serve. Search by name to find a loved one, view service details, and share a memory with the family.</p>
  </div>
</section>
<section class="section" style="padding-top:0" aria-label="Obituary listing">
  <div class="container">
    <div class="glass obit-tools" role="search">
      <div class="search">
        <label class="sr-only" for="obit-search">Search obituaries by name</label>
        {icon("search")}
        <input class="input" id="obit-search" type="search" placeholder="Search by name…" autocomplete="off">
      </div>
      <label class="sr-only" for="obit-sort">Sort obituaries</label>
      <select class="select" id="obit-sort">
        <option value="newest">Newest first</option>
        <option value="oldest">Oldest first</option>
        <option value="name">Name A–Z</option>
      </select>
      <div class="chips" role="group" aria-label="Filter by location">{chips}</div>
    </div>
    <p class="result-meta" id="obit-count" aria-live="polite">Showing all {len(obits)} obituaries, newest first</p>
    <div class="obit-grid" id="obit-grid">
{cards}
    </div>
    <div class="empty-state" id="obit-empty" hidden>
      <span class="icon-badge" style="margin:0 auto 1rem">{icon("search")}</span>
      <h3>No obituaries match your search</h3>
      <p>Try a different spelling, or call us at <a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a> and we will gladly help.</p>
    </div>
    <div class="load-more-wrap"><button class="btn btn--secondary" id="obit-more" type="button" hidden>Show more obituaries</button></div>
  </div>
</section>
{cta_band("", "Obituary alerts", "Can’t find who you’re <em>looking for?</em>", "Our counselors are available 24/7 to help you locate service information for a loved one.")}
'''
    return page("Obituaries — Aetheria Funeral Homes",
                f"Browse {len(obits)} obituaries and service details from Aetheria Funeral Homes.",
                body, "", "obituaries.html", scripts=("obits.js",))


def text_paras(t):
    paras = [p.strip() for p in re.split(r"\n+", t) if p.strip()]
    return "".join(f"<p>{esc(p)}</p>" for p in paras)


def event_card(e):
    typ = (e.get("type") or "Service").strip()
    day = (e.get("day") or "").strip()
    date = (e.get("date") or "").strip()
    time = (e.get("time") or "").strip()
    loc = (e.get("location") or "").strip()
    addr = (e.get("address") or "").strip()
    durl = (e.get("directions_url") or "").strip()
    date_line = ", ".join(x for x in [day, date] if x) or "Date to be announced"
    parts = [f'<span class="event__type">{esc(typ)}</span>', f'<p class="event__date">{esc(date_line)}</p>']
    if time:
        parts.append(f'<span class="event__time">{esc(time)}</span>')
    if loc:
        parts.append(f'<span class="event__loc">{esc(loc)}</span>')
    if addr:
        parts.append(f'<address>{esc(addr)}</address>')
    if durl.startswith("http"):
        parts.append(f'<a class="btn btn--secondary btn--sm" href="{esc(durl)}" target="_blank" rel="noopener">{icon("compass")}Get directions<span class="sr-only"> to {esc(loc or typ)} (opens in new tab)</span></a>')
    return '<article class="card event">' + "".join(parts) + "</article>"


def build_detail(o, prev_o, next_o):
    root = "../"
    first = o["name"].split()[0] if o["name"] else "your loved one"
    loc = o["loc"]
    meta = []
    if o["age"]:
        meta.append(f'<span class="pill-tag">Age {esc(o["age"])}</span>')
    if loc:
        meta.append(f'<span class="pill-tag">{icon("pin")}Aetheria Funeral Homes · {esc(loc["name"])}</span>')
    dates = []
    if o["birth_str"]:
        dates.append(f'<span>{esc(o["birth_str"])}</span>')
    if o["death_str"]:
        if dates:
            dates.append('<span class="sep" aria-hidden="true"></span>')
        dates.append(f'<span>{esc(o["death_str"])}</span>')
    dates_html = "".join(dates)
    date_label = (f'Born {o["birth_str"]}, passed away {o["death_str"]}' if o["birth_str"] else f'Passed away {o["death_str"]}')

    if o["text"]:
        story = f'<div class="sub-h"><h2>Obituary</h2></div><div class="obit-text">{text_paras(o["text"])}</div>'
    else:
        story = f'''<div class="sub-h"><h2>Obituary</h2></div>
<div class="glass pending">
  <span class="icon-badge">{icon("feather")}</span>
  <h3>A full obituary is being prepared by the family</h3>
  <p>In the meantime, we invite you to honor {esc(first)}’s memory by sharing a story, a photo, or a few words of comfort for those who loved {esc(first)}.</p>
  <a class="btn btn--primary" href="#share-a-memory">{icon("heart")}Share a Memory</a>
</div>'''

    if o["events"]:
        services = '<div class="sub-h"><h2>Services</h2></div><div class="svc-events">' + "".join(event_card(e) for e in o["events"]) + "</div>"
    else:
        services = f'''<div class="sub-h"><h2>Services</h2></div>
<div class="card aside-card"><p style="margin:0">Service details have not been published yet. For information, please call us 24/7 at <a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a>.</p></div>'''
    if o["notes"]:
        services += f'<div class="notes">{icon("info")}<p style="margin:0">{esc(o["notes"])}</p></div>'

    loc_aside = ""
    if loc:
        loc_aside = f'''<div class="card aside-card">
  <span class="eyebrow">Arrangements by</span>
  <h3>Aetheria Funeral Homes · {esc(loc["name"])}</h3>
  <address>{esc(loc["street"])}<br>{esc(loc["city"])}<br>{esc(loc["lic"])}</address>
  <a class="btn btn--ghost btn--sm" href="{tel(loc["phone"])}">{icon("phone")}{esc(loc["phone"])}</a>
</div>'''

    def nav_link(x, label, cls):
        if not x:
            return "<span></span>"
        ic = icon("arrow-left") if cls == "prev" else ""
        ic2 = icon("arrow") if cls == "next" else ""
        return f'<a class="btn btn--ghost btn--sm" href="{esc(x["id"])}.html" aria-label="{label}: {esc(x["name"])}">{ic}{label}{ic2}</a>'

    body = f'''
<section class="memorial-hero" aria-labelledby="name-h">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">Home</a><span aria-hidden="true">/</span><a href="{root}obituaries.html">Obituaries</a><span aria-hidden="true">/</span><span aria-current="page">{esc(o["name"])}</span></nav>
    <div class="memorial">
      <div class="portrait">{portrait_inner(o, lazy=False)}</div>
      <div>
        <span class="eyebrow">In Loving Memory</span>
        <h1 id="name-h">{esc(o["name"])}</h1>
        <p class="memorial__dates" aria-label="{esc(date_label)}">{dates_html}</p>
        <div class="memorial__meta">{"".join(meta)}</div>
        <div class="btn-row">
          <a class="btn btn--primary" href="#share-a-memory">{icon("heart")}Share a Memory</a>
          <a class="btn btn--secondary" href="#send-flowers">{icon("flower")}Send Flowers</a>
          <a class="btn btn--secondary" href="#plant-a-tree">{icon("tree")}Plant a Tree</a>
        </div>
      </div>
    </div>
  </div>
</section>
<section class="section" style="padding-top:clamp(2rem,4vw,3rem)">
  <div class="container memorial__body">
    <div>
      {story}
      {services}
      <div class="glass memory-band" id="share-a-memory">
        <div><h3>Share a memory of {esc(first)}</h3><p>Your words can bring comfort to family and friends.</p></div>
        <a class="btn btn--primary" href="#share-a-memory">{icon("feather")}Write a tribute</a>
      </div>
    </div>
    <aside class="aside-stack" aria-label="Ways to honor {esc(o["name"])}">
      <div class="glass aside-card">
        <span class="eyebrow">Honor their memory</span>
        <h3>Ways to show you care</h3>
        <p>Express your sympathy with a memory, a floral tribute, or a living memorial tree.</p>
        <div class="aside-actions">
          <a class="btn btn--primary" href="#share-a-memory">{icon("heart")}Share a Memory</a>
          <a class="btn btn--secondary" href="#send-flowers" id="send-flowers">{icon("flower")}Send Flowers</a>
          <a class="btn btn--secondary" href="#plant-a-tree" id="plant-a-tree">{icon("tree")}Plant a Tree</a>
        </div>
      </div>
      {loc_aside}
      <div class="card aside-card">
        <span class="eyebrow">Need assistance?</span>
        <p style="margin:.25rem 0 1rem">Our counselors are available 24 hours a day.</p>
        <a class="btn btn--ghost btn--sm" href="{tel(PHONE_MAIN)}">{icon("phone")}{PHONE_MAIN}</a>
      </div>
    </aside>
  </div>
  <div class="container" style="margin-top:3rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
    {nav_link(prev_o, "Newer", "prev")}
    <a class="btn btn--secondary btn--sm" href="{root}obituaries.html">All obituaries</a>
    {nav_link(next_o, "Older", "next")}
  </div>
</section>
'''
    desc = f'Obituary and service information for {o["name"]}' + (f', {o["years"]}' if o["years"] else "") + ". Aetheria Funeral Homes."
    return page(f'{o["name"]} — Obituary | Aetheria Funeral Homes', desc, body, root, "obituaries.html")


def opt(title, text, extra=""):
    return f'<article class="card opt"><h3>{esc(title)}</h3><p>{esc(text)}</p>{extra}</article>'


def build_services(C):
    S = C.sec
    local = [(h, C.first("/local-services", h)) for h in
             ["Traditional Local Funeral Service with Vigil", "Traditional One-Day Funeral Service", "Immediate Burial"]]
    crem = [(h, C.first("/cremation-services", h)) for h in ["Direct Cremation", "Cremation with Vigil", "Memorial Service"]]
    docs = ["Birth Certificate", "Voter Identification", "Driver’s License", "Military Service Passbook",
            "Passport", "Consular Registration", "Declaration of Nationality"]
    mex = S("/transfer-services", "Direct Ship Out to Mexico")
    world = S("/transfer-services", "Funeral Transfers Direct to Central America, South America, and the Rest of the World")
    us_out = S("/transfer-services", "Funeral Transfers from California to the Rest of the United States")
    us_in = S("/transfer-services", "Funeral Transfers to California from the Rest of the United States")
    vets = S("/veterans", "VETERANS")
    eligible = C.items_after("/veterans", "Who is Eligible for Military Funeral Honors?")
    flags = re.sub(r"\s*[^.]*:$", "", S("/veterans-burial-flags", "VETERANS BURIAL FLAGS")[0])
    stones = S("/veterans-headstones", "VETERANS HEADSTONES")[0]
    pre = S("/pre-arrangements", "Pre-Arrangements")
    merch = [(h, C.first("/making-arrangements", h)) for h in
             ["Burial Caskets", "Burial Vaults", "Memorial Markers", "Urns", "Urn Vaults", "Cremation Caskets", "Flowers"]]
    grief_intro = S("/grief-support", "")[0]
    grief = [(h, C.first("/grief-support", h)) for h in
             ["CRISIS, GRIEF AND HEALING", "GRIEF AND LOSS", "WILLOWGREEN", "NATIONAL HOSPICE AND PALLIATIVE CARE ORGANIZATION"]]
    grief_year = C.first("/grief-support", "A year of daily grief support")
    steps = [(h, " ".join(S("/when-death-occurs", h)[:2])) for h in
             ["Notify Proper Authorities", "Call the Funeral Home", "Meet the Funeral Director/Staff", "File for a Death Certificate"]]
    when_intro = S("/when-death-occurs", "What to do")[1]

    def titlecase(s):
        return " ".join(w.capitalize() if w.isupper() and len(w) > 3 else w for w in s.split()).replace("And ", "and ")

    def section(id_, ic, eyebrow, title, intro_html, content):
        return f'''<div class="svc-section" id="{id_}">
  <div class="svc-section__intro">
    <span class="icon-badge">{icon(ic)}</span>
    <span class="eyebrow">{eyebrow}</span>
    <h2>{title}</h2>
    {intro_html}
  </div>
  <div>{content}</div>
</div>'''

    toc = "".join(f'<a class="chip" href="#{i}">{t}</a>' for i, t in [
        ("funeral", "Funeral &amp; Burial"), ("cremation", "Cremation"), ("transfers", "Transfers &amp; Repatriation"),
        ("veterans", "Veterans"), ("pre-planning", "Pre-Planning"), ("arrangements", "Caskets &amp; Urns"),
        ("when-death-occurs", "When Death Occurs"), ("grief", "Grief Support")])

    body = f'''
<section class="page-hero" aria-labelledby="sv-h">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">Services</span></nav>
    <span class="eyebrow">Our Services</span>
    <h1 id="sv-h">Services shaped around <em>your wishes</em></h1>
    <p class="lead">{esc(C.sec("/", "Welcome to Continental Funeral Home FD 1915")[0].split(". At Continental Funeral Home we appreciate")[0].split("defines us. ")[-1])}.</p>
    <nav class="toc" aria-label="Jump to a service">{toc}</nav>
  </div>
</section>
<section class="section" style="padding-top:clamp(1rem,3vw,2rem)">
  <div class="container">
  {section("funeral", "leaf", "Funeral &amp; Burial", "Funeral &amp; burial services",
           f'<p>{esc(C.first("/", "Burial Options"))}</p>',
           '<div class="opt-grid">' + "".join(opt(h, t) for h, t in local) + opt("Memorial Options", C.first("/", "Memorial Options")) + "</div>")}
  {section("cremation", "flame", "Cremation", "Cremation services",
           f'<p>{esc(C.first("/", "Cremation Options"))}</p>',
           '<div class="opt-grid">' + "".join(opt(h, t) for h, t in crem) + "</div>")}
  {section("transfers", "globe", "Transfers &amp; Repatriation", "Bringing loved ones home",
           f'<p>{esc(mex[1])}</p>',
           '<div class="opt-grid">'
           + opt("Direct Ship Out to Mexico", mex[0] + " " + mex[2],
                 '<ul>' + "".join(f"<li>{esc(d)}</li>" for d in docs) + '</ul>')
           + opt("Central America, South America &amp; the rest of the world".replace("&amp;", "&"), world[0] + " " + (world[3] if len(world) > 3 else ""))
           + opt("From California to the rest of the U.S.", us_out[0])
           + opt("To California from the rest of the U.S.", us_in[0])
           + "</div>")}
  {section("veterans", "flag", "Veterans", "Veterans services &amp; military honors",
           f'<p>{esc(vets[0])}</p>',
           '<div class="opt-grid">'
           + opt("Military Funeral Honors", vets[1] + " " + vets[2])
           + opt("Who is eligible?", "Eligibility for Military Funeral Honors includes:",
                 '<ul>' + "".join(f"<li>{esc(x)}</li>" for x in eligible[:4]) + '</ul>')
           + opt("Veterans Burial Flags", flags)
           + opt("Veterans Headstones", stones)
           + "</div>")}
  {section("pre-planning", "calendar", "Pre-Planning", "Plan ahead, ease the burden",
           f'<p>{esc(pre[0])}</p>',
           '<div class="opt-grid">' + opt("Peace of mind", pre[1]) + opt("Plan from home", pre[2].replace(" by clicking the button below", "")
           .replace(" See the form below for details.", ""))
           + f'<article class="card opt opt--wide" style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap"><div><h3>Start your pre-arrangements</h3><p>Speak with a funeral counselor at {PHONE_MAIN}.</p></div><a class="btn btn--primary" href="contact.html">Plan a Service {icon("arrow")}</a></article>'
           + "</div>")}
  {section("arrangements", "box", "Making Arrangements", "Caskets, urns &amp; keepsakes",
           f'<p>{esc(C.sec("/making-arrangements", "only the finest quality")[0])}</p>',
           '<div class="opt-grid">' + "".join(opt(h, t) for h, t in merch) + "</div>")}
  {section("when-death-occurs", "compass", "When Death Occurs", "What to do first",
           f'<p>{esc(when_intro)}</p>',
           '<div class="steps">' + "".join(f'<article class="card step"><h3>{esc(h.replace("/Staff", " &amp; staff").replace("&amp;", "&"))}</h3><p>{esc(t)}</p></article>' for h, t in steps) + "</div>")}
  {section("grief", "heart", "Grief Support", "Support that continues",
           f'<p>{esc(grief_intro)}</p><p>{esc(grief_year)}</p>',
           '<div class="opt-grid">' + "".join(opt(titlecase(h), t) for h, t in grief) + "</div>")}
  </div>
</section>
{cta_band("")}
'''
    return page("Services — Aetheria Funeral Homes",
                "Funeral, burial, cremation, repatriation, veterans, and pre-planning services from Aetheria Funeral Homes.",
                body, "", "services.html")


def build_about(C):
    approach = C.first("/about-us", "Our Approach")
    about = C.first("/about-us", "About Us")
    s = re.split(r"(?<=\.)\s+", about)
    p1 = " ".join(s[:2]); p2 = " ".join(s[2:5]); p3 = " ".join(s[5:])
    values = [("shield", "Integrity"), ("hand", "Respect"), ("star", "Professionalism"), ("leaf", "Care"), ("heart", "Compassion")]
    vals = "".join(f'<article class="card value"><span class="icon-badge">{icon(i)}</span><h3>{t}</h3></article>' for i, t in values)
    locs = "".join(loc_card(l, with_btn=True) for l in LOCATIONS)
    transfer = C.sec("/transfer-services", "Funeral Transfers Direct to Central America, South America, and the Rest of the World")
    customs = next((p for p in transfer if p.startswith("At Continental Funeral Home, we understand the customs")), "")
    body = f'''
<section class="page-hero" aria-labelledby="ab-h">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">About</span></nav>
    <span class="eyebrow">About Us</span>
    <h1 id="ab-h">Every life is unique, <em>every farewell</em> personal</h1>
    <p class="lead">{esc(approach)}</p>
  </div>
</section>

<section class="section section--tight" aria-labelledby="story-h">
  <div class="container split">
    <div>
      <span class="eyebrow">Our Story</span>
      <h2 id="story-h">Founded on a vision <em>of service</em></h2>
      <p class="lead" style="color:var(--c-fg)">{esc(p1)}</p>
      <p class="muted" style="line-height:1.8">{esc(customs)}</p>
      <div class="stat-row">
        <div class="card stat"><strong>25+</strong><span>Years in the funeral industry</span></div>
        <div class="card stat"><strong>5</strong><span>Locations across California</span></div>
        <div class="card stat"><strong>24/7</strong><span>Always available to families</span></div>
      </div>
    </div>
    <article class="glass founder-card" aria-labelledby="founder-h">
      <div class="founder-card__top">
        <div class="founder-card__avatar">{monogram("Magda Maldonado", dark=True)}</div>
        <div><span class="eyebrow" style="margin-bottom:.4rem">Founder &amp; Director</span><h3 id="founder-h">Magda Maldonado</h3></div>
      </div>
      <p class="quote" style="font-size:1.6rem;margin-bottom:1.5rem">To provide a memorable funeral service to each and every family who has trusted her with the care of a loved one.</p>
      <p>{esc(p2)}</p>
      <p style="margin:0">{esc(p3)}</p>
    </article>
  </div>
</section>

<section class="section section--wash" aria-labelledby="val-h">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow eyebrow--center">Our Values</span>
      <h2 id="val-h">The compassion <em>that defines us</em></h2>
      <p class="lead">We are dedicated to providing services with integrity, respect, professionalism, care, and compassion.</p>
    </div>
    <div class="values">{vals}</div>
  </div>
</section>

<section class="section section--tight" aria-labelledby="locs-h" id="locations">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Our Locations</span>
      <h2 id="locs-h">Five funeral homes, <em>one family</em></h2>
      <p class="lead">Visit one of our funeral homes in person at your convenience, or reach us any time by phone, text, or email.</p>
    </div>
    <div class="loc-list">{locs}</div>
  </div>
</section>
<div id="contact">{cta_band("")}</div>
'''
    return page("About — Aetheria Funeral Homes",
                "Founded and directed by Magda Maldonado, Aetheria Funeral Homes has served families for more than 25 years across five California locations.",
                body, "", "about.html")


def build_contact(C):
    intro = C.pages["/contact-us"]["main_text"].split("\n")[0].strip()
    locs = "".join(loc_card(l, with_btn=True) for l in LOCATIONS)
    loc_opts = "".join(f'<option>{esc(l["name"])}</option>' for l in LOCATIONS)
    body = f'''
<section class="page-hero" aria-labelledby="ct-h">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">Contact</span></nav>
    <span class="eyebrow">Contact &amp; Plan a Service</span>
    <h1 id="ct-h">We are here, <em>whenever you need us</em></h1>
    <p class="lead">{esc(intro)}</p>
  </div>
</section>
<section class="section section--tight" style="padding-top:0">
  <div class="container split" style="align-items:start">
    <div class="glass care-card">
      <span class="eyebrow">To better serve you</span>
      <h2>Contact us 24/7</h2>
      <ul class="care-list">
        <li><span class="ic">{icon("phone")}</span><div><small>By calling</small><a href="{tel(PHONE_MAIN)}">{PHONE_MAIN}</a></div></li>
        <li><span class="ic">{icon("message")}</span><div><small>By text · no calls, please</small><a href="sms:+13239875025">{PHONE_TEXT}</a></div></li>
        <li><span class="ic">{icon("box")}</span><div><small>By fax · no calls, please</small><span class="v">{PHONE_FAX}</span></div></li>
        <li><span class="ic">{icon("mail")}</span><div><small>By email</small><a href="mailto:{EMAIL}">{EMAIL}</a></div></li>
      </ul>
    </div>
    <form class="card form-card" action="mailto:{EMAIL}" method="post" enctype="text/plain" aria-labelledby="form-h">
      <span class="eyebrow">Send a message</span>
      <h2 id="form-h" style="font-size:2rem">How can we help?</h2>
      <div class="form-grid">
        <label class="field">Your name<input class="input" name="name" autocomplete="name" required></label>
        <label class="field">Phone<input class="input" name="phone" type="tel" autocomplete="tel"></label>
        <label class="field full">Email<input class="input" name="email" type="email" autocomplete="email"></label>
        <label class="field full">Preferred location<select class="input" name="location">{loc_opts}</select></label>
        <label class="field full">Message<textarea class="input" name="message" rows="5"></textarea></label>
      </div>
      <button class="btn btn--primary" type="submit" style="margin-top:1.25rem">Send message {icon("arrow")}</button>
      <p class="muted" style="font-size:.82rem;margin:1rem 0 0">For immediate assistance, please call {PHONE_MAIN} — we answer 24 hours a day.</p>
    </form>
  </div>
</section>
<section class="section section--tight" aria-labelledby="cl-h">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Our Locations</span><h2 id="cl-h">Visit us in person</h2></div>
    <div class="loc-list">{locs}</div>
  </div>
</section>
'''
    return page("Contact — Aetheria Funeral Homes",
                "Contact Aetheria Funeral Homes 24/7 by phone, text, fax, or email, or visit one of five locations.",
                body, "", "contact.html")


# --------------------------------------------------------------------------
def write(rel, content):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    C = Content()
    obits = load_obits()
    ob_dir = os.path.join(HERE, "obituary")
    if os.path.isdir(ob_dir):
        shutil.rmtree(ob_dir)
    write("index.html", build_index(C, obits))
    write("obituaries.html", build_obituaries(obits))
    write("services.html", build_services(C))
    write("about.html", build_about(C))
    write("contact.html", build_contact(C))
    for i, o in enumerate(obits):
        prev_o = obits[i - 1] if i > 0 else None
        next_o = obits[i + 1] if i + 1 < len(obits) else None
        write(o["href"], build_detail(o, prev_o, next_o))
    real = sum(1 for o in obits if o["text"])
    photos = sum(1 for o in obits if o["has_photo"])
    print(f"Built 5 main pages + {len(obits)} obituary pages "
          f"({real} with obituary text, {photos} with photos, {len(obits) - photos} monograms).")


if __name__ == "__main__":
    main()
