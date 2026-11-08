"""Convert a tailored CV .docx to simple HTML so Drive can import it as a Google Doc.

Usage: python3 scripts/docx_to_html.py runs/<run>/cvs/<name>.docx   (writes <name>.html next to it)

Run without -I: python-docx lives in the user site-packages, which -I hides.
Text uploads are reliable through the Drive connector; base64 .docx uploads are not.
"""
import html
import sys

import docx


def main(path):
    d = docx.Document(path)
    out, inlist = [], False
    for i, p in enumerate(d.paragraphs):
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name.lower()
        escaped = html.escape(text)
        is_item = "list" in style or (p._p.pPr is not None and p._p.pPr.numPr is not None)
        if is_item and not inlist:
            out.append("<ul>")
            inlist = True
        if not is_item and inlist:
            out.append("</ul>")
            inlist = False
        if i == 0:
            out.append(f"<h1>{escaped}</h1>")
        elif is_item:
            out.append(f"<li>{escaped}</li>")
        elif "heading" in style or (text.isupper() and len(text) < 30):
            out.append(f"<h2>{escaped}</h2>")
        else:
            out.append(f"<p>{escaped}</p>")
    if inlist:
        out.append("</ul>")
    dest = path[:-5] + ".html"
    with open(dest, "w", encoding="utf-8") as f:
        f.write("<html><body>" + "".join(out) + "</body></html>")
    print(dest)


if __name__ == "__main__":
    main(sys.argv[1])
