#!/usr/bin/env python3
"""Regression checks: preserve true OCR while removing recurring scan noise."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from clean_ocr import clean_ocr_text

def check(raw,expected,absent=()):
    cleaned=clean_ocr_text(raw)
    assert expected in cleaned,(expected,cleaned[:600])
    for token in absent:
        assert token not in cleaned,(token,cleaned[:600])

check("His opin-\n\n98 Correspondence of Andrew Jackson\n\nion was strong.","opinion",["98 Correspondence"])
check("It remained hon-\n\n120 Correspondence of Andrew Jackson\n\norable.","honorable")
check("He has the right to be-\n\nAdd Correspondence of Andrew Jackson\n\nstow the office.","bestow")
check("An old plate shows\nJackson\nCorrespondence of Andrew\nJackson\nNo further writing.","No further writing.",["Correspondence of Andrew"])
check("This is his opin98 Correspondence of Andrew Jackson\n\nion.","opinion")
check("The letter was read.\n\n8 Correspondence of Andrew Jackson\n\nThis answer followed.","This answer followed.",["Correspondence of Andrew Jackson"])
check("We spoke on Tuesday.\n\nOctober, 1837 515\n\nI wrote again.","I wrote again.",["October, 1837 515"])
check("John$-11called for me and paid $350.","John [unclear OCR] called",["John$-11called"])
check("I paid $350 for the horses and bought two good-looking animals.","$350")
check("His charector was questioned; he recd. a note.","charector")
check("A manuscript described Mary-Jane and a year of 1814.","Mary-Jane")
assert clean_ocr_text("John$-11called")==clean_ocr_text(clean_ocr_text("John$-11called"))
archive=ROOT/"app/src/main/assets/archive/corpus.json"
data=json.loads(archive.read_text(encoding="utf-8"))
docs=data["letters"]
assert len(docs)>1800
headers=sum("Correspondence of Andrew Jackson" in d["readable"] for d in docs)
assert headers==0, f"Too many page headers remain in reading copies: {headers}"
assert all(d["original"] and d["readable"] for d in docs)
assert all(d.get("ocrUnclearSpans",0)==d["readable"].count("[unclear OCR]") for d in docs)
flagged=sum(d.get("ocrUnclearSpans",0) for d in docs)
print("OCR_CLEAN_TESTS_OK",len(docs),"letters; remaining page headers:",headers,
      "ambiguous fragments flagged:",flagged)
