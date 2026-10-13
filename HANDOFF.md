# HANDOFF — START HERE (Sonolumina)
Compiled by Super Grok for Seabass Krahn. Paste or hand this to any AI that's taking over.

## 1. Handoff brief (verbatim)
SONOLUMINA HANDOFF (from Seabass Krahn, Oct 12 2026)
VISION: Sonolumina (formerly Logos Theta) is a Bible audio+visual web app. Live: https://seabasskrahn.github.io/logos-theta/ (repo seabasskrahn/logos-theta, build 2026101223). Scripture takes form in sound and light, with gratitude as the core, heard as musical resolution. Each word gets a tone from how it's used across the Bible around a 110 Hz home note, shaped by verse emotion (valence sets the mode, arousal the tempo). Visuals include "Eye waves" (Matthew 6:22): two cross-reference waves are the eyelids and the word tones form the iris. There's also a MilkDrop-style visualizer driven by the words and their emotion.
STACK: Hosted on GitHub Pages; deploy = push to main, and version.json holds the build number. Visualizer is Butterchurn core only (vendor/butterchurn-2.6.7.min.js, MIT, lazy-loaded), with no community preset packs. Sonolumina has its own 4 presets (sorrow, longing, peace, joy) driven by valence, arousal and word onsets. Butterchurn is scaffolding only; a custom engine from scratch is planned later.
REQUEST: Add a separate Chat tab on the site where I chat with a live AI that responds in real time (streaming if possible). Keep it minimal: one tab, a chat UI, a live API call.
CONSTRAINTS: No new paid APIs. I subscribe to Grok and possibly Manus. GitHub Pages has no backend or secret storage, so I paste my own free Gemini API key into the tab on my phone; store it only in the browser's localStorage, never in site code, the repo, or chat. Don't delete anything without my OK. Quick smoke tests only; I do the deep testing.
ENVIRONMENT: No desktop work. The Linux box was reset and only Cloud Code is installed. My phone is my only interface, so give me steps I can do from it.
ASK: Take over this build. Add the Chat tab using what I already have, push it live, then report what you did, what's left, and any decision you need from me as a short question.

## 2. Principles
- Scripture is not replaced by frequencies; Scripture takes form.
- Gratitude is the core and the spirit, expressed as musical resolution ("it is good"). It is not a feature to bolt on.
- Never invent facts. Label where every frequency idea comes from.
- Show a concept (a storyboard or a still) before building it in code.
- Builds are fast, with quick smoke checks only.

