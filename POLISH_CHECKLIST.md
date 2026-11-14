# Jackson Letters — Polish checklist

Current baseline: Android WebView APK with the six Bassett OCR volumes; about 2,117 automatically extracted correspondence candidates (not 2,117 verified historical letter transcripts), 13 labelled plain-English renderings, and a Gmail / SMS-style UI. Work must preserve raw source text and identify conjecture rather than fabricating letters.

## P0 — Fix what blocks normal use

- [x] **P0-01 Installation.** Current APK installs successfully on the user's phone. No upgrade or ongoing update system is needed; deliver one final APK when the app is finished.
- [ ] **P0-02 Actual Android smoke test.** Installation is confirmed by the user; still test first launch, offline launch, inbox, message view, search, star, notes, export/import, device Back, rotation, screen size, and return from background. Confirm no blank screen, WebView exceptions, or freezes.
- [ ] **P0-03 Start-up and large corpus performance.** Show a real loading state; avoid making one giant synchronous 20-MB+ JSON parse and full-body scan on each keystroke. Measure start-up time, memory, scrolling, and low-end-device behavior.
- [ ] **P0-04 Distinguish documents that have multiple representations.** Merge the 14 demo/adapted entries with matching real OCR document IDs instead of showing an apparent duplicate; never quietly overwrite the source; retain legacy notes/star links.
- [ ] **P0-05 Archive verification pipeline.** Detect suspicious dates, implausible names, merges/splits between documents, footnotes, pages and other editorial artifacts. Maintain an audit trail and a 'needs checking' status. Never label OCR automatically 'source-verified.'
- [ ] **P0-06 Correctly describe content and offline state.** Remove misleading 'Load six books' prompts after offline archive is bundled, and make the archive help text, status counts, first-run instructions and download messages reflect the installed version.

## P1 — Make it pleasant to read

- [x] **P1-00 Gmail email threading.** Mail inbox now groups possible replies into one conversation; messages expand/collapse and show source/OCR/reading tabs; May 1797 Jackson–Sevier exchange regression-tested. Individual links remain clearly marked as unverified unless stronger evidence exists.

- [ ] **P1-01 Mobile navigation.** Make inbox → letter → back predictable with Android system Back button/gesture, preserving search/filter and scroll position.
- [ ] **P1-02 Better inbox.** Clear correspondence direction, sender, recipient, historical date, excerpt and source-quality badge, compact mobile rows, optional unread/star markers, and grouping by decade/year.
- [ ] **P1-03 Search, sort and filters.** Fast, indexed search over names/dates/body/subject; filters for sender, recipient, period, modern-English available, OCR-only, verified, starred; show result totals and highlights.
- [x] **P1-04 Chat view usability.** The SMS view now uses bounded chronological history (48 letters per window), date separators, sent/received bubbles, collapsible previews for long letters, scroll-to-selected and direct original/source links. It does not fabricate missing replies. Gmail Mail view keeps its independently labeled candidate reply threads.
- [ ] **P1-05 Reading controls.** Adjustable text size, line spacing, sepia/dark theme, readable headers and link styling, position memory and a clean distraction-free letter view.
- [ ] **P1-06 Sources beside every letter.** Show a readable volume, approximate page (when known), stable source URL, OCR quality, and direct access to scanned pages where a verified page locator exists; avoid false precision.
- [ ] **P1-07 Contacts and conversations.** Normalize only confident name variants, retain original OCR headings, handle similarly named individuals without merging them, and give each correspondent a chronological sent/received timeline.
- [ ] **P1-08 Notes and local data.** Autosave notes reliably; export/import notes, bookmarks, reading state and user-corrected names; backup/export test. Avoid silent loss during normal use.
- [ ] **P1-09 Accessibility.** Large tap targets, labels and semantic controls, TalkBack reading order, contrast, Dynamic Type/font scaling, and keyboard focus.

## P2 — Content and product quality

- [ ] **P2-01 Historical editorial pass.** Check documents against actual volume pages; fix dates/people/page references; flag missing, truncated, and combined entries; review at least a sample from each decade before trusting bulk extraction.
- [ ] **P2-02 Plain-English editions.** For each corrected letter, create a faithful modern-English version in deliberate batches, preserve the original and source citation, and mark omissions and interpretive choices. Do not generate 'replies' that don't survive.
- [ ] **P2-03 Real profiles, careful portraits.** Separate verified biography from speculative illustration; don't label generated pictures as authentic portraits. Add sourced descriptions and relationship context.
- [ ] **P2-04 Timeline and orientation.** Decade navigation, year/date jump, dated events only with supporting sources, and a clear indication when a date is approximate.
- [ ] **P2-05 Final visual pass.** Consistent iconography, spacing, color/theme, typography, transitions and empty/error/loading states. Keep familiar Gmail-inspired structure without implying these were electronic messages.
- [ ] **P2-06 Regression checks.** Automated corpus tests plus repeatable phone-sized UI tests: first letter, oldest/newest, bulk search, large conversation, back navigation, export/import, offline mode and update APK.

## Working order

1. Fix Android navigation and verify phone behavior (P0-02, P1-01). Installation already works.
2. Fix loading/search responsiveness and duplicates (P0-03, P0-04, P1-03).
3. Clean the inbox, chat, and reader (P1-02, P1-04, P1-05).
4. Improve document verification, sources, and editorial statuses (P0-05, P1-06, P2-01).
5. Expand human-checked modern-English editions progressively (P2-02).
6. Finish profiles, styling and regression testing.

Definition of done: one final APK the user can install, which works offline, renders and searches the corpus smoothly on Android, doesn't lose local data unexpectedly, and unambiguously distinguishes original OCR, editorial summaries, and historically verified content. The user does not require post-release app updates.
