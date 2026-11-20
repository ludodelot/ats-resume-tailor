# Schemas

## profile/profile.json (master record, private)

```json
{
  "basics": {"name": "", "label": "", "email": "", "phone": "", "location": "", "nationality": "", "links": [{"label": "GitHub", "url": ""}]},
  "summary": "optional fact-based summary",
  "experience": [{
    "id": "exp-acme-2022", "title": "", "title_alt": "approved variant title", "company": "", "location": "",
    "start": "2022-03", "end": null,
    "accomplishments": [{"id": "acc-acme-1", "text": "true, specific statement with the real numbers", "metrics": ["35%"], "skills": ["python"]}]
  }],
  "projects": [{"id": "proj-x", "name": "", "url": "", "description": "", "accomplishments": []}],
  "skills": [{"name": "JavaScript", "aliases": ["JS"], "level": "advanced"}],
  "education": [{"institution": "", "degree": "", "field": "", "start": "", "end": ""}],
  "certifications": [{"name": "", "issuer": "", "date": ""}],
  "languages": [{"name": "English", "level": "C1"}]
}
```

Rules: stable ids, evidence-level facts, one accomplishment per measurable outcome, no embellishment.

## out/<company>-<role>/cv.json (tailored, disposable)

```json
{
  "language": "en",
  "basics": {"name": "", "label": "target title", "email": "", "phone": "", "location": "", "links": []},
  "summary": "2-3 lines",
  "experience": [{"ref": "exp-acme-2022", "title": "", "company": "", "start": "2022-03", "end": null,
                  "bullets": [{"text": "XYZ-style rewrite", "source": "acc-acme-1"}]}],
  "projects": [], "skills": ["JavaScript"], "education": [], "certifications": [], "languages": []
}
```

`ref` and `source` must exist in the profile. `validate_claims.py` enforces it.
