#!/usr/bin/env python3
"""Build an offline, explicitly UNVERIFIED OCR correspondence index from Bassett volumes I-VI.

This extracts probable letters, not an authoritative scholarly transcription or a complete
catalogue of every surviving Jackson manuscript. Output records always say uncorrected OCR.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.request
import urllib.error

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'app/src/main/assets/archive/corpus.json'
CACHE = BASE / '.bookcache'
IDS = {i: f'correspondenceof000{i}jack' for i in range(1,7)}
YEARS = {1:(1788,1814),2:(1814,1819),3:(1820,1828),4:(1829,1832),5:(1833,1838),6:(1839,1845)}
MONTHS = {k.lower()[:3]:i for i,k in enumerate(
    ['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
MONTHS['agu']=8
MON = r'January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|Jun\.?|Jul\.?|Aug\.?|Sept?\.?|Oct\.?|Nov\.?|Dec\.?'
MON += '|Agust'
DATE = re.compile(r'\b(' + MON + r')\s*([0-3]?\d)(?:st|nd|rd|th|d)?\s*[,.;]?\s*(17[89]\d|18[0-4]\d)\b', re.I)
YEAR = re.compile(r'\b(17[89]\d|18[0-4]\d)\b')
PAGE1 = re.compile(r'^\s*(\d{1,4})\s+Correspondence of Andrew Jackson\s*$', re.I)
PAGE2 = re.compile(r'^\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)[, ]+\s*18\d{2}\s+(\d{1,4})\s*$',re.I)

class OCRHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.inpre = False
        self.fragments = []
    def handle_starttag(self,tag,attrs):
        if tag == 'pre': self.inpre=True; self.depth=1
        elif self.inpre: self.depth+=1
    def handle_endtag(self,tag):
        if self.inpre:
            self.depth-=1
            if self.depth<=0: self.inpre=False
    def handle_data(self,s):
        if self.inpre:self.fragments.append(s)

def unbox(raw):
    s=raw.decode('utf-8','replace').replace('\r\n','\n')
    if '<html' in s[:4000].lower() or '<pre' in s[:4000].lower():
        parser=OCRHTML()
        parser.feed(s)
        if parser.fragments:
            s=html.unescape(''.join(parser.fragments))
    return s.replace('\ufeff','')

def download(vol):
    CACHE.mkdir(parents=True,exist_ok=True)
    dest=CACHE / f'vol{vol}.txt'
    if dest.exists() and dest.stat().st_size>90000:
        return dest.read_text('utf-8','replace')
    ident=IDS[vol]
    urls=[
        f'https://archive.org/stream/{ident}/{ident}_djvu.txt',
        f'https://archive.org/download/{ident}/{ident}_djvu.txt',
        f'https://archive.org/download/{ident}/{ident}_full_text.txt',
        f'https://archive.org/download/{ident}/{ident}_text.pdf.txt',
    ]
    errs=[]
    for url in urls:
        try:
            print('Downloading',vol,url,flush=True)
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (academic correspondence research)','Accept':'text/plain,text/html,*/*'})
            with urllib.request.urlopen(req,timeout=25) as resp:
                if int(resp.status)!=200:raise RuntimeError(f'HTTP {resp.status}')
                raw=resp.read(25_000_001)
            if len(raw)>25_000_000:raise RuntimeError('source larger than OCR limit')
            s=unbox(raw)
            if len(s)<90000 or 'jackson' not in s.lower():raise RuntimeError(f'not full OCR: {len(s)} chars')
            if s.lower().count('correspondence of andrew jackson')<3:
                raise RuntimeError('unexpected source; missing page headers')
            dest.write_text(s,encoding='utf-8')
            print('Volume',vol,'retrieved:',len(s),'characters',flush=True)
            return s
        except Exception as e:
            errs.append(str(e))
            print('Download failed:',type(e).__name__,str(e)[:190],flush=True)
            time.sleep(1)
    raise RuntimeError(f'Volume {vol} not retrieved: '+' | '.join(errs[-4:]))

def clean_name(s):
    s=re.sub(r'[\u00b9\u00b2\u00b3*\'".,;:!\s]+$','',s.strip())
    s=re.sub(r'\s+',' ',s)
    # Historical name spelling retained, with OCR capitalization normalized for display.
    return ' '.join(w.capitalize() if w.isupper() else w for w in s.split())

def heading(line):
    s=line.strip().rstrip('?”’ ')
    if not 7<=len(s)<=115 or any(ch.isdigit() for ch in s):return
    # Most real headings are titlecase or uppercase, and isolated on a line.
    if re.search(r'(\.{3,}|[_]{3,}|[!?;:])',s):return
    s=re.sub(r'[\u00b9\u00b2\u00b3*.\s]+$','',s)
    m=re.fullmatch(r'(?:To|T[o0])\s+(.{3,100})',s,re.I)
    if m:
        name=clean_name(m.group(1))
        if len(name)>90 or len(name.split())>15:return
        if name and name[0].islower() and not re.match(r'(?i)^(the|his|her|our|a|an)\b',name):return
        if re.search(r'(?i)\b(that|which|because|having|was|were|would|should|been|are)\b',name):return
        if re.match(r'(?i)^(be|the attention|the contrary|the reader|this|what|whom)\b',name):return
        if re.search(r'[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}\s+[a-z]{4}',name):return
        return ('Andrew Jackson',name)
    m=re.fullmatch(r'(.{3,95}?)\s+TO\s+(?:GEN(?:ERAL)?[. ]+)?(?:ANDREW\s+)?JACKSON',s,re.I)
    if m:
        name=clean_name(m.group(1))
        if len(name)<3:return
        return (name,'Andrew Jackson')

def find_date(lines,i,vol):
    # Date must be on a distinct dateline immediately following the heading.
    for j in range(i+1,min(i+7,len(lines))):
        line=lines[j].strip()
        if not line:continue
        match=DATE.search(line)
        if not match:continue
        if re.search(r'\.{3,}',line):return
        y=int(match.group(3))
        lo,hi=YEARS[vol]
        if not(lo<=y<=hi):continue
        mon=MONTHS.get(match.group(1).lower()[:3])
        if not mon:continue
        try:date=dt.date(y,mon,int(match.group(2))).isoformat()
        except ValueError:continue
        if len(line)>170:return
        return date,j
    return None

def page_near(lines,i):
    for line in reversed(lines[max(0,i-85):i]):
        m=PAGE1.match(line) or PAGE2.match(line)
        if m:return int(m.group(1))
    return None

def parse(s,vol):
    lines=s.replace('\r\n','\n').splitlines()
    heads=[]
    for i,line in enumerate(lines):
        who=heading(line)
        if not who:continue
        dated=find_date(lines,i,vol)
        if not dated:continue
        date,stop=dated
        heads.append((i,stop,date,who))
    # Dedupe header matches and suppress most table-of-contents artifacts.
    docs=[]
    for n,(at,after,date,(sender,recipient)) in enumerate(heads):
        nextat=heads[n+1][0] if n+1<len(heads) else len(lines)
        if nextat<after+2:continue
        # Stop when a new non-letter document begins, instead of attaching it to a letter.
        nonletter=re.compile(r'^(?:PETITION|DEPOSITION|COMMISSION|COURT\s+RECORD|ORDERS?|PROCLAMATION|MEMORANDUM|CERTIFICATE|RESOLUTION|AFFIDAVIT|ARTICLES|REPORT OF|LIST OF|MINUTES|ACCOUNT OF)\b',re.I)
        for k in range(after+2,nextat):
            title=lines[k].strip()
            if len(title)<95 and nonletter.match(title):
                letters=sum(c.isalpha() for c in title)
                capitals=sum(c.isupper() for c in title)
                if letters>3 and capitals/letters>.30:
                    nextat=k
                    break
        raw='\n'.join(lines[after+1:nextat]).strip()
        if len(raw)<135:continue
        original_len=len(raw)
        if len(raw)>36000:raw=raw[:36000]+'\n\n[OCR extraction truncated after 36,000 characters]'
        if not re.search(r'[A-Za-z]{4}',raw):continue
        # OCR edition includes occasional contents, footnotes, page headers; flag for review.
        page=page_near(lines,at)
        ident=hashlib.sha1((str(vol)+'|'+date+'|'+sender+'|'+recipient+'|'+raw[:120]).encode()).hexdigest()[:15]
        docs.append({
           'id':'basset-'+str(vol)+'-'+ident,'date':date,
           'from':sender,'to':recipient,
           'subject':sender+' to '+recipient+' ('+date+')',
           'original':raw,'modern':'',
           'summary':'Automatically extracted historical text (uncorrected OCR); no modern-English adaptation yet.',
           'replyContext':'A reply relationship has not been independently verified.',
           'context':'This letter was extracted automatically from the published correspondence. OCR may contain transcription errors, editorial notes, and text from nearby documents.',
           'source':f'https://archive.org/details/{IDS[vol]}',
           'sourceCitation':f'Correspondence of Andrew Jackson, ed. John Spencer Bassett, volume {vol}'+(f', printed p. ~{page}' if page else '')+' (OCR; needs review).',
           'volume':vol,'page':page,'status':'ocr','kind':'letter',
           'sourceChecked':False,'extractionWarning':(original_len>36000), 'needsReview':(original_len>17000 or len(recipient)>65 or len(sender)>65),
        })
    print('Volume',vol,'candidate headings:',len(heads),'accepted:',len(docs),flush=True)
    if len(docs)<30:
        raise RuntimeError(f'Volume {vol}: fewer than 30 probable letters; format or source may be wrong')
    return docs

def main():
    all_docs=[]
    counts={}
    for i in range(1,7):
        raw=download(i)
        docs=parse(raw,i)
        all_docs+=docs
        counts[str(i)]=len(docs)
    ids={}; kept=[]
    for d in all_docs:
        if d['id'] not in ids:
            ids[d['id']]=1; kept.append(d)
    if not any(d['date']=='1788-08-12' and d['from']=='Andrew Jackson' for d in kept):
        raise RuntimeError('Earliest known 1788 Jackson-to-Avery letter was not extracted; check OCR headings')
    kept.sort(key=lambda x:(x['date'],x['volume'],x['id']))
    bundle={'edition':'Correspondence of Andrew Jackson, John Spencer Bassett, volumes I-VI',
       'status':'Uncorrected scan-derived OCR. Not all original letters survive, and this is not an exhaustive list.',
       'source':'https://archive.org/details/correspondenceof0001jack',
       'volumeCounts':counts,'letters':kept}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('OFFLINE_ARCHIVE_OK:',len(kept),'letters; per-volume:',counts,'bytes:',OUT.stat().st_size,flush=True)

if __name__=='__main__':
    main()
