# Jackson Letters Standalone — separate Android installation

This Android app presents Andrew Jackson's surviving historical correspondence in a Gmail-style offline reader. It is **not** an actual Gmail client.

## Included
- 2,116 automatically extracted OCR correspondence candidates from the six public-domain Bassett volumes.
- About 1,902 provisional Gmail-style conversations, grouping only possible historical replies; missing letters are never fabricated.
- 33 condensed and clearly labelled plain-English adaptations. The remaining entries generally contain unverified OCR reading copies.
- Sender/recipient inbox, chronological message view, local search and period/quality filters, reading preferences, device-local notes and stars, contacts, source links, JSON and standalone HTML exports.

## Final fixes
- Corrected switching from SMS-style messages back to a full Gmail-style letter.
- Cached full-text searches; displayed a clear load/failure state while the offline corpus opens.
- Preserved user-imported records and multiple uncertain letters with the same date and correspondent.
- Made stars from earlier starter versions removable after merging with canonical OCR letters.
- Fixed the inbox marking a letter as read automatically before it is opened.
- Fixed the standalone HTML export so it opens completely offline, rather than attempting to fetch bundled files.
- Prevented emoji and other supplementary Unicode characters from being corrupted when Android streams JSON/HTML backups; stream chunks without a duplicate 20-MB archive allocation.
- Made local notes autosave and flush when Android backgrounds the app; fixed clearing a note.
- Improved focus indicators, note labels, navigation controls and mobile tap targets.
- Recovered 43 illegible OCR fragments as explicit uncertainty markers (not guessed words), preserving original OCR for each letter.

## Historical limitations
The records are *OCR candidates*, not 2,116 verified manuscripts. The current audit identifies 286 records needing manual review. Dates, names, page boundaries and original print OCR may still be wrong. Of the 2,116, only 33 have condensed modern-English adaptations. Verify against the linked book scans before citing any original. The app does not invent replies or hide its editorial limits.

## Install
Download **JacksonLetters-Standalone.apk** from the [release page](https://github.com/bryankmann7-a11y/andrew-jackson-gmail/releases/tag/v3.3.0-standalone) on your Android phone and open it.

**This APK installs as a new app, not an update.** The Android package ID is `org.jacksonletters.archive.standalone`; earlier versions use a different ID and remain untouched. Local notes and stars are not automatically shared. If wanted, export a JSON backup from the old installation and import it into this separate installation. There is no need to uninstall either older app.

This is a directly distributed, debug-signed APK, not a Play Store release.

## Verification
GitHub Actions tests the downloaded historical corpus, OCR cleanup and audit, source metadata, archive filters, export, Unicode chunking, startup syntax, threads, stars, navigation, SMS views and Android compilation. A physical-phone UI test has **not** been completed. The hosted emulator did not finish reliably due to Android system-image/ADB startup failure; it did not establish an app crash.
