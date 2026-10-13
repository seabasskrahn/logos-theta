# Sonolumina: free and local options for the offline orchestrator, voice and music (October 2026)

Prepared Oct 12, 2026 (MT). This replaces the paid-API plan; see `ai-orchestrator-apis-2026-10.md` for that.

Labels used in this report:
- **"Source"** means the figure is quoted from the cited page. Many of these are third-party roundups; I have marked those, so check them before relying on them.
- **"Estimate"** means my own arithmetic from the stated assumptions. It is not a measured benchmark.
- **"Not published"** means I could not find an official figure.

## Key sources
- Local LLM picks by VRAM (Oct 2026): https://vdf.ai/blog/best-local-llm-by-vram/ and https://vdf.ai/blog/best-local-llm-for-agents-tool-calling/
- Structured output with local models (May 2026): https://insiderllm.com/guides/structured-output-local-llms/
- gpt-oss JSON problems under Ollama: https://openticketai.com/en/docs/blog/best-ollama-model-zammad-ai/
- Gemini rate limits (official, updated 2026-10-09): https://ai.google.dev/gemini-api/docs/rate-limits
- Free tier roundups checked Oct 12, 2026 (third-party): https://freellm.today/ , https://gravity.fast/data/free-llm-api-tiers/ , https://decodethefuture.org/en/best-free-llm-apis-2026/ , https://capitalandcompute.net/blog/how-to-test-llm-apps-without-paying-for-tokens/
- Cerebras limits (official): https://inference-docs.cerebras.ai/support/rate-limits
- TTS: https://localaimaster.com/blog/best-local-tts-models , https://localaimaster.com/blog/kokoro-vs-xtts-vs-chatterbox , https://gigagpu.com/tts-latency-benchmarks/ , https://github.com/SWivid/F5-TTS , https://docs.coqui.ai/en/stable/models/xtts.html
- Music: https://github.com/ace-step/ACE-Step-1.5 , https://huggingface.co/ACE-Step/Ace-Step1.5 , https://songcreator.pro/blog/best-open-source-ai-music-models , https://boppy.me/blog/best-open-source-ai-music-models

---

## 1. Local LLMs (Ollama, LM Studio, llama.cpp)

**How to get reliable JSON:**
- Pass a JSON Schema in Ollama's `format` field. Ollama converts it to a grammar, which guarantees syntactically valid output. Generation is about 30–80% slower with the grammar on (insiderllm).
- llama.cpp offers the same thing via `--grammar`/GBNF. LM Studio also supports structured output.
- Turn **thinking/reasoning off** on Qwen 3.x and Gemma 4. Otherwise the JSON can end up in `reasoning_content` instead of the answer (insiderllm, openticketai).
- Validate every response against the schema anyway (Pydantic or Instructor) and retry any that fail.

