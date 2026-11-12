"""Render preview screenshots + basic checks (run with /workspace/tokens/.venv/bin/python)."""
import os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "previews")
os.makedirs(OUT, exist_ok=True)
DETAIL = sys.argv[1] if len(sys.argv) > 1 else "2355253"
PENDING = sys.argv[2] if len(sys.argv) > 2 else "2699013"
jobs = [("index.html", "index-1440.png", 1440), ("obituaries.html", "obituaries-1440.png", 1440),
        (f"obituary/{DETAIL}.html", f"obituary-{DETAIL}-1440.png", 1440),
        ("services.html", "services-1440.png", 1440), ("about.html", "about-1440.png", 1440),
        ("index.html", "index-mobile-390.png", 390),
        (f"obituary/{PENDING}.html", f"obituary-{PENDING}-pending-monogram-1440.png", 1440),
        ("contact.html", "contact-1440.png", 1440)]
with sync_playwright() as p:
    b = p.chromium.launch()
    for rel, name, w in jobs:
        pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto("file://" + os.path.join(HERE, rel), wait_until="networkidle")
        pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); }""")
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        fonts = pg.evaluate("""() => ({serif: document.fonts.check('300 48px "Cormorant Garamond"'), sans: document.fonts.check('400 16px Outfit'),
            loaded: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style)})""")
        broken_imgs = pg.evaluate("() => [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
        pg.wait_for_timeout(1200)  # let fade-up animations finish
        pg.screenshot(path=os.path.join(OUT, name), full_page=True)
        print(name, "fonts:", fonts["serif"], fonts["sans"], len(fonts["loaded"]), "broken imgs:", len(broken_imgs), "console errors:", errs[:3])
    # search test
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("file://" + os.path.join(HERE, "obituaries.html"))
    total = pg.locator("#obit-grid .obit-card").count()
    visible0 = pg.locator("#obit-grid .obit-card:not([hidden])").count()
    pg.fill("#obit-search", "maria")
    vis = pg.locator("#obit-grid .obit-card:not([hidden])").count()
    print("index cards:", total, "initially visible:", visible0, "| search 'maria' visible:", vis, "|", pg.inner_text("#obit-count"))
    pg.fill("#obit-search", "zzzzqq"); print("no-match empty state visible:", pg.is_visible("#obit-empty"))
    b.close()
