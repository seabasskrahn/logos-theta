# Sonolumina (Logos Theta)

Bible audio web app: scripture narration with a tone layer built from each word's own codebook (how the word is used in the Bible) and an emotion-driven score. Live at https://seabasskrahn.github.io/logos-theta/. Full algorithm: `SONOLUMINA_ALGORITHM.md` (design repo).

## Texts and data credits
- **Berean Standard Bible (BSB)**: public domain (Berean Bible, bereanbible.com). Default reading and narration text (`bsb/`).
- **King James Version (KJV)**: public domain. Selectable translation; also the versification base (`kjv/`).
- **World English Bible (WEB)**: public domain (ebible.org). Used only for emotion scoring; not shipped.
- **Hebrew**: Westminster Leningrad Codex via Open Scriptures Hebrew Bible (OSHB). **Greek**: MorphGNT/SBLGNT lemmas; Scrivener 1894 TR text.
- **Strong's Hebrew and Greek dictionaries**: public domain; JSON by Open Scriptures (CC-BY-SA). Glosses used for emotion scoring only.
- **NRC VAD Lexicon** (Saif M. Mohammad, National Research Council Canada, 2018): non-commercial use with credit. Only per-verse aggregates are shipped (`vad/`).
- **OpenBible.info**: cross references and place geocoding (CC-BY).

## Build tools
`tools/build_bsb.py` → `bsb/`; `tools/build_codebook.py` → `codebook/` (KJV entries, plus BSB-only English stems); `tools/build_vad.py` → `vad/` (BSB 0.35 / WEB 0.25 / glosses 0.30 / KJV 0.10 blend with negation handling). Sources go in a folder passed as the first argument.
