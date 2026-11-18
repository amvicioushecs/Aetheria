"""Check internal links/assets (and #anchors) for all generated pages."""
import os, re, sys, glob
from urllib.parse import unquote
HERE = os.path.dirname(os.path.abspath(__file__))
pages = sorted(set(
    glob.glob(os.path.join(HERE, "index.html"))
    + glob.glob(os.path.join(HERE, "*", "index.html"))
    + glob.glob(os.path.join(HERE, "obituary", "*", "index.html"))
))
ids_cache, bad, n = {}, [], 0

def ids(path):
    if path not in ids_cache:
        ids_cache[path] = set(re.findall(r'\sid="([^"]+)"', open(path, encoding="utf-8").read()))
    return ids_cache[path]

def resolve(ref, current):
    path, _, frag = ref.partition("#")
    path = path.split('?', 1)[0]
    if not path:
        return current, frag
    path = unquote(path)
    if path.startswith("/"):
        rel = path.lstrip("/")
        target = os.path.normpath(os.path.join(HERE, rel))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(current), path))
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    elif path.endswith("/") or (path.startswith("/") and not os.path.splitext(rel if path.startswith("/") else path)[1]):
        base = path.lstrip("/").rstrip("/")
        target = os.path.join(HERE, "index.html") if not base else os.path.join(HERE, base, "index.html")
    return target, frag

for p in pages:
    html = open(p, encoding="utf-8").read()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
        if re.match(r'^(https?:|mailto:|tel:|sms:|data:|#)', ref) or ref.startswith("https://"):
            continue
        if re.match(r'^(https?:|mailto:|tel:|sms:|data:)', ref):
            continue
        n += 1
        target, frag = resolve(ref, p)
        if not os.path.exists(target):
            bad.append((os.path.relpath(p, HERE), ref, os.path.relpath(target, HERE) if target.startswith(HERE) else target))
            continue
        if frag and target.endswith(".html") and frag not in ids(target):
            bad.append((os.path.relpath(p, HERE), ref, "missing anchor"))
print(f"pages checked: {len(pages)}, internal refs: {n}, broken: {len(bad)}")
for b in bad[:25]:
    print("  BROKEN", b)
sys.exit(1 if bad else 0)
