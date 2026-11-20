#!/usr/bin/env python3
"""Convert profile.json or cv.json to the JSON Resume schema (jsonresume.org).

Usage: python3 export_jsonresume.py FILE.json --out resume.json
"""
import argparse, json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.loads(Path(a.src).read_text(encoding="utf-8"))
    b = d.get("basics", {})
    out = {"basics": {"name": b.get("name", ""), "label": b.get("label", ""), "email": b.get("email", ""), "phone": b.get("phone", ""),
                      "summary": d.get("summary", ""), "location": {"address": b.get("location", "")},
                      "profiles": [{"network": l.get("label", ""), "url": l.get("url", "")} for l in b.get("links", [])]},
           "work": [], "projects": [], "skills": [], "education": [], "certificates": [], "languages": []}

    def highlights(e):
        return [x["text"] for x in (e.get("bullets") or e.get("accomplishments") or [])]
    for e in d.get("experience", []):
        out["work"].append({"name": e.get("company", ""), "position": e.get("title", ""), "startDate": str(e.get("start", "")), "endDate": str(e.get("end") or ""), "highlights": highlights(e)})
    for e in d.get("projects", []):
        out["projects"].append({"name": e.get("name", ""), "description": e.get("description", ""), "url": e.get("url", ""), "highlights": highlights(e)})
    for s in d.get("skills", []):
        out["skills"].append({"name": s if isinstance(s, str) else s["name"], "keywords": [] if isinstance(s, str) else s.get("aliases", [])})
    for e in d.get("education", []):
        out["education"].append({"institution": e.get("institution", ""), "studyType": e.get("degree", ""), "area": e.get("field", ""), "startDate": e.get("start", ""), "endDate": e.get("end", "")})
    for c in d.get("certifications", []):
        out["certificates"].append({"name": c.get("name", ""), "issuer": c.get("issuer", ""), "date": c.get("date", "")})
    for l in d.get("languages", []):
        out["languages"].append({"language": l.get("name", ""), "fluency": l.get("level", "")})
    Path(a.out).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote", a.out)


if __name__ == "__main__":
    main()