## 3. Unified equation
Sound(w,t) = F0 · R(w) · K(E(v,t)) · [Σ α_u Sound(u,t)] → Res
- **F0:** 110 Hz home note (432 option; in Live mode, the listener's baseline).
- **R(w):** Eye codebook. The step is floor(12·frac(rank·φ)) on just-intonation ratios, the octave comes from occurrence count, and companion words snap to consonant intervals. The English codebook has 14,973 entries.
- **E:** NRC VAD emotion, blended BSB 0.35 / WEB 0.25 / Strong's glosses 0.30 / KJV 0.10, with negation handling and chapter smoothing.
- **K:** valence sets the mode (Lydian/Ionian, Mixolydian, Dorian, Aeolian), arousal sets the tempo (54–84 BPM), and dominance sets register and brightness.
- **Neighbours:** companion words plus OpenBible cross-references weighted by votes (one link deep).
- **Res:** a V–I cadence per verse, an IV–I "Amen" at chapter end, and the tonic at the close.
- **Time:** works at three scales: verse rhythm, the arc of the chapter, and the whole story.
- **Book families** each get their own instrument: Law, History, Poetry/Wisdom, Prophets, Gospels, Letters, Revelation.

## 4. Build history
- **2026101218:** softer sound (white noise replaced by a pad and soft bells), plus the optional Solfeggio layer in Live mode with a strength slider.
- **Loudness fix:** the carrier pad was 14 dB too hot. It was rebalanced so every frequency layer sits within about 2 dB, like instruments in a mix.
- **2026101220–21:** the score (synthesized cello, strings, electric piano, celesta), diatonic snapping, about 8 dB of ducking under the voice, Mixer sliders, and the Music style setting (Score, Ambient, Pure tones).
- **2026101222:** BSB default with a KJV toggle.
- **2026101223:** MilkDrop style (Butterchurn core, 4 own presets). Its feedback/trail loop (decay + warp) gives the flowing trails. Credits go to Butterchurn (Jordan Berg, MIT) and MilkDrop (Ryan Geiss, BSD).
- **Other features:**
  - Modes: Word mode (pure codebook) versus Live mode (room mic, hummed baseline, glide).
  - Speed reading: RSVP in 1–5 word chunks, and the Visual tab up to about 968 WPM.
  - Visual styles: Cymatics (Chladni, Bessel, Rubens) plus Eye waves, Spectrum, Starfield.

## 5. Known gaps
- **Emotion misreads:** Psalm 22:1 reads as peace, and Psalm 23:1 and Revelation 21:4 read as longing.
- **Narration:** the phone's speech voice isn't in the audio mix, so the visuals don't react to it.
- **MilkDrop testing:** it hasn't been tested on real phones and hasn't been checked for flashing.
- **"Now decoding" line:** it was once blank for about the first 8 s.
- **Licence:** NRC VAD is non-commercial only.

## 6. Research and next ideas
- **Free model pre-scoring:** have a free model score each chapter's emotion, timing and cadence ahead of time and store the results as data files, so playback still makes no AI calls. Free local option: Qwen through Ollama; needs his GPU specs.
- **Paid orchestrator option:** Gemini 3.8 Flash, run ahead of playback. Not chosen because of the no-paid-APIs rule.
- **Visualizer references:** Windows Media Player (XP/Vista) visualizations. Microsoft never released their source, and leaked code is off-limits; adapt the look, not the code. MilkDrop was open-sourced (BSD, 2013), and Butterchurn is its MIT WebGL port. That's the legal path.
- **Later:**
  - A custom visual engine made only for the Eye waves and emotion data.
  - An Android APK under the Sonolumina name.

## 7. Full algorithm spec
# Sonolumina: final sound specification (web build 2026101222)

> "The light of the body is the eye: if therefore thine eye be single, thy whole body shall be full of light." (Matthew 6:22, KJV)

All synthesis is plain, deterministic Web Audio code in `index.html`. There are no AI calls and no audio samples. The data is built offline by `tools/build_codebook.py`, `tools/build_xref.py` and `tools/build_vad.py`.

## 1. The equation

$$
\mathrm{Sound}(w,t)\;=\;\mathrm{Res}\!\left[\,F_0\cdot R(w)\cdot K\big(E(v,t)\big)\cdot\Big(\sum_{u\in N(w)}\alpha_u\,\mathrm{Sound}(u,t)\Big)\right]
$$

Read it as: the word $w$ sounds at the home note, times its codebook ratio, placed by the emotion-chosen mode and register, coloured by its network neighbours weighted by $\alpha_u$, and always resolved home. The recursion is cut after one level (the neighbours' own partials are not expanded further). In code, `Sound(x,E)` returns the word's frequency plus its weighted partials, and `scoreVerse` places every voice through it.

| Term | Meaning | Implementation |
|---|---|---|
| $w$ | a whole word (Hebrew/Greek lemma via OSHB/MorphGNT, or English stem: KJV entries, plus BSB-only stems ranked after the KJV) | `cbLook` |
| $v$ | the verse containing $w$ | `S.pos` |
| $t$ | time: (a) word position in the verse, (b) chapter arc, (c) canonical position | see §4 |
| $F_0$ | home note (pupil): 110 Hz; ×432/440 with the 432 option; the listener's baseline in Live mode. Live modifiers: Room listening (±50 cents toward a consonance with the room's peak), Solfeggio pull (strength 0–1) | `BASEF()`, `TUNE()`, `ROOM`, `solfF` |
| $R(w)$ | Eye codebook ratio: $\mathrm{JUST}[\lfloor 12\{\mathrm{rank}\cdot\varphi\}\rfloor]\cdot 2^{\mathrm{oct}}$, where rank is the order of first appearance, $\varphi$ is the golden ratio, oct = 0/1/2 for ≥200 / 20–199 / <20 occurrences, and JUST = {1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8} | `codebook/*.json` |
| $E(v,t)$ | emotion $(V,A,D)\in[0,1]^3$ | `vad/*.json`, `verseE` |
| $K(E)$ | maps emotion to music: mode, tempo, density, loudness, register, brightness | `Kmap` |
| $N(w)$ | network: (i) the 2 most frequent verse companions (codebook partials), $\alpha=2/3,1/3$; (ii) OpenBible cross-references (top 3 per verse), $\alpha=\text{votes}/\max(\text{votes})$ | `Sound().parts`, `meet(..., alpha)` |
| Res | the Resolution rule (§6) | `scoreVerse` |

## 2. $K(E)$: emotion to music

| Emotion | Musical effect |
|---|---|
| Valence $V$: mode (all modes on the same tonic $F_0$, just intonation) | $V>0.70$: Lydian if $D>0.6$, else Ionian (joy). $0.50<V\le0.70$: Mixolydian (peace). $0.32<V\le0.50$: Dorian (longing). $V\le0.32$: Aeolian (sorrow). |
| Arousal $A$: tempo, density, loudness | Tempo = $54+30A$ BPM (× speed, clamped 0.75–2). Arpeggio subdivisions per bar: 4 / 6 / 8 at $A\le0.3$ / $\le0.55$ / above. Melody at most one note per 2 / 1.5 / 1 beats. Music level ×$(0.75+0.5A)$. |
| Dominance $D$: register and brightness | Melody register ×$2^{0.6(D-0.5)}$ (523–1568 Hz at $D=0.5$). Master low-pass $1100+0.6(700+900D)$ Hz. Celesta weight $0.12+0.08D$. Strings $0.04+0.03(1-A)+0.02D$. |

Modes as just ratios:
- Lydian: 1, 9/8, 5/4, 45/32, 3/2, 5/3, 15/8
- Ionian: 1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8
- Mixolydian: 1, 9/8, 5/4, 4/3, 3/2, 5/3, 16/9
- Dorian: 1, 9/8, 6/5, 4/3, 3/2, 5/3, 16/9
- Aeolian: 1, 9/8, 6/5, 4/3, 3/2, 8/5, 9/5

**Smooth transitions.** A mode only changes at a verse boundary. When it changes, the first bar of the new verse plays a pivot chord whose tones are identical in both modes (tried in the order IV, V, vi, I). Loudness and brightness glide with time constants of 1.2–1.5 s.

## 3. Voices (Score style)
- **Bass:** cello, a filtered saw on the chord root (65–130 Hz).
- **Pad:** strings, 2 detuned saws per chord tone through a 1.1 kHz low-pass, with slow attack and delayed vibrato.
- **Counter-melody:** FM electric piano playing broken arpeggios.
- **Melody:** celesta on key words (lemmas with fewer than 200 occurrences), quantized to eighths, with rests after punctuation. Companion partials sound softly at $0.35\alpha$, snapped to chord tones.
- **Cross-refs:** low-passed string swells from the side of the referenced verse (left = earlier in the Bible, right = later), at gain ×$(0.4+0.6\alpha)$, with mirrored envelopes meeting at the centre.

Each section has its own bus with EQ carve-out, a pan position and a Mixer slider, and the section gains were calibrated offline to about −37 to −38 dBFS RMS each. A master compressor and limiter follow.

The music ducks −8 dB while the narrator speaks (utterance start/end events, else an estimate) and swells in the gaps. Styles: Score (default), Ambient, Pure tones (the 2026101219 sine ensemble).

## 4. $E(v,t)$: emotion over time
- **Lexicon:** NRC Valence, Arousal, and Dominance Lexicon (Saif M. Mohammad, National Research Council Canada, 2018; about 20k English words, scored 0–1).
- **Four sources per verse (build 2026101222).** Each is scored on its own, turned into a percentile across all 31,102 verses, then blended:
  - BSB (Berean Standard Bible) 0.35
  - WEB (World English Bible) 0.25
  - original-language glosses 0.30
  - KJV 0.10

  The weights renormalise when a source has no scoreable words for a verse.
- **Raw score per English text:** the salience-weighted mean over the words found in the lexicon. The weight is $w=0.25+|V-0.5|+|A-0.5|$. Matching tries the exact form, then a small archaic map (saith → say, …), then suffix stripping. Divine names (God, LORD, Jesus, Christ, Yahweh) are excluded, so their constant high valence doesn't mask the verse.
- **Original-language glosses (approximate):** each OSHB Strong's number and each MorphGNT lemma (matched to the Strong's Greek lemma with accents stripped) is mapped to the first clause of its `strongs_def` in the public-domain Strong's dictionaries (Open Scriptures JSON), and that gloss is scored like English. Proper names and divine-name entries (H430, H410, H433, H3068, H3069, H136, H3050, G2316, G2962, G2424, G5547) are skipped. A dictionary gloss is not the word's sense in that verse, so treat this as a rough signal.
- **Negation:** a word with not, no, never, nor, neither, none, without, cannot or nothing among the 3 words before it has its valence flipped and halved around neutral, $v\to0.5-(v-0.5)/2$, and its arousal pulled halfway to neutral. So "no more death" reads as mild relief rather than grief.
- **Passage smoothing:** the BSB text used has no section headings, so smoothing stays at chapter level (below).
- **Three time scales:**
  - (a) Within a verse: word positions, eighth-note quantization and punctuation rests.
  - (b) The chapter arc: a Gaussian smoothing within the chapter ($\sigma=2$ verses, window ±6), so the music builds, peaks and settles.
  - (c) The canonical drift: the mean of the verse's book.
