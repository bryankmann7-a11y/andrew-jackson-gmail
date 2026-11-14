"""Conservative display-only cleanup of historical scanned-book OCR.

The original text remains unchanged. The cleaned reading copy is not a
verified transcription or modern-English translation. Page furniture is
removed only when it has clear signs of being a running book header.
"""
import re

# The running header often interrupts a word on a printed page break:
#   'opin-\n\n98 Correspondence of Andrew Jackson\n\nion' => 'opinion'
PAGE_TITLE = re.compile(r'(?m)^[^\n]{0,18}Correspondence of Andrew Jackson[^\n]{0,5}$')
SPLIT_WATERMARK = re.compile(
    r'(?m)^[ \t]*Jackson[ \t]*\n[ \t]*Correspondence of Andrew[ \t]*\n[ \t]*Jackson[ \t]*$'
)
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

# Only flag clearly corrupted letter-junk-letter strings.
# Monetary amounts such as $350 and normal historic spellings are untouched.
GARBLED = re.compile(r'(?<!\w)([A-Za-z]{3,})[$#@~^*|+][0-9_.\-\\/]{1,8}([A-Za-z]{3,})(?!\w)')
PAGE_STITCH = re.compile(r'(?<=\w)-[ \t]*(?:\n[ \t]*){1,3}(?=[a-z])')
# All matching examples in the six-volume audit were distorted printings of
# 'William'. Restrict this pattern to the distinctive 1-am ending; do not
# apply a general 1->i substitution to arbitrary historical words.
MISREAD_WILLIAM = re.compile(r'(?i)\bW[ilutxr]{1,8}1a{0,2}m{1,2}\b')



def clean_ocr_text(text):
    """Return a display-only reading copy. Never change or overwrite the source."""
    s = text.replace('\r\n', '\n').replace('\r', '\n')
    s = MONTH_HEADER.sub('', s)
    s = SPLIT_WATERMARK.sub('', s)
    s = SPLIT_PAGE.sub(lambda m: m.group('stem') + m.group('end'), s)
    s = EMBEDDED_PAGE.sub(lambda m: m.group('stem') + m.group('end'), s)
    s = PAGE_TITLE.sub('', s)
    s = MISREAD_WILLIAM.sub('William', s)
    s = re.sub(r'(?i)\bSmi1th\b', 'Smith', s)
    s = re.sub(r'(?i)\bDivis1on\b', 'Division', s)
    s = re.sub(r'(?i)\bthou8ands\b', 'thousands', s)
    s = GARBLED.sub(lambda m: m.group(1) + ' [unclear OCR] ' + m.group(2), s)
    # Collapsing excess blank lines before stitching handles a page break
    # where the printed running header occupied multiple blank lines.
    s = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', s)
    s = PAGE_STITCH.sub('', s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    s = re.sub(r'(?<!\n)\n(?!\n)', ' ', s)
    s = re.sub(r' *\n[ \t]*\n(?:\s*\n)+', '\n\n', s)
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()
