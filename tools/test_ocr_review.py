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
 "basset-1-9e869e7885e988a":("1799-03-27","Andrew Jackson",["Mrs. Jackson","Hammond"]),
 "basset-1-aa7f6f673d41b47":("1803-10-02","John Sevier",["governor","pistols"]),
 "basset-1-32f7d2dac87b636":("1804-01-07","John Coffee",["$25,000","$40,000"]),
 "basset-1-a05bb0177e766ab":("1804-04-06","Mrs. Jackson",["My love","poverty"]),
 "basset-1-14ea21c23102551":("1806-11-12","Thomas Jefferson",["three regiments","twenty days"]),
 "basset-1-719ea98a3509ec1":("1806-11-17","Daniel Smith",["Burr","cannot confirm"]),
 "basset-1-3ba8d6b99e16837":("1806-12-19","Andrew Jackson",["Seth Pease","confidential"]),
}
for uid,(date,person,words) in samples.items():
 d=by_id[uid]
 assert d["date"]==date and d["to"]==person
 assert d["modern"] and "human-authored" in d["modernType"]
 assert all(word.lower() in d["modern"].lower() for word in words)
 assert d["original"] and d["readable"]
 assert d["status"]=="ocr" and d["sourceChecked"] is False
 assert d["ocrFlags"]==audit_letter(d)

additional_letters = {
 "basset-1-2083f23d6268b7f": ("1806-12-05", ["Mrs. Jackson", "defend"]),
 "basset-1-8f8443529d1e5b9": ("1806-12-29", ["Burr", "New Orleans"]),
 "basset-1-4a74504242600a4": ("1807-01-05", ["Gallatin", "mustered"]),
 "basset-1-14fb0396d9f7105": ("1807-01-09", ["Union", "Doctors Claiborne"]),
 "basset-1-0bef28e4e0ea918": ("1813-02-16", ["Fort Massac", "government property"]),
 "basset-1-ecb2fd48c873b49": ("1813-03-30", ["sick", "quartermaster"]),
 "basset-1-6d3b1f49751084d": ("1813-04-10", ["March 22", "New Orleans"]),
 "basset-1-56e95462436fc35": ("1813-10-19", ["Mr. Quarles", "relief"]),
 "basset-1-962a97d2936f7b8": ("1813-09-25", ["Huntsville", "Mobile"]),
}
for uid,(date,phrases) in additional_letters.items():
 d=by_id[uid]
 assert d["date"]==date
 assert d["modern"] and all(p.lower() in d["modern"].lower() for p in phrases)
 assert d["status"]=="ocr" and not d["sourceChecked"], "Do not label OCR as scan checked"
 assert "human-authored" in d["modernType"]
 assert len(d["original"])>200

assert "referred to yourself, not to me" in by_id["basset-1-540838e26cba234"]["modern"]
assert normalize_person("John Oveertonn")=="John Overton"
assert normalize_person("Jouhn Coffee")=="John Coffee"
assert normalize_person("John Cooffee")=="John Coffee"
assert normalize_person("W. C. C, Clarborne")=="William C. C. Claiborne"
assert normalize_person("James K. Porx")=="James K. Polk"
assert normalize_person("Major Witiaam B. Lewis")=="William B. Lewis"
assert normalize_person("Major Wil.Iam B. Lewits")=="William B. Lewis"
assert normalize_person("Andrew J. Doneetson")=="Andrew J. Donelson"

assert all(d["ocrFlags"]==audit_letter(d) for d in docs)
flagged=[d for d in docs if d["ocrFlags"]]
assert len(flagged)>=120, "Suspiciously few OCR anomalies detected"
assert all(d.get("needsReview") for d in flagged)
report=build_report()
assert report["total_letter_candidates"]==len(docs)
assert report["flagged_for_review"]==len(flagged)
print("OCR_REVIEW_TESTS_OK",len(docs),"letters;",len(flagged),"review candidates; modern renditions",sum(bool(d["modern"]) for d in docs))
