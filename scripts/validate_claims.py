#!/usr/bin/env python3
"""Verify every claim in a tailored cv.json against profile.json. Exit 1 on any error.

Usage: python3 validate_claims.py cv.json profile.json
Checks: bullet source ids exist; numbers in a bullet appear in the source; titles/companies/dates match;
listed skills exist in the profile; certifications and education exist. Standard library only.
"""
import json, re, sys
from pathlib import Path

NUM = re.compile(r"\d[\d,.]*\s?(?:%|[kKmMbB]\b)?")


def nums(s):
    return {re.sub(r"[\s,]", "", n).lower().rstrip(".") for n in NUM.findall(s)}


def main():
    cv = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    prof = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    errors, warns = [], []

    acc = {}
    roles = {}
    for sec in ("experience", "projects"):
        for e in prof.get(sec, []):
            roles[e["id"]] = e
            for a in e.get("accomplishments", []):
                acc[a["id"]] = (e, a)
    skills = set()
    for s in prof.get("skills", []):
        skills.add(s["name"].lower())
        skills.update(x.lower() for x in s.get("aliases", []))
    for e, a in acc.values():
        skills.update(x.lower() for x in a.get("skills", []))

    for sec in ("experience", "projects"):
        for e in cv.get(sec, []):
            ref = e.get("ref")
            role = roles.get(ref)
            if not role:
                errors.append(f"{sec}: unknown ref '{ref}'")
                continue
            if sec == "experience":
                for f in ("company", "start", "end"):
                    if e.get(f) and str(e[f]) != str(role.get(f, "")):
                        errors.append(f"{ref}: {f} '{e[f]}' != profile '{role.get(f)}'")
                if e.get("title") and e["title"].lower() != role.get("title", "").lower() and e["title"] != role.get("title_alt", ""):
                    errors.append(f"{ref}: title '{e['title']}' != profile '{role.get('title')}' (use title_alt for approved variants)")
            for b in e.get("bullets", []):
                src = acc.get(b.get("source"))
                if not src or src[0]["id"] != ref:
                    errors.append(f"{ref}: bullet source '{b.get('source')}' missing or from another role: {b['text'][:50]}")
                    continue
                extra = nums(b["text"]) - nums(src[1]["text"] + " " + " ".join(map(str, src[1].get("metrics", []))))
                if extra:
                    errors.append(f"{ref}: numbers not in evidence {sorted(extra)} in: {b['text'][:60]}")

    for s in cv.get("skills", []):
        if s.lower() not in skills:
            errors.append(f"skill '{s}' not in profile")
    prof_certs = {c["name"].lower() for c in prof.get("certifications", [])}
    for c in cv.get("certifications", []):
        if c["name"].lower() not in prof_certs:
            errors.append(f"certification '{c['name']}' not in profile")
    prof_edu = {(e.get("institution", "").lower(), e.get("degree", "").lower()) for e in prof.get("education", [])}
    for e in cv.get("education", []):
        if (e.get("institution", "").lower(), e.get("degree", "").lower()) not in prof_edu:
            errors.append(f"education '{e.get('degree')}' at '{e.get('institution')}' not in profile")
    low = json.dumps(cv, ensure_ascii=False).lower()
    for w in ("expert in everything", "guru", "ninja", "rockstar"):
        if w in low:
            warns.append(f"inflated wording: '{w}'")

    for w in warns:
        print("[WARN]", w)
    for e in errors:
        print("[ERROR]", e)
    print(f"{len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
