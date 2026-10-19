"""Render a Markdown report to PDF via headless Microsoft Edge.

Usage: python md2pdf.py ../REPORT_zh.md ../REPORT_zh.pdf
"""

import re
import subprocess
import sys
from pathlib import Path

import markdown

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CSS = """
body { font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
       font-size: 10.5pt; line-height: 1.6; color: #222; margin: 0 6mm; }
h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 14pt; margin-top: 18px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 12pt; margin-top: 14px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 4px 6px; vertical-align: top; }
th { background: #f0f0f0; }
tr { page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f4f4f4; padding: 0 2px; }
pre { background: #f4f4f4; padding: 8px; font-size: 8.5pt; white-space: pre-wrap; }
pre code { background: none; }
blockquote { border-left: 3px solid #999; margin: 6px 0; padding-left: 10px; color: #555; }
hr { border: none; border-top: 1px solid #ddd; }
a { color: #1a5fb4; text-decoration: none; }
"""

LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s")


def fix_lists(text):
    """Python-Markdown needs a blank line before a list and 4-space nesting; GitHub doesn't."""
    out, in_code = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code and LIST_ITEM.match(line):
            if out and out[-1].strip() and not LIST_ITEM.match(out[-1]) and not out[-1].startswith(" "):
                out.append("")
            indent = len(line) - len(line.lstrip())
            line = " " * (indent * 2) + line.lstrip()
        out.append(line)
    return "\n".join(out)


src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
body = markdown.markdown(fix_lists(src.read_text(encoding="utf-8")), extensions=["tables", "fenced_code"])
html = src.with_suffix(".html")
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
                f"<body>{body}</body></html>", encoding="utf-8")
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", html.as_uri()], check=True, timeout=120)
html.unlink()
print("wrote", out)
