# Jackson Letters Android

An offline, Gmail-style Android reader for the historical correspondence of Andrew Jackson.

The APK bundles OCR-based correspondence candidates extracted from all six public-domain Bassett volumes, with a Gmail-style inbox and possible reply threads, an optional SMS-style chronological view, search, notes, stars, contacts, source links, and offline data export. The historical letters were never emails; the Gmail appearance is a reading interface only.

## Archive contents and limitations

- **2,116 automatically extracted correspondence candidates** (not verified transcripts of 2,116 original letters).
- **1,902 provisional email-style conversations** from matching names, dates and textual references. Thread links may be uncertain; no missing replies are invented.
- **33 editorially labelled plain-English reading aids**; the remaining entries generally show OCR reading copies.
- **286 entries flagged for OCR review** in the November 14, 2026 build, including **43 explicitly marked unreadable fragments**. An `[unclear OCR]` marker means the text could not be safely reconstructed from OCR alone.
- Each letter retains its original uncorrected OCR text alongside its display-only cleaned reading copy. Human verification against page images is still required before quoting or treating a document as definitive.

## Android build

The project is built using the GitHub Actions workflow **Build Jackson Letters APK**. After a successful run, download the **JacksonLetters-debug-APK** artifact from the workflow's Artifacts section. The current APK is a debug build, not a Google Play release. Installation has been confirmed on the user's Android phone, but full handset regression testing remains outstanding.

**Project checklist:** [POLISH_CHECKLIST.md](POLISH_CHECKLIST.md). The user wants one final APK after remaining polish, not an installation after every development build.
