# Sonolumina: should it get an AI orchestrator? API comparison (October 2026)

Prepared Oct 12, 2026 (MT). All prices are USD list prices, taken from the official pricing pages fetched today unless a line says otherwise. Promos and price changes are flagged where they apply. **Where a vendor does not publish a figure, this report says "not published".** Most vendors do not publish latency numbers, so latency is given only where a vendor states one.

## Sources
- OpenAI API pricing: https://platform.openai.com/docs/pricing
- Gemini API pricing (last updated 2026-10-09): https://ai.google.dev/gemini-api/docs/pricing
- Lyria RealTime docs: https://ai.google.dev/gemini-api/docs/realtime-music-generation and https://ai.google.dev/gemini-api/docs/models/lyria-realtime-exp
- Anthropic pricing: https://docs.anthropic.com/en/docs/about-claude/pricing
- xAI models and pricing: https://docs.x.ai/docs/models
- ElevenLabs API pricing: https://elevenlabs.io/pricing/api
- Stability, Suno and Lyria third-party summary: https://aimusicapi.ai/en/blog/ai-music-generation-api-comparison (third-party source; Stability's own page was not fetched)
- Suno API status (third-party): https://sunnoai.com/music-generation-api/ and https://kunavo.com/guides/suno-api
- fal: https://fal.ai/pricing · Runway: https://docs.dev.runwayml.com/guides/pricing/ · Luma: https://lumalabs.ai/api/pricing

## 1. Orchestrator LLMs (they hold the large fixed source prompt)

| Model | Input $/M | Cached input $/M | Output $/M | Context and caching notes |
|---|---|---|---|---|
| **Gemini 3.8 Flash** | 0.75 (rises to 1.50 on Jan 1, 2027) | 0.075 (0.15 from 2027), plus storage of $0.50/M tokens per hour | 3.75 (7.50 from 2027) | Explicit context caching on the paid tier. The 1M context figure comes from a third party (seminal.ai). |
| Gemini 3.5 Flash-Lite | 0.30 | 0.03, plus storage of $1/M per hour | 2.50 | Cheapest Gemini that does the job reasonably. |
| Gemini 3.1 Pro Preview | 2.00 (≤200k) | 0.20 | 12.00 | Preview model. |
| **OpenAI gpt-6-luna** | 0.10 | 0.01 (cache writes cost 0.125) | 0.50 | "Short context" pricing applies up to 272K input tokens. |
| OpenAI gpt-6.1-sol | 2.00 | 0.10 | 10.00 | Flagship-class model. Flex tier is half price. |
| OpenAI gpt-5.4-mini | 0.75 | 0.075 | 4.50 | |
| **Claude Haiku 5.5** | 0.10 (prompts ≤100k), 0.50 (>100k) | 0.01 (≤100k) | 0.50 (≤100k) | Keep the source prompt under 100k tokens or every price is 5×. Cache writes are 1.25× (5-minute) or 2× (1-hour). |
| Claude Sonnet 5.5 | 2.00 | 0.10 | 10.00 | Full 1M context at standard price on 4.6+ models. |
| Claude Opus 5.5 | 4.00 | 0.20 | 20.00 | |
| xAI grok-4.3 | 1.25 (<200k) | 0.20 | 2.50 | 1M context |
| xAI grok-4.7 | 2.00 | 0.50 | 6.00 | 500k context |

Latency: none of these vendors publishes a time-to-first-token figure on its pricing pages (**not published**). Anthropic and OpenAI do sell paid "Fast" tiers (Opus at $8/$40 per M; OpenAI Fast is about 2× standard).

Fit for "one agent, one system": all of them handle a long fixed system prompt plus tool calling. The things that actually separate them are the cache-read price and the cache rules:
- Anthropic and OpenAI cache-read rates are very low.
- Gemini also charges hourly storage for explicit caches.
- Anthropic Agent SDK / Managed Agents add $0.08 per session-hour.

Claude has no audio or image generation, so it would have to call other services for voice and music.

## 2. Real-time voice (speech-to-speech) and TTS