- **Combination:** $E=0.45\,\mathrm{pct}(\mathrm{raw})+0.35\,\mathrm{arc}+0.20\,\mathrm{book}$, where pct is the percentile across all 31,102 verses. It is stored as 2-digit integers, 190 KB in total.

**Sample values (build 2026101222).** The last four columns are each source's valence percentile.

| Verse | V | A | D | Label | Mode | BSB | WEB | Gloss | KJV |
|---|---|---|---|---|---|---|---|---|---|
| Genesis 1:1 | .77 | .28 | .67 | joy · still · majestic | Lydian | 94 | 94 | 98 | 97 |
| Psalm 22:1 | .58 | .39 | .41 | peace · moving · steady | Mixolydian | 48 | 40 | 97 | 28 |
| Psalm 23:1 | .43 | .32 | .37 | longing · still · humble | Dorian | 46 | 26 | 36 | 32 |
| Lamentations 1:1 | .36 | .73 | .36 | longing · stirring · humble | Dorian | 32 | 42 | 58 | 61 |
| John 11:35 | .23 | .69 | .17 | sorrow · stirring · humble | Aeolian | 0 | 0 | 2 | 0 |
| Revelation 21:4 | .40 | .57 | .43 | longing · moving · steady | Dorian | 19 | 27 | 4 | 26 |
| Psalm 150:1 | .84 | .49 | .75 | joy · moving · majestic | Lydian | 97 | 92 | 95 | 94 |

