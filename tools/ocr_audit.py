#!/usr/bin/env python3
"""Audit *possible* OCR errors in Bassett letter candidates; do not alter source.

Heuristics are deliberately overinclusive. Flags request human review; they
are not evidence that a document is invalid or its wording is incorrect.
"""
from __future__ import annotations
from collections import Counter
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "app/src/main/assets/archive/corpus.json"
REPORT_DIR = ROOT / "reports"

LETTER_DIGIT = re.compile(r"\b[A-Za-z]{2,}[0-9]+[A-Za-z]{2,}\b")
MIDWORD_SYMBOL = re.compile(r"\b[A-Za-z]{2,}[$@#^*|~+][A-Za-z0-9$@#^*|~+.\-]{0,12}\b")
INTERRUPTED_WORD = re.compile(r"(?i)[a-z]{3,}-[ \t]*(?:\n[ \t]*){2,5}[1-9][0-9]?[ \t]+[A-Za-z]")
EMBEDDED_HEADING = re.compile(r"(?mi)^[ \t]*(?:To [A-Z][A-Za-z .,']{6,60}|[A-Z][A-Za-z .,'-]{6,60} TO JACKSON)[.?! \t]*$")
JUNK_LINE = re.compile(r"(?m)^[ \t]*(?:[_.:*=~\- ]{4,}|[A-Za-z0-9.,:$%/ +]{9,40}(?:\s\.\.\s){2,})[ \t]*$")

def audit_letter(letter):
    raw = letter.get("original", "")
    readable = letter.get("readable", "")
    flags = []
    # Scan the untouched OCR too: the display copy now hides unmistakably
    # garbled words behind [unclear OCR], but the review queue must retain
    # the reason they were flagged for inspection.
    if LETTER_DIGIT.search(raw) or LETTER_DIGIT.search(readable):
        flags.append("letter_digit_fusion")
    if MIDWORD_SYMBOL.search(raw) or MIDWORD_SYMBOL.search(readable):
        flags.append("symbol_in_word")
    if INTERRUPTED_WORD.search(raw):
        flags.append("word_interrupted_by_footnote")
    if len(EMBEDDED_HEADING.findall(raw)) > 1:
        flags.append("possible_multiple_documents")
    if len(raw) >= 35000 or "OCR extraction truncated" in raw:
        flags.append("truncated_extraction")
    elif len(raw) > 14000:
        flags.append("unusually_long_extraction")
    if len(letter.get("ocrFrom", letter.get("from", ""))) > 65 or len(letter.get("ocrTo", letter.get("to", ""))) > 65:
        flags.append("suspicious_correspondent_heading")
    if "[unclear OCR]" in readable:
        flags.append("unclear_scan_text")
    return flags

def build_report(corpus=CORPUS):
    letters=json.loads(Path(corpus).read_text(encoding="utf-8"))["letters"]
    records=[]
    counts=Counter()
    for d in letters:
        flags=audit_letter(d)
        if flags:
            counts.update(flags)
            text=d.get("readable","")
            snippet=text[:280].replace("\n"," ")
            records.append({
              "id":d["id"],"date":d["date"],"from":d["from"],"to":d["to"],
              "volume":d.get("volume"),"page_approximate":d.get("page"),
              "flags":";".join(flags),"snippet":snippet,
            })
    records.sort(key=lambda r:(-len(r["flags"].split(";")),r["date"],r["id"]))
    REPORT_DIR.mkdir(parents=True,exist_ok=True)
    path=REPORT_DIR/"ocr_review.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["id","date","from","to","volume","page_approximate","flags","snippet"])
        writer.writeheader()
        writer.writerows(records)
    info={"total_letter_candidates":len(letters),"flagged_for_review":len(records),"flag_counts":dict(sorted(counts.items())),"not_verified":"Heuristic flags only; review scans before amending source text."}
    (REPORT_DIR/"ocr_review_summary.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    print("OCR_REVIEW_AUDIT_OK",len(records),"of",len(letters),"candidates flagged",dict(counts))
    return info

if __name__=="__main__":
    build_report()
