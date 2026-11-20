#!/usr/bin/env python3
"""Render cv.json to an ATS-safe single-column HTML, Markdown and (if an engine exists) PDF.

Usage: python3 render_cv.py cv.json --out DIR [--region us|uk|eu|dach|latam] [--no-pdf]
PDF engines tried in order: weasyprint (python), Chrome/Chromium headless. Standard library otherwise.
"""
import argparse, html, json, shutil, subprocess
from pathlib import Path

CSS = """
body{font-family:Arial,Helvetica,sans-serif;font-size:10.5pt;line-height:1.35;color:#111;max-width:760px;margin:24px auto;padding:0 18px}
h1{font-size:20pt;margin:0}h2{font-size:12pt;border-bottom:1px solid #333;margin:14px 0 6px;padding-bottom:2px;text-transform:uppercase}
.contact{margin:2px 0 8px}.role{margin:8px 0 0}.meta{color:#333}ul{margin:3px 0 6px 18px;padding:0}li{margin:1px 0}
@page{size:A4;margin:14mm}
"""
LABELS = {
    "en": dict(summary="Summary", experience="Experience", projects="Projects", skills="Skills", education="Education", certs="Certifications", languages="Languages", present="Present"),
    "es": dict(summary="Resumen", experience="Experiencia", projects="Proyectos", skills="Habilidades", education="Formación", certs="Certificaciones", languages="Idiomas", present="Actualidad"),
}


def e(s):
    return html.escape(str(s))


def render(cv, region):
    lang = cv.get("language", "en")
    L = LABELS.get(lang, LABELS["en"])
    b = cv.get("basics", {})
    contact = [b.get(k) for k in ("email", "phone", "location")] + [l.get("url", "") for l in b.get("links", [])]
    if region in ("eu", "dach", "latam") and b.get("nationality"):
        contact.append(b["nationality"])
    contact = [c for c in contact if c]
    h = [f"<h1>{e(b.get('name',''))}</h1>"]
    if b.get("label"):
        h.append(f"<div class='meta'>{e(b['label'])}</div>")
    h.append(f"<div class='contact'>{' | '.join(e(c) for c in contact)}</div>")
    md = [f"# {b.get('name','')}", b.get("label", ""), " | ".join(contact), ""]
    if cv.get("summary"):
        h.append(f"<h2>{L['summary']}</h2><p>{e(cv['summary'])}</p>")
        md += [f"## {L['summary']}", cv["summary"], ""]

    def block(items, key):
        for it in items:
            name = it.get("title") or it.get("name", "")
            org = it.get("company", "")
            dates = " - ".join(x for x in (str(it.get("start", "")), str(it.get("end") or L["present"])) if x and x != "None") if it.get("start") else ""
            h.append(f"<div class='role'><strong>{e(name)}</strong>{', ' + e(org) if org else ''}<span class='meta'> | {e(dates)}</span></div><ul>")
            md.append(f"**{name}**{', ' + org if org else ''}" + (f" | {dates}" if dates else ""))
            for bl in it.get("bullets", []):
                h.append(f"<li>{e(bl['text'])}</li>")
                md.append(f"- {bl['text']}")
            h.append("</ul>")
            md.append("")

    if cv.get("experience"):
        h.append(f"<h2>{L['experience']}</h2>")
        md.append(f"## {L['experience']}")
        block(cv["experience"], "experience")
    if cv.get("projects"):
        h.append(f"<h2>{L['projects']}</h2>")
        md.append(f"## {L['projects']}")
        block(cv["projects"], "projects")
    if cv.get("skills"):
        h.append(f"<h2>{L['skills']}</h2><p>{e(', '.join(cv['skills']))}</p>")
        md += [f"## {L['skills']}", ", ".join(cv["skills"]), ""]
    if cv.get("education"):
        h.append(f"<h2>{L['education']}</h2>")
        md.append(f"## {L['education']}")
        for ed in cv["education"]:
            line = f"{ed.get('degree','')}, {ed.get('institution','')} ({ed.get('start','')}-{ed.get('end','')})"
            h.append(f"<p>{e(line)}</p>")
            md.append(line)
        md.append("")
    if cv.get("certifications"):
        h.append(f"<h2>{L['certs']}</h2><ul>" + "".join(f"<li>{e(c['name'])}{', ' + e(c['issuer']) if c.get('issuer') else ''}</li>" for c in cv["certifications"]) + "</ul>")
        md += [f"## {L['certs']}"] + [f"- {c['name']}" for c in cv["certifications"]] + [""]
    if cv.get("languages"):
        h.append(f"<h2>{L['languages']}</h2><p>{e(', '.join(l['name'] + ' (' + l.get('level','') + ')' for l in cv['languages']))}</p>")
        md += [f"## {L['languages']}", ", ".join(f"{l['name']} ({l.get('level','')})" for l in cv["languages"]), ""]
    doc = f"<!doctype html><html lang='{lang}'><head><meta charset='utf-8'><title>{e(b.get('name',''))} - CV</title><style>{CSS}</style></head><body>{''.join(h)}</body></html>"
    return doc, "\n".join(md)


def to_pdf(html_path, pdf_path):
    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return "weasyprint"
    except Exception:
        pass
    for exe in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium", "chromium-browser", "chrome"):
        path = exe if Path(exe).exists() else shutil.which(exe)
        if path:
            r = subprocess.run([path, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], capture_output=True)
            if r.returncode == 0 and Path(pdf_path).exists():
                return "chrome"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--region", default="us")
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    cv = json.loads(Path(a.cv).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    doc, md = render(cv, a.region)
    (out / "cv.html").write_text(doc, encoding="utf-8")
    (out / "cv.md").write_text(md, encoding="utf-8")
    print("Wrote", out / "cv.html", out / "cv.md")
    if not a.no_pdf:
        eng = to_pdf(out / "cv.html", out / "cv.pdf")
        print(f"Wrote {out/'cv.pdf'} via {eng}" if eng else "No PDF engine found (pip install weasyprint, or install Chrome). HTML/MD are ready.")


if __name__ == "__main__":
    main()
