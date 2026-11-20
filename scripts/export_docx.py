#!/usr/bin/env python3
"""Export cv.json to an ATS-safe .docx using only the standard library (zipfile + OOXML).

Usage: python3 export_docx.py cv.json --out cv.docx
Single column, built-in Heading styles, real bullets, Arial 11pt. No tables, images or text boxes.
"""
import argparse, json, zipfile
from pathlib import Path
from xml.sax.saxutils import escape as E

LAB = {"en": ("Summary", "Experience", "Projects", "Skills", "Education", "Certifications", "Languages", "Present"),
       "es": ("Resumen", "Experiencia", "Proyectos", "Habilidades", "Formación", "Certificaciones", "Idiomas", "Actualidad")}


def para(text, style=None, bold=False, size=None, bullet=False):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if bullet:
        ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
    rpr = ("<w:b/>" if bold else "") + (f'<w:sz w:val="{size}"/>' if size else "")
    return f'<w:p><w:pPr>{ppr}</w:pPr><w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{E(str(text))}</w:t></w:r></w:p>'


def build(cv):
    S, X, P, K, ED, C, L, PRES = LAB.get(cv.get("language", "en"), LAB["en"])
    b = cv.get("basics", {})
    body = [para(b.get("name", ""), "Title")]
    if b.get("label"):
        body.append(para(b["label"]))
    contact = [b.get(k) for k in ("email", "phone", "location")] + [l.get("url", "") for l in b.get("links", [])]
    body.append(para(" | ".join(c for c in contact if c)))
    if cv.get("summary"):
        body += [para(S, "Heading1"), para(cv["summary"])]
    for key, label in (("experience", X), ("projects", P)):
        if cv.get(key):
            body.append(para(label, "Heading1"))
            for it in cv[key]:
                name = it.get("title") or it.get("name", "")
                org = it.get("company", "")
                dates = f"{it.get('start','')} - {it.get('end') or PRES}" if it.get("start") else ""
                body.append(para(" | ".join(x for x in (f"{name}, {org}" if org else name, dates) if x), bold=True))
                body += [para(bl["text"], bullet=True) for bl in it.get("bullets", [])]
    if cv.get("skills"):
        body += [para(K, "Heading1"), para(", ".join(cv["skills"]))]
    if cv.get("education"):
        body.append(para(ED, "Heading1"))
        body += [para(f"{e.get('degree','')}, {e.get('institution','')} ({e.get('start','')}-{e.get('end','')})") for e in cv["education"]]
    if cv.get("certifications"):
        body.append(para(C, "Heading1"))
        body += [para(c["name"], bullet=True) for c in cv["certifications"]]
    if cv.get("languages"):
        body += [para(L, "Heading1"), para(", ".join(f"{l['name']} ({l.get('level','')})" for l in cv["languages"]))]
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            + "".join(body) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr></w:body></w:document>')


CT = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/></Types>'
RELS = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
DOCRELS = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/></Relationships>'
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
STYLES = f'<?xml version="1.0" encoding="UTF-8"?><w:styles {W}><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="21"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="60"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="40"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="60"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:caps/><w:sz w:val="24"/></w:rPr></w:style></w:styles>'
NUM = f'<?xml version="1.0" encoding="UTF-8"?><w:numbering {W}><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="-"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="260"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cv = json.loads(Path(a.cv).read_text(encoding="utf-8"))
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOCRELS)
        z.writestr("word/document.xml", build(cv))
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/numbering.xml", NUM)
    print("Wrote", a.out)


if __name__ == "__main__":
    main()
