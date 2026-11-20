#!/usr/bin/env python3
"""Transparent keyword match score between job keywords and a profile (or a tailored CV).

Usage: python3 score_match.py keywords.json profile.json [--cv cv.json] [--json]
Score = 100 * (2*required_hit + 1*preferred_hit + 0.5*other_hit) / (2*req + pref + 0.5*other)
Standard library only.
"""
import argparse, json, re
from pathlib import Path

def _load_syn():
    syn = {}
    tax = Path(__file__).resolve().parent.parent / "references" / "skills_taxonomy.json"
    if tax.exists():
        for sk in json.loads(tax.read_text(encoding="utf-8"))["skills"]:
            for al in sk["aliases"]:
                syn[al.lower()] = sk["name"].lower()
    return syn


SYN = _load_syn()


def canon(s):
    s = s.lower().strip()
    return SYN.get(s, s)


def text_of_profile(p):
    parts = [p.get("summary", "")]
    for sk in p.get("skills", []):
        parts += [sk["name"]] + sk.get("aliases", [])
    for sec in ("experience", "projects"):
        for e in p.get(sec, []):
            parts += [e.get("title", ""), e.get("name", ""), e.get("company", ""), e.get("description", "")]
            parts += [a.get("text", "") for a in e.get("accomplishments", [])]
            parts += [s for a in e.get("accomplishments", []) for s in a.get("skills", [])]
    for c in p.get("certifications", []):
        parts.append(c.get("name", ""))
    for ed in p.get("education", []):
        parts += [ed.get("degree", ""), ed.get("field", "")]
    return " ".join(parts)


def text_of_cv(cv):
    parts = [cv.get("summary", ""), " ".join(cv.get("skills", []))]
    for e in cv.get("experience", []):
        parts += [e.get("title", ""), e.get("company", "")] + [b["text"] for b in e.get("bullets", [])]
    for e in cv.get("projects", []):
        parts += [e.get("name", "")] + [b["text"] for b in e.get("bullets", [])]
    for c in cv.get("certifications", []):
        parts.append(c.get("name", ""))
    return " ".join(parts)


def has(term, corpus):
    t = canon(term)
    variants = {t, term.lower()} | {k for k, v in SYN.items() if v == t}
    return any(re.search(r"(?<![\w+#])" + re.escape(v) + r"(?![\w+#])", corpus) for v in variants)


def score(kw, corpus):
    groups = (("required", 2.0), ("preferred", 1.0), ("other", 0.5))
    num = den = 0.0
    matched, missing = [], []
    for g, w in groups:
        for term in kw.get(g, []):
            den += w
            if has(term, corpus):
                num += w
                matched.append(term)
            else:
                missing.append({"term": term, "group": g})
    return (round(100 * num / den, 1) if den else 0.0), matched, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords")
    ap.add_argument("profile")
    ap.add_argument("--cv")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    kw = json.loads(Path(a.keywords).read_text(encoding="utf-8"))
    prof = json.loads(Path(a.profile).read_text(encoding="utf-8"))
    res = {}
    s, m, miss = score(kw, text_of_profile(prof).lower())
    res["profile"] = {"score": s, "matched": m, "gaps": miss}
    if a.cv:
        cv = json.loads(Path(a.cv).read_text(encoding="utf-8"))
        s2, m2, miss2 = score(kw, text_of_cv(cv).lower())
        res["cv"] = {"score": s2, "matched": m2, "gaps": miss2}
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    for k, v in res.items():
        print(f"== {k.upper()} match: {v['score']}%")
        print("   matched:", ", ".join(v["matched"]) or "-")
        print("   gaps   :", ", ".join(f"{g['term']} ({g['group']})" for g in v["gaps"]) or "none")
    print("\nGaps are NOT to be added unless the user confirms they are true.")


if __name__ == "__main__":
    main()
