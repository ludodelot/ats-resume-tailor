#!/usr/bin/env python3
"""Merge new evidence (a partial profile.json) into the master profile without duplicates.

Usage: python3 merge_profile.py profile.json new.json [--apply]
Dry run by default: prints what would be added or conflicts. Roles match on (company, start year).
Accomplishments match on text similarity >= 0.8. Conflicts (different end date, title) are reported, never overwritten.
"""
import argparse, difflib, json, re, sys
from pathlib import Path


def key(role):
    return (re.sub(r"\W+", "", role.get("company", role.get("name", "")).lower()), str(role.get("start", ""))[:4])


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:24]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("new")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    base = json.loads(Path(a.profile).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    added, conflicts = [], []
    for sec in ("experience", "projects"):
        have = {key(r): r for r in base.setdefault(sec, [])}
        for r in new.get(sec, []):
            k = key(r)
            if k not in have:
                r.setdefault("id", f"{'exp' if sec == 'experience' else 'proj'}-{slug(r.get('company', r.get('name', 'x')))}-{k[1]}")
                for i, acc in enumerate(r.get("accomplishments", []), 1):
                    acc.setdefault("id", f"acc-{slug(r.get('company', r.get('name', 'x')))}-{i}")
                base[sec].append(r)
                added.append(f"{sec}: new role/project {r.get('company', r.get('name'))} {k[1]}")
                continue
            cur = have[k]
            for f in ("title", "end"):
                if r.get(f) is not None and str(r.get(f)) != str(cur.get(f)):
                    conflicts.append(f"{cur['id']}: {f} differs: profile '{cur.get(f)}' vs new '{r.get(f)}'")
            existing = cur.setdefault("accomplishments", [])
            for acc in r.get("accomplishments", []):
                best = max((difflib.SequenceMatcher(None, acc["text"].lower(), e["text"].lower()).ratio() for e in existing), default=0)
                if best >= 0.8:
                    continue
                acc.setdefault("id", f"acc-{cur['id'].split('-', 1)[-1]}-{len(existing) + 1}")
                existing.append(acc)
                added.append(f"{cur['id']}: + {acc['text'][:60]}")
    names = {s["name"].lower() for s in base.setdefault("skills", [])}
    for s in new.get("skills", []):
        if s["name"].lower() not in names:
            base["skills"].append(s)
            added.append(f"skill: {s['name']}")
    for sec, kf in (("education", "degree"), ("certifications", "name"), ("languages", "name")):
        have = {(x.get(kf, "")).lower() for x in base.setdefault(sec, [])}
        for x in new.get(sec, []):
            if x.get(kf, "").lower() not in have:
                base[sec].append(x)
                added.append(f"{sec}: {x.get(kf)}")
    print(f"{len(added)} addition(s), {len(conflicts)} conflict(s)")
    for x in added:
        print("  +", x)
    for x in conflicts:
        print("  ! CONFLICT", x, "(ask the user)")
    if a.apply:
        Path(a.profile).write_text(json.dumps(base, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Applied.")
    else:
        print("Dry run. Re-run with --apply to write.")
    sys.exit(0)


if __name__ == "__main__":
    main()
