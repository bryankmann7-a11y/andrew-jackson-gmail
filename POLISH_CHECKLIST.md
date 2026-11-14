# Jackson Letters — Polish checklist

Current baseline: Android WebView APK with the six Bassett OCR volumes; 2,116 automatically extracted correspondence candidates (not 2,116 verified historical letter transcripts), 33 labelled plain-English renderings, and a Gmail / SMS-style UI. Work must preserve raw source text and identify conjecture rather than fabricating letters.

## P0 — Fix what blocks normal use

- [x] **P0-01 Installation.** Current APK installs successfully on the user's phone. No upgrade or ongoing update system is needed; deliver one final APK when the app is finished.
- [ ] **P0-02 Actual Android smoke test.** Installation is confirmed by the user; still test first launch, offline launch, inbox, message view, search, star, notes, export/import, device Back, rotation, screen size, and return from background. Confirm no blank screen, WebView exceptions, or freezes.
- [ ] **P0-03 Start-up and large corpus performance.** Show a real loading state; avoid making one giant synchronous 20-MB+ JSON parse and full-body scan on each keystroke. Measure start-up time, memory, scrolling, and low-end-device behavior.
- [x] **P0-04 Avoid duplicated starter correspondence.** Match starter adaptations to source OCR only when the date, sender, recipient and a unique original agree; preserve original OCR, legacy notes/stars and uncertain same-day alternatives. Automated regression passes.
- [ ] **P0-05 Archive verification pipeline.** Detect suspicious dates, implausible names, merges/splits between documents, footnotes, pages and other editorial artifacts. Maintain an audit trail and a 'needs checking' status. Never label OCR automatically 'source-verified.'
- [x] **P0-06 Accurate offline messaging.** Removed the misleading load-six-books prompts, corrected archive counts and clearly separated OCR from modern-English adaptations. Offline bundle verified in Android build.

## P1 — Make it pleasant to read

- [x] **P1-00 Gmail email threading.** Mail inbox now groups possible replies into one conversation; messages expand/collapse and show source/OCR/reading tabs; May 1797 Jackson–Sevier exchange regression-tested. Individual links remain clearly marked as unverified unless stronger evidence exists.

- [x] **P1-01 Mobile navigation.** Android Back button/gesture now closes dialogs and drawers first, dismisses the keyboard when editing, restores reader/inbox/profile navigation state, preserves search/filter and scroll position, supports SMS → full email → SMS, and survives rotation. Automated regression and APK compile tests pass; physical-phone smoke testing remains open under P0-02.
- [ ] **P1-02 Better inbox.** Clear correspondence direction, sender, recipient, historical date, excerpt and source-quality badge, compact mobile rows, optional unread/star markers, and grouping by decade/year.
- [ ] **P1-03 Search, sort and filters (partially complete).** Search by names, dates, body and subject; chronological sort, folder filters, plus period, plain-English, OCR-only and needs-review filters now work with Gmail threads. Debounce reduces repeated searches; indexed search, explicit correspondent filters and result highlighting remain open.
- [x] **P1-04 Chat view usability.** The SMS view now uses bounded chronological history (48 letters per window), date separators, sent/received bubbles, collapsible previews for long letters, scroll-to-selected and direct original/source links. It does not fabricate missing replies. Gmail Mail view keeps its independently labeled candidate reply threads.
- [x] **P1-05 Reading controls.** Adjustable font size, line spacing, paper/sepia/night reading colors, persisted preferences, and returning to the reader's former position via app navigation. Automated checks pass; Android handset visual QA remains open.
- [ ] **P1-06 Sources beside every letter.** Show a readable volume, approximate page (when known), stable source URL, OCR quality, and direct access to scanned pages where a verified page locator exists; avoid false precision.
- [ ] **P1-07 Contacts and conversations.** Normalize only confident name variants, retain original OCR headings, handle similarly named individuals without merging them, and give each correspondent a chronological sent/received timeline.
- [ ] **P1-08 Notes and local data (partially complete).** Autosave notes and export/import personal state; standalone HTML export now includes all four offline reader scripts and data, with regression tests for saved notes. Full Android backup/restore and migration smoke test remains open.
- [ ] **P1-09 Accessibility.** Large tap targets, labels and semantic controls, TalkBack reading order, contrast, Dynamic Type/font scaling, and keyboard focus.

