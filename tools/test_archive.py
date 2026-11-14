#!/usr/bin/env python3
"""Integrity tests for the downloaded, *unverified* OCR archive.

Does not certify that an OCR segment equals a historical manuscript.
"""
import collections
import datetime as dt
import json
from pathlib import Path

p=Path(__file__).resolve().parents[1]/"app/src/main/assets/archive/corpus.json"
data=json.loads(p.read_text(encoding="utf-8"))
letters=data["letters"]
ids={x["id"] for x in letters}
assert len(letters)>=1800, f"Too few letter candidates: {len(letters)}"
assert len(ids)==len(letters), "Duplicate document identifiers"
assert set(map(int,data["volumeCounts"]))==set(range(1,7)), "Missing volume"
assert sum(data["volumeCounts"].values())==len(letters),"Volume sum mismatch"
assert all(x["source"].startswith("https://archive.org/") for x in letters)
assert all(len(x["original"])>130 for x in letters),"Empty raw OCR"
assert all(x["original"] for x in letters)
assert all(x["status"]=="ocr" and x["sourceChecked"] is False for x in letters)
assert all(x.get("textQuality","").startswith("uncorrected OCR") for x in letters)
assert all(x.get("ocrFrom") and x.get("ocrTo") for x in letters)
assert all(x["replyToId"] in ids for x in letters if x.get("replyToId"))
for x in letters:
    dt.date.fromisoformat(x["date"])
    assert len(x["from"])<115 and len(x["to"])<115
    if x.get("modern"):
        assert len(x["modern"])>100 and "human-authored" in x["modernType"]
first=sorted(letters,key=lambda x:x["date"])[0]
assert first["date"]=="1788-08-12",first["date"]
assert first["to"]=="Waightstill Avery", first["to"]
assert first["modern"],"The earliest letter should have an English rendering"
for d,to in [("1789-02-13","Daniel Smith"),("1791-01-20","Daniel Smith"),
             ("1793-01-30","John McKee"),("1794-05-16","John McKee")]:
    matches=[x for x in letters if x["date"]==d and x["to"]==to and x["from"]=="Andrew Jackson"]
    assert matches,(d,to)
    assert matches[0]["modern"],f"Missing early letter modern English: {d} to {to}"
assert sum(x["from"]=="Andrew Jackson" for x in letters)>500
assert sum(x["to"]=="Andrew Jackson" for x in letters)>250
names=collections.Counter(x["to"] for x in letters)
assert names["John Coffee"]>=30, f"Coffee name variants not merged: {names['John Coffee']}"
assert names["Francis P. Blair"]>=25,f"Blair name variants not merged: {names['Francis P. Blair']}"
print("ARCHIVE_TESTS_OK",len(letters),"OCR candidates;",
      sum(bool(x["modern"]) for x in letters),"human-authored English renderings;",
      sum(bool(x.get("replyToId")) for x in letters),"tentative reply links")