| Hardware tier | Recommended model (Oct 2026) | Size at 4-bit | Licence | Notes |
|---|---|---|---|---|
| CPU-only, 16–32 GB RAM | Qwen3.5-4B, Gemma 4 E4B, or Qwen 2.5 7B (a known-good budget JSON model) | ~3–5 GB of RAM | Apache 2.0 | Works, but slowly. Use the smallest model that passes your quality test set. |
| 8 GB GPU (RTX 4060/3070/5060) | **Qwen3.5-9B Q4_K_M** (vdf.ai's pick for 8 GB), or Gemma 4 E4B | about 6 GB | Apache 2.0 | Leaves about 46K tokens of context, plenty for one chapter at a time. |
| 12 GB GPU | Gemma 4 12B Q4_0 | | Apache 2.0 | |
| 16 GB GPU | gpt-oss-20b (12.1 GB, MXFP4), Gemma 4 12B Q8, or Qwen3.6-35B-A3B with `--cpu-moe` | 12–17 GB | Apache 2.0 (gpt-oss adds a usage policy) | **gpt-oss has documented broken JSON under Ollama** (openticketai), so test it before relying on it. |
| 24 GB GPU (3090/4090) | **Qwen3.6-35B-A3B Q4_K_M** (~22 GB, only 3B parameters active, so it is fast), Gemma 4 26B-A4B (~18 GB), Qwen 3.6-27B dense (~17 GB), Mistral Small 3.2 24B | 17–22 GB | Apache 2.0 | The strongest open pick for JSON in Oct 2026 (vdf.ai, insiderllm). |

Other model families:
- **DeepSeek V4:** good structured output, but too large for home PCs at the useful sizes.
- **Llama:** not a top JSON pick in the current roundups.

**Throughput:** I found no single vendor benchmark covering these exact setups. gpt-oss-20b on 16 GB is quoted at "~140 tok/s" (insiderllm/vdf summary). For planning I used these rough **estimates**:
- CPU-only, 4–8B model: about 5–15 tokens/s.
- 8 GB GPU, 9B model: about 30–60 tokens/s.
- 24 GB GPU, 35B-A3B MoE: about 60–120 tokens/s.

**Estimate: how long scoring the whole Bible once would take.**
- Assumptions:
  - 1,189 chapters, about 26 verses each, processed one chapter per call.
  - Each call has about 3,000 tokens of fixed instructions/schema plus about 1,500 tokens of verse text.
  - Each verse's output is compact JSON of about 40 tokens (emotion vector, tempo, cadence id, cross-reference ids), so about 1,000 output tokens per chapter.
  - That totals roughly **5.4M input tokens and 1.2M output tokens**.
  - Keep the fixed prefix identical on every call so llama.cpp/Ollama can reuse its KV cache and only process the new verse text.
- Results:

| Tier | Generation time | With prompt processing and retries |
|---|---|---|
| 24 GB GPU (~100 tok/s) | about 3.5 h | **about 4–6 hours** |
| 8 GB GPU (~40 tok/s) | about 8.5 h | **about 10–14 hours**, i.e. one night |
| CPU-only (~8 tok/s) | about 42 h | **about 2–4 days** in the background, resumable chapter by chapter |

- This is a **one-time** job. Its output is static JSON of only a few MB for the whole Bible.
- For a deterministic result, set temperature to 0 and a fixed seed. Then spot-check, for example, Psalms and the Gospels by hand.

## 2. Free hosted tiers (as of Oct 12, 2026)

| Service | Free limits | Data / training | Does ~1,200 chapters (~6.6M tokens) fit? |
|---|---|---|---|
| **Google AI Studio (Gemini free tier)** | Limits are set per project and model and are **shown only in AI Studio; no figures on the public page**. Daily quotas reset at midnight PT. Experimental and preview models get lower limits (official rate-limits page). | Free-tier content **"used to improve our products"** (official pricing page). The capitalandcompute roundup says this applies outside the EEA, Switzerland and UK. | Probably yes over a few days. Unverified, because the limits aren't published. Note the Batch API needs the paid tier. |
| **Groq** | 30 requests/min, 1,000/day, **8K tokens/min and 200K tokens/day per model** (gpt-oss-120b, gpt-oss-20b, Qwen3.8 27B) (freellm/gravity) | "Not retained by default; zero data retention available" (decodethefuture) | Daily token cap: about **33 days** on one model, about 11 days rotating across 3 models. Feasible, but slow. |
| **OpenRouter `:free` models** | 20 requests/min, **50 requests/day** (1,000/day after buying $10 of credits once, which is not free) | Depends on the upstream provider | 1,189 requests at 50/day is about 24 days. Free models can be withdrawn at any time. |
| **Cloudflare Workers AI** | 10,000 Neurons/day (about 244K tokens/day on gpt-oss-120b per decodethefuture), 300 requests/min | "Not used for training" (decodethefuture) | About 27 days. |
| **Mistral free plan** | $10/month of API credits. Rate limits are shown only in the console. | **Trains on free-plan data unless you opt out** (decodethefuture, capitalandcompute) | Possibly, within the credit. |
| NVIDIA build.nvidia.com | Listed as having a free offer (freellm). Limits are not published in the sources I read. | Not verified | Unknown |
| **Cerebras** | **Not a free tier.** A $5 credit that lasts 30 days and requires a payment method (official docs). | | No, as a lasting free option. |
| **GitHub Models** | **Retired July 30, 2026** | | No. |
| Hugging Face | No monthly credits for free accounts any more (freellm) | | No. |

**Verdict:** the free tiers can do a one-time pass if you spread it over days to weeks and rotate providers. But terms change constantly, and Gemini's free tier means Google may use the data. Scripture is public, so that matters less here than usual. Free tiers suit spot checks and comparisons; a local model is the dependable route.

## 3. Free local TTS

| Model | Licence | Quality | Speed | Hardware |
|---|---|---|---|---|
| **Kokoro-82M** | **Apache 2.0** (commercial OK) | Clean, natural narration with 54 built-in voices and 8 languages. **No voice cloning.** | GPU real-time factor 0.03 on an RTX 4060 Ti, so a 10-second clip takes about 0.3 s (gigagpu). On CPU it is "faster than real time" (localaimaster). | About 2–3 GB of VRAM, or CPU |
| **Piper** | **GPL-3.0** (current fork) | Decent, but more robotic | Fastest on CPU; real-time factor 0.04 on GPU | Under 1 GB, CPU-first |
| **Chatterbox** (Resemble AI) | **MIT** | Most expressive. Has an emotion "exaggeration" dial and about 5 s zero-shot cloning. Resemble's own blind test claims listeners preferred it to ElevenLabs (vendor claim). | Real-time factor 0.12 on a 4060 Ti | About 4–6 GB of VRAM; GPU recommended |
| F5-TTS | Code MIT, **weights CC-BY-NC (non-commercial)** | Excellent cloning | Real-time factor about 0.15 (PyTorch) | 4–8 GB |
| XTTS v2 (Coqui) | **CPML, non-commercial**. Coqui shut down in Jan 2024. | Strong 17-language cloning | Real-time factor 0.30 on a 4060 Ti | 4–6 GB |

The app is free, but stick to Apache, MIT or GPL weights anyway so donations or redistribution never become a problem.

**Estimate: pre-rendering a full Bible narration.**
- Length: about 783k words (KJV) at about 150 wpm comes to **about 87 hours of audio**.
- Render time:
  - Kokoro on a mid-range GPU (real-time factor about 0.03–0.05): **about 3–5 hours**.
  - Kokoro on CPU: assuming a real-time factor of 0.2–0.5 (my assumption), **about 17–45 hours**.
  - Chatterbox on an 8–16 GB GPU (real-time factor about 0.12): **about 10–12 hours**.
- File size:
  - Mono Opus at 24 kbps: about **0.95 GB**.
  - Opus at 32 kbps: about 1.25 GB.
  - MP3 at 64 kbps: about 2.5 GB.
- Hosting: GitHub Pages recommends keeping a published site under about 1 GB, and blocks files over 100 MB. So host the audio separately (for example a GitHub Release or a separate repo per testament, per-chapter files loaded lazily), or ship only a starter set. GitHub's limits are from my general knowledge of GitHub's docs; I did not fetch them this session, so confirm at docs.github.com.
- Use the **KJV/WEB** (public domain) as the text source. Modern translations' audio rights are restricted.
- An alternative with no hosting at all: run Kokoro **in the browser** via the kokoro-js/ONNX web builds. Those exist, but I didn't verify their performance this session.

## 4. Free local music generation

| Model | Licence | Hardware | Realism / fit |
|---|---|---|---|
| **ACE-Step 1.5** | **MIT**. Commercial use allowed; trained on licensed, royalty-free and synthetic data (HF card). | **Under 4 GB VRAM** for the 2B turbo model. 8–16 GB for 2B plus its language model. The XL (4B) model needs 12 GB with offload or 20 GB+ without. | Full songs, vocals optional, 50+ languages. A full song takes under 10 s on an RTX 3090 (vendor claim). This is the most realistic free option. |
| Stable Audio Open 1.0 | Stability Community License: free, including commercial use, under $1M/yr revenue | About 12 GB | Up to 47 s clips at 44.1 kHz. Best for **ambient textures, pads, drones, SFX**. Weak structure, no real vocals. |
| MusicGen (AudioCraft) | Code MIT, **weights CC-BY-NC 4.0 (non-commercial)** | 8–16 GB | 30 s instrumental. Dated. |
| YuE / YuE2 | Conflicting reports: one source says non-commercial by default, another Apache 2.0 with credit. **Check the repo before use.** | 16 GB minimum, 24 GB+ in practice. Minutes of compute per 30 s even on a 4090. | Highest quality for full songs with vocals, but heavy. |
| Magenta RealTime | Apache 2.0 code, CC-BY weights (boppy) | Not checked | The only *streaming* open option. I did not evaluate it in depth. |

**Compared with the existing Web Audio synth:** generated tracks sound more "produced", but they are opaque audio files. They cannot follow the per-verse emotion curve, timing and cadences note by note, and each one adds megabytes to download. The synth is algorithmic and synced, with zero download and full control, which is exactly what makes Sonolumina distinctive.

**Best use of AI music:** pre-render a small library of royalty-free ambient beds with ACE-Step or Stable Audio Open, for example about 20 loops tagged by mood (lament, praise, peace and so on). The app can then crossfade them *under* the live synth according to the emotion scores. That is optional; skipping it keeps the app pure.

## 5. Recommended setup

**Pipeline (all offline, run once, output static files):**
1. **Orchestrator:** a Python script plus Ollama.
   - Model: **Qwen3.6-35B-A3B** on 24 GB, **Qwen3.5-9B** on 8 GB, or **Qwen3.5-4B / Qwen 2.5 7B** on CPU.
   - Settings: thinking off, temperature 0, JSON Schema in `format`.
   - Run one chapter per call, cache-friendly fixed prefix, validate, retry, and checkpoint each chapter to `data/chapters/BOOK_CH.json`.
2. **A deterministic layer stays in code.** The codebook lookup, timing maths, cross-reference graph and cadence rules should remain JS/Python. Ask the LLM only for the fuzzy, judgment-based part (emotion nuance per verse, choosing a cadence from a fixed list). That makes it narrow and reliable.
3. **Voice (optional):** Kokoro (Apache 2.0) to pre-render KJV or WEB chapters as Opus (about 1 GB in total). Use Chatterbox (MIT) instead if you want more expressive delivery and have a GPU.
4. **Music:** keep the Web Audio synth. Optionally add a few ACE-Step (MIT) ambient beds.
5. **Playback:** fully client-side (static JSON, Web Audio, canvas, optional audio files). No API keys, no server, works offline.

**Hardware needs:**

| Tier | What works | Approximate one-time build time (estimate) |
|---|---|---|
| CPU-only (any modern 6–8 core, 16 GB RAM; 32 GB is better) | 4–8B LLM, Kokoro or Piper. Skip music generation. | LLM 2–4 days; narration about 1–2 days. Both can run overnight and resume. |
| 8 GB GPU (RTX 3060/4060 class) | 9B LLM, Kokoro or Chatterbox, ACE-Step 2B turbo | LLM about half a day; narration under 1 day |
| 16–24 GB GPU (4070 Ti Super/3090/4090) | 35B-A3B LLM (best JSON quality), Chatterbox, ACE-Step XL, Stable Audio Open | LLM about 4–6 h; narration about 3–12 h |

**Tradeoffs:**
- Local quality is below the frontier paid models, so build a hand-labelled test set of about 50 verses and compare models against it.
- Large audio files complicate GitHub Pages hosting.
- Electricity is the only running cost.
- Free hosted tiers are a fine supplement (Groq for quick model comparisons, the Gemini free tier for spot checks), but they should not be the core path.

**Honest bottom line:** the cheapest and most reliable option is still to keep the runtime fully client-side, use a local LLM **once** at build time for the fuzzy emotion layer, and leave everything else in deterministic code.
