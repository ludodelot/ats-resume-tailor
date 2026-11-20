# What ATS actually do (evidence vs myth)

Confidence: [vendor docs / recruiter reports] unless marked inference. Re-verify, vendors change.

- ATS parse text out of the file, then store fields (name, titles, employers, dates, skills). A human recruiter usually searches and reads the result. Large "auto-reject by score" pipelines exist but are less universal than the myth suggests.
- PDF and DOCX both work **if they contain real text**. Image-only or scanned PDFs fail.
- Things that commonly break parsing: multi-column layouts, tables, text boxes, text in headers/footers, icons, graphics, unusual fonts.
- Many systems combine keyword/Boolean filters on hard requirements (degree, certification, location, work authorisation) with semantic ranking. Design for both: exact phrases from the posting for real skills, plus clear context.
- Hidden text and keyword stuffing are detectable and damage trust. Don't.
- A "score" shown by third-party checkers is not the employer's ATS score. Treat any number as a proxy. [inference]

Safe format: single column, name and contact in the body, standard headings (Experience, Education, Skills), full job titles, consistent dates, Arial or Times 10.5-12 pt, no graphics.