| Option | Price | Latency / real-time |
|---|---|---|
| Gemini 3.8 Live / 3.1 Flash Live | Audio in $0.005/min, audio out $0.018/min (text out $4.50/M) | Described as "low-latency audio-to-audio"; no millisecond figure published. |
| OpenAI gpt-realtime-2.1 | Audio $32/M in, $64/M out (cached audio input $0.40) | Realtime API. Latency not published on the pricing page. |
| OpenAI gpt-realtime-2.1-mini | Audio $10/M in, $20/M out | Same as above. |
| OpenAI gpt-live-1 | $0.05/min plus backend model usage | |
| xAI Grok Voice (speech to speech) | $0.08/min | |
| **Gemini 3.8 Flash TTS** | $0.00225 per 10 s ≈ **$0.0135/min** (doubles Jan 1, 2027) | Batch tier is half price. |
| Gemini 3.8 Flash-Lite TTS | $0.0015 per 10 s ≈ $0.009/min (doubles in 2027) | Described as "low-latency". |
| OpenAI tts-1 / tts-1-hd | $15 / $30 per 1M characters | |
| OpenAI gpt-4o-mini-tts | Text in $0.60/M, audio out $12/M | |
| xAI TTS | $15 per 1M characters | |
| **ElevenLabs v4 Turbo** | $0.04 per 1K characters (promo $0.011 ends Oct 12) | **~100 ms** stated by the vendor |
| ElevenLabs Flash/Turbo | $0.04 per 1K characters | **~75 ms** stated |
| ElevenLabs v4 / v3 | $0.08 per 1K characters | Most expressive voices. |

Scripture narration does not need a conversational speech-to-speech model. Plain TTS of verse text is cheaper and easier to control.

## 3. Music generation

| Option | Price | Real-time? |
|---|---|---|
| **Lyria RealTime (`lyria-realtime-exp`)** | **Not published** on Google's pricing page (experimental) | Yes. Streams 48 kHz stereo PCM over WebSocket. You steer it with weighted prompts, BPM, density, brightness and scale. Control latency is **max 2 s**. Instrumental only. Changing BPM or scale requires a reset. |
| Lyria 3.5 (full song) | $0.08 per song | No, it renders whole songs. |
| Lyria 3 Clip Preview (30 s) | $0.04 per clip | No. |
| ElevenLabs Music | $0.15/min (5 min max) | No, it renders files. |
| Stability Stable Audio 2.5 | ~$0.20 per generation (20 credits at $0.01), up to 3 min | No. Figure is from a third-party summary; Stability's own page was not checked. |
| Suno | **No public self-serve API.** A curated partner program was announced July 2026 with no price published. Third-party wrappers are unofficial. | No. |

## 4. Images and video (only relevant if you want pre-rendered art)

- **Images:**
  - Gemini Nano Banana 2.1: $0.0336 per 1K image.
  - Gemini 3.1 Flash Image: $0.067 per 1K image.
  - xAI grok-imagine-image: $0.02 per image.
  - OpenAI gpt-image-2: $30 per 1M image output tokens. OpenAI points to its calculator instead of a per-image price.
  - fal Z Image Turbo: $0.005 per megapixel.
  - Runway muse_image: 1 credit ($0.01).
  - Luma Uni-1.1: ~$0.04 per 2K image.
- **Video:**
  - Veo 3.1 Lite: $0.05/s (720p). Veo 3.1 Fast: $0.10/s. Veo 3.1 Standard: $0.40/s.
  - Gemini Omni Flash: ~$0.10/s.
  - grok-imagine-video-1.5-lite: $0.02/s.
  - Luma: $0.15 per 5 s at 540p.
  - Runway gwm1_avatars (real-time): 2 credits per 6 s.
- None of these is a real-time cymatics renderer. They produce minutes of output per dollar, while a canvas or WebGL frame costs nothing and renders in under 16 ms on the user's GPU.

## 5. Recommendation (hybrid)