## P2 — Content and product quality

- [x] **P2-00b Targeted OCR editorial batch (November 2026).** Audited all six volumes; 253 of 2,116 candidate entries are flagged for manual source review under the expanded checks. Saved a generated CSV review queue in GitHub Actions. Corrected common digit-corrupted words and clear name variants (including William B. Lewis), added document-level OCR warnings in Gmail/SMS views, and added eleven hand-edited modern-English reading aids to the existing thirteen (24 total). The archive remains unverified overall; do not mistake these mechanical or editorial improvements for scan checking.


- [x] **P2-00 Automated OCR display cleanup.** Remove printed page headers/page numbers from readable copies; rejoin words split across pages; explicitly flag embedded unreadable symbols, e.g. `John$-11called` → `John [unclear OCR] called`; preserve verbatim `original` field. Filter a known misclassified table-of-contents item and test fixes against all six volumes. Further source-by-source corrections remain open.


- [x] **P2-00c Additional illegible OCR markers (November 14, 2026).** Clearly fused words containing digits or symbols now show `[unclear OCR]` in display-only reading copies instead of unreadable junk; legitimate amounts and years are preserved. The OCR audit checks the original text too, retaining the exact reason each passage was flagged. All original OCR remains untouched. The full six-volume CI audit currently flags 286 entries for review; 43 fragment markers are displayed. Regression and APK compilation tests pass.

- [ ] **P2-01 Historical editorial pass.** Check documents against actual volume pages; fix dates/people/page references; flag missing, truncated, and combined entries; review at least a sample from each decade before trusting bulk extraction.
- [ ] **P2-02 Plain-English editions (ongoing editorial work).** Added nine further short OCR-grounded adaptations (1806–1813), bringing the total to 33. Historical source OCR is preserved and none is presented as scan-verified. The majority of correspondence still needs human editorial work; missing replies must not be invented.
- [ ] **P2-03 Real profiles, careful portraits.** Separate verified biography from speculative illustration; don't label generated pictures as authentic portraits. Add sourced descriptions and relationship context.
- [ ] **P2-04 Timeline and orientation.** Decade navigation, year/date jump, dated events only with supporting sources, and a clear indication when a date is approximate.
- [ ] **P2-05 Final visual pass.** Consistent iconography, spacing, color/theme, typography, transitions and empty/error/loading states. Keep familiar Gmail-inspired structure without implying these were electronic messages.
- [ ] **P2-06 Regression checks.** Automated corpus tests plus repeatable phone-sized UI tests: first letter, oldest/newest, bulk search, large conversation, back navigation, export/import, offline mode and update APK.

## Latest verified build

- GitHub Actions [run 43626779073](https://github.com/bryankmann7-a11y/andrew-jackson-gmail/actions/runs/43626779073) (commit `47b00aa21c9f6e9405c5955e6fc5d6be8fba80f4`): Python and JavaScript preflight, six-volume download, OCR cleaning, review audit, archive integrity, reader/filter, standalone export, Gmail threading, SMS, navigation and APK build all passed.
- 2,116 OCR candidates in 1,902 provisional Gmail-style conversations, 33 modern-English reading aids, 286 OCR review candidates, and 43 explicitly marked unreadable fragments. This is a code-and-CI pass, not a manual verification of scans or physical Android smoke test.

## Working order

1. Fix Android navigation and verify phone behavior (P0-02, P1-01). Installation already works.
2. Fix loading/search responsiveness and duplicates (P0-03, P0-04, P1-03).
3. Clean the inbox, chat, and reader (P1-02, P1-04, P1-05).
4. Improve document verification, sources, and editorial statuses (P0-05, P1-06, P2-01).
5. Expand human-checked modern-English editions progressively (P2-02).
6. Finish profiles, styling and regression testing.

Definition of done: one final APK the user can install, which works offline, renders and searches the corpus smoothly on Android, doesn't lose local data unexpectedly, and unambiguously distinguishes original OCR, editorial summaries, and historically verified content. The user does not require post-release app updates.
