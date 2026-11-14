#!/usr/bin/env python3
"""Verify the OCR review queue and four new OCR-based reading aids."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from ocr_audit import audit_letter, build_report
from enrich_archive import normalize_person

docs=json.loads((ROOT/"app/src/main/assets/archive/corpus.json").read_text(encoding="utf-8"))["letters"]
by_id={d["id"]:d for d in docs}
samples={
 "basset-1-540838e26cba234":("1797-05-12","John McNairy",["friendship","letter"]),
 "basset-1-06465203ac3cd4e":("1798-01-25","Robert Hays",["France","Duck River"]),
 "basset-1-a440eef6ccfec38":("1798-06-24","William Cocke",["confidential","Senate"]),
 "basset-1-a52ce575b2cd058":("1798-06-24","John Sevier",["Irwin","treaty"]),
}
for uid,(date,person,words) in samples.items():
 d=by_id[uid]
 assert d["date"]==date and d["to"]==person
 assert d["modern"] and "human-authored" in d["modernType"]
 assert all(word.lower() in d["modern"].lower() for word in words)
 assert d["original"] and d["readable"]
 assert d["status"]=="ocr" and d["sourceChecked"] is False
 assert d["ocrFlags"]==audit_letter(d)

assert "referred to yourself, not to me" in by_id["basset-1-540838e26cba234"]["modern"]
assert normalize_person("John Oveertonn")=="John Overton"
assert normalize_person("Jouhn Coffee")=="John Coffee"
assert normalize_person("James K. Porx")=="James K. Polk"
assert normalize_person("Andrew J. Doneetson")=="Andrew J. Donelson"

assert all(d["ocrFlags"]==audit_letter(d) for d in docs)
flagged=[d for d in docs if d["ocrFlags"]]
assert len(flagged)>=120, "Suspiciously few OCR anomalies detected"
assert all(d.get("needsReview") for d in flagged)
report=build_report()
assert report["total_letter_candidates"]==len(docs)
assert report["flagged_for_review"]==len(flagged)
print("OCR_REVIEW_TESTS_OK",len(docs),"letters;",len(flagged),"review candidates; modern renditions",sum(bool(d["modern"]) for d in docs))
