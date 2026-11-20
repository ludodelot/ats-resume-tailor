#!/usr/bin/env python3
"""Heuristic ATS-parseability check for a CV (.pdf, .html, .md, .txt).

Usage: python3 check_ats_format.py FILE. Exit 1 on failures.
PDF text via `pdftotext` (poppler) or pypdf. Checks: extractable text, contact info, standard headings,
column/table layout signs, page count, odd glyphs. Heuristic, not a real ATS.
"""
import re, shutil, subprocess, sys
from pathlib import Path

HEADINGS = {"experience": r"experience|experiencia|work history|employment",
            "education": r"education|formaci[oó]n|educaci[oó]n",
            "skills": r"skills|habilidades|competencias"}


def extract(path):
    p = Path(path)
    if p.suffix == ".pdf":
        if shutil.which("pdftotext"):
            out = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout
            pages = out.count("\f") + (0 if out.endswith("\f") else 1)
            return out, pages
        try:
            from pypdf import PdfReader
            r = PdfReader(str(p))
            return "\n".join(pg.extract_text() or "" for pg in r.pages), len(r.pages)
        except Exception:
            sys.exit("Need `pdftotext` (brew install poppler) or `pip install pypdf` to read PDFs.")
    t = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix in (".html", ".htm"):
        t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
        t = re.sub(r"</(h[1-6]|p|li|div|ul|tr)>|<br\s*/?>", "\n", t, flags=re.I)
        t = re.sub(r"<[^>]+>", " ", t)
        t = re.sub(r"[ \t]+", " ", t)
    return t, None


def main():
    text, pages = extract(sys.argv[1])
    fails, warns = [], []
    if len(text.strip()) < 300:
        fails.append("Very little extractable text (scanned image or text in graphics?)")
    head = "\n".join(text.strip().splitlines()[:8])
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", head):
        warns.append("No email in the first lines (is contact info in a header/footer or image?)")
    if not re.search(r"\+?\d[\d\s().-]{7,}", head):
        warns.append("No phone number in the first lines")
    for name, rx in HEADINGS.items():
        if not re.search(rf"^\s*(?:{rx})\s*$", text, re.I | re.M):
            warns.append(f"Standard heading for '{name}' not found as its own line")
    gap = [l for l in text.splitlines() if re.search(r"\S {5,}\S", l)]
    if text.splitlines() and len(gap) / max(len(text.splitlines()), 1) > 0.15:
        warns.append(f"{len(gap)} lines have wide internal gaps: possible multi-column layout or table")
    if re.search(r"[•●■❖]{2,}|[-]", text):
        warns.append("Private-use or decorative glyphs found (icons/bullets that may not parse)")
    if pages and pages > 2:
        warns.append(f"{pages} pages: aim for 1-2")
    for f in fails:
        print("[FAIL]", f)
    for w in warns:
        print("[WARN]", w)
    print(f"{len(fails)} failures, {len(warns)} warnings" + (f", {pages} page(s)" if pages else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
