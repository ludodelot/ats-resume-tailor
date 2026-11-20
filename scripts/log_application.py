#!/usr/bin/env python3
"""Append an application to out/applications.csv (date, company, role, score, file, evidence ids).

Usage: python3 log_application.py --company Acme --role "Data Analyst" --cv out/acme/cv.json [--score 82.5] [--log out/applications.csv]
Evidence ids are read from the bullets' `source` fields in cv.json.
"""
import argparse, csv, json
from datetime import date
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--cv", required=True)
    ap.add_argument("--score", default="")
    ap.add_argument("--log", default="out/applications.csv")
    a = ap.parse_args()
    cv = json.loads(Path(a.cv).read_text(encoding="utf-8"))
    ids = sorted({b["source"] for sec in ("experience", "projects") for e in cv.get(sec, []) for b in e.get("bullets", [])})
    log = Path(a.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "company", "role", "score", "cv", "evidence_ids", "status"])
        w.writerow([date.today().isoformat(), a.company, a.role, a.score, a.cv, ";".join(ids), "applied"])
    print(f"Logged {a.company} / {a.role} ({len(ids)} evidence ids) to {log}")


if __name__ == "__main__":
    main()
