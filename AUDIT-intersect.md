
## Intersect audit (build 2026101205, 12 Oct 2026 MT)
Scope: continuous blended tone, OpenBible cross-references ("Intersect"), four-panel UI, seamless playback. Plain JS/HTML, no AI calls, no new network services.

**1. Tone**
- Theta: four binaural pairs (carriers 150/200/250/300 Hz) with beats spread around the chosen centre and clamped to 4-8 Hz. Three centres: lower, middle (default), upper. The old 10 Hz "alpha" option is gone. The pairs run on real-time oscillators in the tone bed, so they never restart between verses. Saved WAVs still bake theta into the file.
- 777 Hz: soft and steady, with its own on/off switch. Labelled as a symbolic choice, not a researched or biblical frequency.
- Evolving tone: steered word by word by Hebrew gematria (Torah) or Greek isopsephy (NT, Scrivener TR). Where no original text is bundled it uses an English-lexicon fallback. Theme partials (the "solfeggio" numbers) are labelled as 1990s numerology. The 7.83/40 Hz shimmer is labelled "colour only".
- Tuning: A=440 by default. A=432 is an optional checkbox labelled "alternative tuning, preference, thin evidence". It scales every generated tone by 432/440, except 777 Hz, which is a fixed Hz value. There are no preset buttons.
- The honesty notes in Sound › More follow /workspace/research/sound-frequency-research.md: scripture gives no tuning or Hz value; the 120 trumpeters are a head count; the 440 Nazi story is a 1988 myth; solfeggio comes from 1990s numerology; 432 rests on one borderline pilot study. The app makes no healing claims.

**2. Intersect**
- Data: OpenBible.info cross_references.txt (CC-BY), from a.openbible.info/data/cross-references.zip. `tools/build_xref.py` turns it into xref/<Book>.json: up to 5 refs per verse, ranked by votes, votes > 0, ranges reduced to their first verse. Each row is [book, chapter, verse, votes, motif digits, theme mask]. Total size is 3.1 MB across 66 lazily loaded files (Cache API `lt-xref-v2`).
- Only real cross references are used. There is no keyword matching.
- Playback: each ref plays as a soft motif on the bed, panned left if the ref comes earlier in the Bible and right if later. Its tab lights up as it plays.
- Tabs: tappable cross-reference tabs appear under the current verse, with the visible credit "Cross references: OpenBible.info, CC-BY" (linked).
- Follow the thread: Reading panel. It hops to the strongest cross-reference not yet visited, and the hop is prefetched like any other next verse.

**3. UI**
- Four bottom-sheet panels (Sound, Reading, Sleep & Pray, Tools). Each has a "More" expander.
- Pray mode, Flash (RSVP), Night mode, wake locks and the phone fixes are kept as they were. Their controls were moved into the panels.
- Buttons use `touch-action:manipulation`, which stops double-tap zoom from eating taps.

**4. Playback**
- Every live source runs through its own gain stage. Start, stop and swap use ramps, never hard cuts, and each verse buffer has 0.6 s edge fades.
- After a verse starts, the next verse is predicted (range, follow the thread, night loop, auto). Its text is fetched and its buffer pre-rendered. It is then scheduled to start 0.8 s before the current one ends, with a linear crossfade.
- The tone bed (theta, 777 Hz, evolving tone) is never restarted. It stays live for 2.5 s across any gap.
- Narration mode pre-builds the next segment.
- "Play per press" options: verse, 3 verses, paragraph, chapter (default), custom N, continuous (to Rev 22:21). Paragraph is approximate because the KJV files have no paragraph marks: a paragraph ends at a sentence end where the next verse does not open with a conjunction, with a maximum of 8 verses.
- Whole-Bible KJV search: button or Enter, first 200 hits.
- Speed goes up to 3x. Narration rate is capped at 3, but many speech engines cap lower.
- Chapter-back fix: a tap while the previous jump was still loading used the old position, so two taps only moved one chapter. Chapter and verse stepping now use the pending position.

**Verified (headless Chrome 'new', local server)**
- `node --check` passes on the inline script, and `py_compile` passes on the tool. The page loads with 0 page or console errors.
- With chunk set to 3 verses, playback ran Gen 1:1 → 1:2 → 1:3 through two prefetched crossfade swaps, then stopped at the end of the chunk. With Auto on, swaps continued 1:1 → 1:4.
- Bed theta gain was live at 0.05.
- John 3:16 tabs showed Romans 5:8, 1 John 4:9, Romans 8:32, John 3:15 and John 11:25, with the credit shown. Tapping a tab played Romans 5:8. Follow the thread picked 1 John 4:9.
- Searching "living water" returned 7 matches.
- Two quick chapter-backs from Exodus 3 landed on Exodus 1. Chapter-back at Genesis 1 stayed put.
- All four panels rendered. The 432 toggle set A=432.

**Not verified**
- Real-device audio quality: whether a crossfade is audible, how binaural beats sound on headphones, and iOS/Android background or lock-screen behaviour.
- The speechSynthesis gap between narrated verses. This is inherent to the browser and was not tested with a real voice.
- The thermal and CPU cost of 13 always-on oscillators on low-end phones.
