"""Generate ar/index.html from index.html.

index.html is the English source. Every translated element carries
data-en / data-ar and holds text only; attributes that change in Arabic
carry data-ar-<attr> (for example data-ar-href, data-ar-content).

Run from the repo root after editing index.html:
    python tools/build-ar.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text(encoding="utf-8")

# Text: <tag ... data-ar="X" ...>English</tag>  ->  <tag ...>X</tag>
TEXT = re.compile(r'(<(\w+)\b[^>]*?\sdata-ar="([^"]*)"[^>]*>)(.*?)(</\2>)', re.S)


def swap_text(m):
    open_tag, _, ar, _, close_tag = m.groups()
    return open_tag + ar + close_tag


# Attributes: data-ar-<attr>="X" replaces <attr>'s value in the same tag
TAG = re.compile(r"<\w+\b[^>]*\sdata-ar-[\w-]+=\"[^\"]*\"[^>]*>")
ATTR = re.compile(r'\sdata-ar-([\w-]+)="([^"]*)"')


def swap_attrs(m):
    tag = m.group(0)
    for name, value in ATTR.findall(tag):
        tag, n = re.subn(r'(\s%s=")[^"]*(")' % re.escape(name), lambda x: x.group(1) + value + x.group(2), tag, count=1)
        if not n:
            raise SystemExit(f"data-ar-{name} has no matching {name}= in: {tag[:120]}")
    return tag


out, n_text = TEXT.subn(swap_text, src)
out, n_attr = TAG.subn(swap_attrs, out)
out = out.replace('<html lang="en" dir="ltr">', '<html lang="ar" dir="rtl">', 1)
out = out.replace(
    "<!-- Source page (English). ar/index.html is generated from it: run `python tools/build-ar.py` after editing. -->",
    "<!-- Generated from index.html by tools/build-ar.py. Do not edit by hand. -->",
    1,
)
if 'lang="ar" dir="rtl"' not in out:
    raise SystemExit("html lang/dir was not switched")

(ROOT / "ar").mkdir(exist_ok=True)
(ROOT / "ar" / "index.html").write_text(out, encoding="utf-8")
print(f"ar/index.html written: {n_text} text swaps, {n_attr} tags with attribute swaps")
