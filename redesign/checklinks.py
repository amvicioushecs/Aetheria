"""Check internal links/assets (and #anchors) for all generated pages."""
import os, re, sys, glob
from urllib.parse import urlparse, unquote
HERE = os.path.dirname(os.path.abspath(__file__))
pages = sorted(glob.glob(os.path.join(HERE, "*.html")) + glob.glob(os.path.join(HERE, "obituary", "*.html")))
ids_cache, bad, n = {}, [], 0
def ids(path):
    if path not in ids_cache:
        ids_cache[path] = set(re.findall(r'\sid="([^"]+)"', open(path, encoding="utf-8").read()))
    return ids_cache[path]
for p in pages:
    html = open(p, encoding="utf-8").read()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
        if re.match(r'^(https?:|mailto:|tel:|sms:|data:)', ref):
            continue
        n += 1
        path, _, frag = ref.partition("#")
        target = os.path.normpath(os.path.join(os.path.dirname(p), unquote(path))) if path else p
        if not os.path.exists(target):
            bad.append((os.path.relpath(p, HERE), ref)); continue
        if frag and target.endswith(".html") and frag not in ids(target):
            bad.append((os.path.relpath(p, HERE), ref))
print(f"pages checked: {len(pages)}, internal refs: {n}, broken: {len(bad)}")
for b in bad[:20]: print("  BROKEN", b)
