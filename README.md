# Jackson Letters — offline Android correspondence reader

An Android app for reading Andrew Jackson's historical correspondence through a familiar Gmail-style inbox and message threads. It is an offline historical reader, **not** an email client.

## Get the Android app

Download the **JacksonLetters-v3.2.0.apk** file from the [GitHub releases page](https://github.com/bryankmann7-a11y/andrew-jackson-gmail/releases). Open the downloaded APK on Android to install it. An Android browser or file manager may ask for permission to install the APK.

**Do not uninstall an existing copy first.** Its notes, read markers, and stars live on your phone. Installing over the current version should preserve them when both APKs share the same signing key. If Android reports a signature conflict, export your JSON backup from the installed app before making any changes.

This is a personal, debug-signed Android APK, not a Google Play release. Android 8.0+ is supported.

## What is in the archive

- **2,116 historical OCR correspondence candidates** extracted automatically from six public-domain Bassett volumes—not 2,116 independently verified manuscript transcriptions.
- **1,902 candidate email-style conversations** grouped cautiously by correspondents, dates and possible reply references.
- **33 labelled plain-English editorial reading aids**. Other entries generally display OCR reading copies, not English translations.
- **286 entries flagged for human OCR review** in the November 2026 audit. The separate original OCR is retained, and uncertain fragments are explicitly labelled.
- Gmail-style threads, SMS-like chronology, offline search and filters, adjustable reading styles, source links, notes, stars, import and export.

Do not quote the OCR as verified historical wording without checking the original scan. No missing replies are invented.

## Development and test status

The repository builds an installable APK with GitHub Actions, runs archival and UI-logic regression tests, and runs an offline Android emulator smoke test as part of its release workflow. A passing emulator launch does not replace checking the final installation on the user's physical phone.

See [release notes](RELEASE_NOTES.md) and [polish and verification checklist](POLISH_CHECKLIST.md) for limits and remaining editorial work.