Known misses:
- Psalm 22:1 has a high gloss valence (dictionary glosses of the Hebrew words lack the cry of the verse), which lifts it to peace.
- Psalm 23:1 and Revelation 21:4 are dragged down by the chapter arc and by negated words that still score below neutral.

## 5. Visual
- The palette follows valence: hue $210-170V$, so cool blue at sorrow and warm gold at joy.
- Motion speed is ×$(0.5+A)$.
- The Eye waves and the Cymatics sand use the same palette and pace.
- Cymatics: the Chladni mode $(n,m)$ with $n^2+m^2$ nearest $5\cdot f/F_0$; a Bessel $J_0$ ripple dish; a Rubens' tube line of flames.

## 6. Res: the Resolution rule
1. Every verse ends V–I (authentic cadence). The cadential V always uses the leading tone 15/8, even in the minor-flavoured modes. A chapter's last verse ends IV–I (plagal "Amen" cadence).
2. A melody note ending a phrase (within about a beat before punctuation) moves to the nearest chord tone.
3. A final melody note on the tonic closes every verse.
4. Any other non-chord tone resolves stepwise to a chord tone within half a beat.

## 7. Other features
- **Speed reading (RSVP):** 1–5-word chunks with the focal letter highlighted. It follows narration boundary events or the estimate; with the voice off, about 97 WPM × speed.
- **Visual tab:** immersive view up to the dial's max (about 1000 WPM). Above the voice's limit, narration is muted.
- **Word mode** (default) vs **Live mode** (baseline, Room listening, Solfeggio).
- **Theta:** soft binaural beats, 4–8 Hz.
- **777 Hz:** a soft, symbolic layer.
- The 432 tuning option.
- Background and lock-screen play are kept alive by a near-silent carrier buffer.

## 8. Data sources and licences
| Data | Source | Licence |
|---|---|---|
| Hebrew lemmas | Open Scriptures Hebrew Bible (WLC) | CC-BY 4.0 |
| Greek lemmas | MorphGNT SBLGNT | CC-BY-SA 3.0 |
| English text (default) | Berean Standard Bible (BSB) | public domain |
| English text (option) | KJV | public domain |
| Emotion only | World English Bible (WEB, ebible.org) | public domain |
| Emotion only | Strong's Hebrew/Greek dictionaries (JSON: Open Scriptures) | public domain text; JSON CC-BY-SA |
| Cross-references and place names | OpenBible.info | CC-BY |
| Verse emotion | NRC VAD Lexicon | Free for research/non-commercial use with credit; commercial use needs NRC's consent; the lexicon must not be redistributed (only per-verse aggregates are shipped). If the app ever becomes commercial, switch lexicons or obtain consent. |

## 9. Real vs symbolic
**Real (measured from data):**
- Word counts, first appearances and co-occurrence.
- Cross-reference votes.
- Lexicon emotion ratings (crowd-sourced judgements of modern English words, applied to BSB/WEB/KJV text and to dictionary glosses of the original words, so ancient usage is only approximated).
- Physical formulas: Chladni, Bessel, standing waves.
- Measured loudness balance.

**Symbolic (design choices):**
- The Eye framing.
- $F_0=110$ Hz, the just scale and the golden-ratio spread.
- The emotion → mode mapping (a Western convention).
- The tempo and register ranges.
- The instrument choices.
- 777 Hz, the 432 option and Solfeggio (Puleo, 1970s numerology).

No frequency is named in scripture. This is a devotional mapping, not a treatment or a claim about the mind.
