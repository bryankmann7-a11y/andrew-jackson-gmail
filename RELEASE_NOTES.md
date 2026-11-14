# Jackson Letters v3.2.0

Offline Android correspondence reader, built to look and navigate like familiar Gmail conversations.

## Included
- 2,116 OCR-extracted historical correspondence **candidates** from the six public-domain Bassett volumes.
- About 1,902 *provisional* Gmail-style conversations. These group possible replies from surviving documents; they are not verified email threads.
- 33 clearly labeled condensed plain-English readings. Most other records are **OCR reading copies**, not translations.
- Historical incoming/outgoing letters, chronological message view, search, year and OCR-quality filters, adjustable reading appearance, stars, device-local notes, and exports.

## Release fixes
- Fixed switching from the message-style reader into a full email.
- Cached full-text OCR search so repeated searches do not reconstruct every letter's searchable text.
- Clear loading status for the bundled offline archive and accurate labels on OCR-only reading tabs.
- Autosave notes from the letter reader and preserve OCR provenance when importing backups.
- Display-only masking of additional badly garbled OCR fragments while preserving original extracted text separately.
- Tests verify threading, OCR handling, import/export metadata, navigation, archive integrity and APK compilation.

## Important archival limits
These are not verified original manuscripts or a complete catalog of every surviving Jackson letter. OCR may contain wrong names, dates, page breaks or mixed documents. The current audit flags 286 records for manual review; verify against linked source scans before quoting. No missing replies were written or invented.

## Install
Download **JacksonLetters-v3.2.0.apk** from this release on your Android phone and open it. Android may ask you to approve installing apps from your browser or Files app.

**Keep your existing Jackson Letters app installed** and install this over it. It uses the same application identifier and an incremented version code. Do not uninstall the old app first: its private notes and starred items are saved locally. If Android reports a signing mismatch, stop and export your existing data before attempting any uninstall.

This is a personal-use debug-signed APK provided directly through GitHub, not a Google Play Store package. The six-volume historical archive works offline once installed.

## Checks
The CI workflow verifies the archive and builds the Android APK. Automated checks and any emulator smoke test do not guarantee behavior on every physical Android handset.
