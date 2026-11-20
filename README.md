# ATS Resume Tailor

**An Agent Skill that generates ATS-friendly CVs and resumes tailored to each job posting, from a living career profile, with every claim verified. No fabrication, no keyword tricks.**

Works with Claude Code, Codex, Cursor and any agent that loads `SKILL.md` skills.

## Why

Generic CVs miss keywords. Generic AI CVs invent things. This skill keeps one private **master profile** of everything you have really done, then for each job it selects, rewrites and scores only what is true, and refuses to add what is not.

## Features

- **Living career profile.** Grows from old CVs (PDF/DOCX), GitHub repos, LinkedIn export, performance reviews.
- **Job analysis.** Extracts required vs preferred keywords from a posting.
- **Transparent match score.** A simple, documented rubric. Shows matched terms and honest gaps.
- **Claim verification.** Every bullet points to an accomplishment id. Numbers, skills, titles, companies and dates are checked against the profile (exit 1 on any mismatch).
- **ATS-safe output.** Single column, standard headings, real text. HTML, Markdown and PDF.
- **Format checker.** Flags missing contact info, non-standard headings, multi-column layouts, decorative glyphs, page count.
- **Region presets.** US/UK, EU, DACH, LatAm conventions for photo and personal data.
- **Application log.** Which evidence went into which application.
- **Private by default.** `profile/`, `jobs/` and `out/` are git-ignored. Nothing leaves your machine except the GitHub username you choose to ingest.

## Install

Claude Code:

```bash
git clone https://github.com/ludodelot/ats-resume-tailor ~/.claude/skills/ats-resume-tailor
```

## Quick start

Try the scripts on the bundled fake data:

```bash
python3 scripts/extract_keywords.py examples/job.example.txt --profile examples/profile.example.json > /tmp/kw.json
python3 scripts/score_match.py /tmp/kw.json examples/profile.example.json --cv examples/cv.example.json
python3 scripts/validate_claims.py examples/cv.example.json examples/profile.example.json
python3 scripts/render_cv.py examples/cv.example.json --out /tmp/cv --region us
python3 scripts/check_ats_format.py /tmp/cv/cv.pdf
```

With your agent: *"Use ats-resume-tailor. Build my profile from `~/cv_old.pdf` and my GitHub `<user>`, then tailor a CV for this job: `<paste posting>`."*

## Scripts (Python 3, standard library; optional tools noted)

| Script | Purpose | Optional |
|---|---|---|
| `ingest_sources.py` | PDF, DOCX, GitHub, LinkedIn to readable sources | `pdftotext` (poppler) or `pypdf`, `python-docx` |
| `extract_keywords.py` | Required / preferred keywords from a job posting | |
| `score_match.py` | Transparent match score and gaps | |
| `validate_claims.py` | Verify every bullet against the profile | |
| `render_cv.py` | HTML, Markdown, PDF | `weasyprint` or Chrome for PDF |
| `check_ats_format.py` | Heuristic parseability check | `pdftotext` or `pypdf` |

## Honesty rules

The skill never invents skills, numbers, titles or employers, never hides text, and never stuffs keywords. When a job asks for something you lack, it tells you and asks whether it is true.

## Limits

No tool can reproduce a real employer's ATS scoring. The match score is a proxy. See `references/ats-facts.md` for what is evidence and what is myth.

## Related ideas

ATS resume optimizer, tailored CV generator, AI resume builder, job description keyword extraction, JSON Resume, Claude Code skill, resume parser check.

## Contributing

Issues and PRs welcome: new region presets, ESCO/O*NET skill mapping, DOCX renderer, more parser tests.

## License

MIT. See [LICENSE](LICENSE).
