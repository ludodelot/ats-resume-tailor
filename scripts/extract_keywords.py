#!/usr/bin/env python3
"""Extract weighted keywords from a job description.

Usage: python3 extract_keywords.py JD.txt [--profile profile.json] [--top 40] > keywords.json
Standard library only. Output is a starting point: review it with judgment.
"""
import argparse, json, re
from collections import Counter
from pathlib import Path

STOP = set("""a an the and or of to in for with on at by from as is are be been being this that these those it its
we you your our their they will can may must should would could have has had do does did not no yes more most
less least such than then also etc per via into over under about across within without including include
experience work working role team teams company job position candidate ability strong years year
responsibilities requirements qualifications skills knowledge looking join us who what when where how
new help make use using build building develop developing""".split())
REQ_HDR = re.compile(r"(requirements?|qualifications?|must.have|what you.ll need|what we.re looking for|required|you have)", re.I)
PREF_HDR = re.compile(r"(nice.to.have|preferred|bonus|plus|desirable|ideally)", re.I)
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9+#.\-/]*[A-Za-z0-9+#]|[A-Za-z]")


def norm(t):
    return t.lower().strip(".-/")


def candidates(tokens):
    for n in (1, 2, 3):
        for i in range(len(tokens) - n + 1):
            g = tokens[i:i + n]
            if g[0] in STOP or g[-1] in STOP or any(len(x) < 2 for x in g):
                continue
            if n > 1 and any(x in STOP for x in g[1:-1]) and n == 3:
                pass
            yield " ".join(g)


LEAD = re.compile(r"^(\d+\+?\s*years?(\s+of)?(\s+(professional|relevant|hands-on))?(\s+experience)?(\s+(as|in|with|using))?|experience\s+(with|in|of|using)|(advanced|strong|solid|proven|excellent|good|working|deep)\s+(knowledge of|experience (with|in)|proficiency in|understanding of)?|proficiency\s+(in|with)|knowledge\s+of|familiarity\s+with|ability\s+to|an?\s+)\s*", re.I)
SPLIT = re.compile(r",|;|/|\s+and\s+|\s+or\s+|\s+&\s+", re.I)


def phrases(line):
    line = re.sub(r"^[\-*\u2022\d.)\s]+", "", line).strip().rstrip(".")
    out = []
    for piece in SPLIT.split(line):
        for _ in range(3):
            new = LEAD.sub("", piece.strip())
            if new == piece:
                break
            piece = new
        piece = piece.strip(" .:")
        words = piece.split()
        if 1 <= len(words) <= 4 and not all(norm(w) in STOP for w in words) and norm(words[0]) not in STOP:
            out.append(norm(piece) if len(words) > 1 else norm(piece))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jd")
    ap.add_argument("--profile")
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()
    text = Path(a.jd).read_text(encoding="utf-8", errors="replace")
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    req, pref, other = [], [], []
    title = lines[0] if lines and len(lines[0]) < 70 else ""
    if title:
        req.append(norm(title))
    section = "body"
    body_counter = Counter()
    for s in lines[1:]:
        if len(s) < 60 and (s.endswith(":") or s.isupper() or s.startswith("#")):
            section = "req" if REQ_HDR.search(s) else "pref" if PREF_HDR.search(s) else "body"
            continue
        if section in ("req", "pref"):
            (req if section == "req" else pref).extend(phrases(s))
        toks = [norm(t) for t in TOKEN.findall(s)]
        for c in candidates(toks):
            body_counter[c] += 1
        for raw in TOKEN.findall(s):
            if re.search(r"[A-Z].*[A-Z]|[+#.]|\d", raw) and norm(raw) not in STOP and len(raw) > 1:
                body_counter[norm(raw)] += 2

    seen = set(req) | set(pref)
    for c, n in body_counter.most_common():
        if n >= 2 and c not in seen and not any(c in x for x in seen if " " in x):
            other.append(c)
            seen.add(c)
        if len(other) >= 10:
            break

    def dedupe(xs):
        r = []
        for x in xs:
            if x not in r:
                r.append(x)
        return r
    req, pref = dedupe(req), [x for x in dedupe(pref) if x not in req]
    profile_hits = []
    if a.profile:
        prof = json.loads(Path(a.profile).read_text(encoding="utf-8"))
        low = text.lower()
        for sk in prof.get("skills", []):
            names = [sk["name"]] + sk.get("aliases", [])
            if any(re.search(r"(?<!\w)" + re.escape(n.lower()) + r"(?!\w)", low) for n in names):
                profile_hits.append(sk["name"])
    out = {"required": req[:a.top], "preferred": pref[:a.top], "other": other, "profile_skills_in_jd": profile_hits}
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