1. **Orchestrator: Gemini 3.8 Flash**, with **gpt-6-luna** or **Claude Haiku 5.5** as the budget alternatives.
   - Use it **offline/ahead of playback**, not per audio frame. Give it the cached source prompt plus a chapter's text, and have it return a JSON "score": per-verse emotion values, timing, cross-reference links, cadence choices and TTS text.
   - Cache that JSON in localStorage or a static file on GitHub Pages. After that, playback costs nothing and has zero latency.
   - Gemini is the convenient pick because one API key also covers TTS, Live and Lyria.
   - On pure token cost, gpt-6-luna ($0.01/M cached) and Haiku 5.5 (≤100k prompt) are about 10× cheaper. Test quality on the emotion-scoring task before choosing.
2. **Voice: Gemini 3.8 Flash TTS** (~$0.81/hr of speech at today's price) for cost. **ElevenLabs Flash or v4 Turbo** (~75–100 ms, about $2/hr) if you want the best voice and the lowest latency. Cache the generated verse audio so each verse is paid for only once. The Bible is finite, so re-listening is free.
3. **Music: keep the Web Audio synth**, because it is the core of the algorithm and already real-time. If you want AI texture, Lyria RealTime is the only streaming option, but its price is not published and the model is experimental. Use it as an optional ambient layer you steer from the emotion scores.
4. **Visuals: stay client-side.** Cymatics are deterministic physics/maths (Chladni patterns, standing waves) driven by the audio you already generate. Generative video costs $0.02–$0.40 per second, renders slowly, cannot sync to live audio, and adds nothing the canvas does not already do.
5. **API keys:** GitHub Pages cannot hide keys. You would need a small proxy (for example a Cloudflare Worker or a Vercel function) or have users bring their own key.

## 6. Rough monthly cost: ESTIMATE, light personal use (1 hr/day, 30 days)

Assumptions:
- 50k-token source prompt, cached.
- 30 orchestrator calls per hour, each with 1k new input tokens and 500 output tokens.
- About 50k characters of narration per hour (~150 wpm).
- Today's list prices, no free tier.

| Component | Per hour | Per month |
|---|---|---|
| Gemini 3.8 Flash orchestrator: 1.5M cached tokens ($0.11) + storage ($0.025) + 30k input ($0.02) + 15k output ($0.06) | ~$0.22 | **~$6.60** |
| gpt-6-luna orchestrator, same load | ~$0.03 | ~$1 |
| Claude Haiku 5.5, same load (prompt ≤100k) | ~$0.04 | ~$1.20 |
| Claude Sonnet 5.5, same load (with 1-hour cache write) | ~$0.56 | ~$17 |
| Gemini 3.8 Flash TTS, 60 min of speech | ~$0.81 | ~$24 (~$48 after Jan 1, 2027) |
| ElevenLabs Flash/v4 Turbo (50k characters at $0.04/1K) | ~$2.00 | ~$60 |
| OpenAI tts-1 or xAI TTS ($15 per 1M characters) | ~$0.75 | ~$22 |
| ElevenLabs Music, if generated continuously | $9.00 | ~$270 (why AI music should not run continuously) |
| Lyria RealTime | not published | unknown |

**A typical hybrid, Gemini Flash orchestrator plus Gemini TTS, comes to roughly $30/month without caching. If generated verse audio and scores are cached and reused, it falls toward a few dollars a month.** The Gemini free tier, for testing in AI Studio, could cover prototyping. Note that free-tier content is used to improve Google's products.

## 7. The honest case for keeping it all client-side

- The "algorithm" (codebook, emotion scoring, timing, cross-reference network, cadences) is already deterministic code. An LLM re-reading it in a prompt is slower, costs money every time, and is **non-deterministic**: the same verse could come out different on each play, which is bad for a scripture app.
- Real-time feel: Web Audio and canvas respond in milliseconds. Network round-trips plus model latency (vendors don't publish figures, and Lyria's control latency alone is up to 2 s) can only make it worse.
- Cost and hosting: $0 today, with no backend, no API keys, no rate limits and no vendor deprecations. Gemini 2.5 Flash Image, for example, shut down on Oct 2, 2026, and many Gemini prices double on Jan 1, 2027.
- Privacy and offline use: the app keeps working without a connection.
- Where AI does help: as a **build-time** tool. Use it to enrich the codebook, pre-compute emotion scores for all ~31k verses once (with the Batch API at 50% off, a few dollars total), or pre-render narration. Then ship static JSON and audio. You get the AI's benefit with none of the runtime cost or latency.
