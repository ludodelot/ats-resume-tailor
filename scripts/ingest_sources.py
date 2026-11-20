#!/usr/bin/env python3
"""Ingest career sources into a local folder the agent can read.

  python3 ingest_sources.py pdf FILE.pdf --out profile/sources     (text via pdftotext or pypdf)
  python3 ingest_sources.py text FILE.docx|.txt|.md --out ...      (docx via python-docx if installed)
  python3 ingest_sources.py github USERNAME --out profile/sources  (public API: repos, languages, topics)
  python3 ingest_sources.py linkedin EXPORT_DIR --out ...          (copies key CSVs as readable markdown)

Nothing is sent anywhere except the GitHub username to api.github.com for the `github` command.
"""
import argparse, csv, json, shutil, subprocess, sys, urllib.request
from pathlib import Path


def pdf(src, out):
    if shutil.which("pdftotext"):
        t = subprocess.run(["pdftotext", "-layout", src, "-"], capture_output=True, text=True).stdout
    else:
        try:
            from pypdf import PdfReader
            t = "\n".join(p.extract_text() or "" for p in PdfReader(src).pages)
        except Exception:
            sys.exit("Install poppler (`brew install poppler`) or `pip install pypdf`.")
    if len(t.strip()) < 100:
        print("Almost no text: scanned PDF? Try OCR (e.g. `ocrmypdf in.pdf out.pdf`).")
    dest = out / f"{Path(src).stem}.txt"
    dest.write_text(t, encoding="utf-8")
    print("Wrote", dest)


def text(src, out):
    p = Path(src)
    if p.suffix == ".docx":
        try:
            import docx
            t = "\n".join(x.text for x in docx.Document(src).paragraphs)
        except ImportError:
            sys.exit("pip install python-docx")
    else:
        t = p.read_text(encoding="utf-8", errors="replace")
    dest = out / f"{p.stem}.txt"
    dest.write_text(t, encoding="utf-8")
    print("Wrote", dest)


def github(user, out):
    def get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "ats-resume-tailor", "Accept": "application/vnd.github+json"})
        return json.load(urllib.request.urlopen(req, timeout=20))
    repos = get(f"https://api.github.com/users/{user}/repos?per_page=100&sort=pushed")
    rows = []
    for r in repos:
        if r.get("fork"):
            continue
        rows.append({"name": r["name"], "description": r.get("description"), "language": r.get("language"),
                     "topics": r.get("topics", []), "stars": r["stargazers_count"], "url": r["html_url"], "pushed": r["pushed_at"][:10]})
    dest = out / "github.json"
    dest.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    langs = sorted({r["language"] for r in rows if r["language"]})
    print(f"Wrote {dest}: {len(rows)} original repos. Languages: {', '.join(langs)}")


def linkedin(src, out):
    for name in ("Positions.csv", "Education.csv", "Skills.csv", "Certifications.csv", "Projects.csv", "Profile.csv"):
        f = Path(src) / name
        if f.exists():
            rows = list(csv.DictReader(f.open(encoding="utf-8-sig")))
            md = [f"# {name}"] + ["- " + "; ".join(f"{k}: {v}" for k, v in r.items() if v) for r in rows]
            (out / f"linkedin_{f.stem}.md").write_text("\n".join(md), encoding="utf-8")
            print("Wrote", out / f"linkedin_{f.stem}.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["pdf", "text", "github", "linkedin"])
    ap.add_argument("source")
    ap.add_argument("--out", default="profile/sources")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    {"pdf": pdf, "text": text, "github": github, "linkedin": linkedin}[a.kind](a.source, out)


if __name__ == "__main__":
    main()
