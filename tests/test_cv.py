import json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S, EX = ROOT / "scripts", ROOT / "examples"


def run(script, *args):
    r = subprocess.run([sys.executable, str(S / script), *map(str, args)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class CVTests(unittest.TestCase):
    def test_keywords(self):
        code, out = run("extract_keywords.py", EX / "job.example.txt")
        d = json.loads(out)
        for k in ("sql", "python", "power bi"):
            self.assertIn(k, d["required"])
        self.assertIn("dbt", d["preferred"])

    def test_score_reports_gaps_and_uses_taxonomy(self):
        with tempfile.TemporaryDirectory() as t:
            kw = Path(t) / "kw.json"
            kw.write_text(json.dumps({"required": ["javascript", "postgresql", "snowflake"], "preferred": [], "other": []}))
            code, out = run("score_match.py", kw, EX / "profile.example.json", "--json")
            d = json.loads(out)["profile"]
            self.assertIn("javascript", d["matched"])      # profile says "JS"
            self.assertIn("postgresql", d["matched"])      # alias of SQL
            self.assertEqual([g["term"] for g in d["gaps"]], ["snowflake"])

    def test_validate_passes_and_blocks_fabrication(self):
        code, _ = run("validate_claims.py", EX / "cv.example.json", EX / "profile.example.json")
        self.assertEqual(code, 0)
        cv = json.loads((EX / "cv.example.json").read_text())
        cv["experience"][0]["bullets"][0]["text"] = "Cut reporting time by 50%"
        cases = {"number": cv}
        cv2 = json.loads((EX / "cv.example.json").read_text()); cv2["skills"].append("Snowflake")
        cv3 = json.loads((EX / "cv.example.json").read_text()); cv3["experience"][0]["bullets"][0]["source"] = "acc-nope"
        cv4 = json.loads((EX / "cv.example.json").read_text()); cv4["experience"][0]["company"] = "Other Corp"
        for name, c in {"number": cv, "skill": cv2, "source": cv3, "company": cv4}.items():
            with tempfile.TemporaryDirectory() as t:
                f = Path(t) / "cv.json"; f.write_text(json.dumps(c))
                code, out = run("validate_claims.py", f, EX / "profile.example.json")
                self.assertEqual(code, 1, f"{name}: {out}")

    def test_render_and_format_check(self):
        with tempfile.TemporaryDirectory() as t:
            run("render_cv.py", EX / "cv.example.json", "--out", t, "--no-pdf")
            code, out = run("check_ats_format.py", Path(t) / "cv.html")
            self.assertEqual(code, 0, out)
            self.assertNotIn("heading", out.lower())

    def test_docx_export_is_valid_zip_with_text(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "cv.docx"
            code, out = run("export_docx.py", EX / "cv.example.json", "--out", f)
            self.assertEqual(code, 0, out)
            with zipfile.ZipFile(f) as z:
                self.assertIsNone(z.testzip())
                xml = z.read("word/document.xml").decode()
            self.assertIn("Alex Rivera", xml)
            self.assertIn("Heading1", xml)
            self.assertNotIn("<w:tbl>", xml)

    def test_merge_dedupes_and_flags_conflicts(self):
        with tempfile.TemporaryDirectory() as t:
            prof = Path(t) / "p.json"; prof.write_text((EX / "profile.example.json").read_text())
            new = {"experience": [{"title": "Data Analyst", "company": "Acme Retail", "start": "2022-03", "end": "2025-01",
                                   "accomplishments": [{"text": "Built Power BI dashboards for 12 stores that cut weekly reporting time by 35%"},
                                                       {"text": "Mentored 3 junior analysts"}]}],
                   "skills": [{"name": "Python"}, {"name": "dbt"}]}
            n = Path(t) / "n.json"; n.write_text(json.dumps(new))
            code, out = run("merge_profile.py", prof, n)
            self.assertIn("CONFLICT", out)           # end date differs
            self.assertIn("Mentored 3 junior", out)  # new accomplishment
            self.assertIn("skill: dbt", out)
            self.assertNotIn("+ Built Power BI", out)  # duplicate skipped

    def test_log_application(self):
        with tempfile.TemporaryDirectory() as t:
            log = Path(t) / "a.csv"
            run("log_application.py", "--company", "Acme", "--role", "Analyst", "--cv", EX / "cv.example.json", "--log", log)
            self.assertIn("acc-acme-1", log.read_text())

    def test_jsonresume_export(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "r.json"
            run("export_jsonresume.py", EX / "profile.example.json", "--out", out)
            d = json.loads(out.read_text())
            self.assertEqual(d["basics"]["name"], "Alex Rivera")
            self.assertEqual(len(d["work"]), 2)


if __name__ == "__main__":
    unittest.main()
