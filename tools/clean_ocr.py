"""Conservative DISPLAY-ONLY cleanup of historical scan OCR.

Never replace the raw source text. A readable copy is neither a verified
transcription nor a plain-English translation. Rejoin obvious word breaks
through running headers, remove scan page furniture, and flag ambiguous junk.
"""
import re

# A page number and book title can interrupt the actual text mid-word:
#   'his opin-\n\n98 Correspondence of Andrew Jackson\n\nion' => 'his opinion'.
PAGE_TITLE = re.compile(r'(?m)^[ \t]*(?:[0-9]{1,4}[.,]?|[“”\"‘])?[ \t]*Correspondence of Andrew Jackson[ \t]*$')
SPLIT_PAGE = re.compile(
    r'(?i)(?P<stem>[a-z]{2,})-[ \t]*(?:\n[ \t]*){1,3}'
    r'\d{1,4}[,.]?[ \t]+Correspondence of Andrew Jackson'
    r'[ \t]*(?:\n[ \t]*){1,3}(?P<end>[a-z]{2,})'
)
EMBEDDED_PAGE = re.compile(
    r'(?i)(?P<stem>[a-z]{2,})\d{1,4}[,.]?[ \t]+'
    r'Correspondence of Andrew Jackson[ \t]*(?:\n[ \t]*){1,3}'
    r'(?P<end>[a-z]{2,})'
)
MONTH_HEADER = re.compile(
    r'(?m)^[ \t]*(?:January|February|March|April|May|June|July|August|September|October|November|December),?'
    r'[ \t]+(?:17\d{2}|18\d{2})[ \t]+\d{1,4}[ \t]*$'
)
# Only intervene if junk has both a distinctive scan-symbol and digits/
# punctuation INSIDE an otherwise alphabetic token. Do not touch ordinary
# currency ($350), hyphenated names, footnote markers or historical spellings.
GARBLED = re.compile(r'(?<!\w)([A-Za-z]{3,})[$#@~^*|+][0-9_.\-\\/]{1,8}([A-Za-z]{3,})(?!\w)')
PAGE_STITCH = re.compile(r'(?<=\w)-[ \t]*\n[ \t]*(?=[a-z])')


def clean_ocr_text(text):
    """Produce a display-friendly copy; leave text argument and original intact."""
    s = text.replace('\r\n', '\n').replace('\r', '\n')
    s = MONTH_HEADER.sub('', s)
    s = SPLIT_PAGE.sub(lambda m: m.group('stem') + m.group('end'), s)
    s = EMBEDDED_PAGE.sub(lambda m: m.group('stem') + m.group('end'), s)
    s = PAGE_TITLE.sub('', s)
    # Preserve readable fragments, explicitly label the unreadable span.
    s = GARBLED.sub(lambda m: m.group(1) + ' [unclear OCR] ' + m.group(2), s)
    s = PAGE_STITCH.sub('', s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    s = re.sub(r'(?<!\n)\n(?!\n)', ' ', s)
    s = re.sub(r' *\n[ \t]*\n(?:\s*\n)+', '\n\n', s)
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()
