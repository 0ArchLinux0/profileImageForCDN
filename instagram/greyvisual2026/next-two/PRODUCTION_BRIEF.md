# GV next two — Production & release gates (2026-10-26)

## Scope

Produce exactly two **new original English Reels** for existing `@greyvisual2026`:
- **First release candidate: GV-004**, Geometry — same perimeter / different area
- **Second release candidate: GV-002**, Chance — 23-person birthday paradox

IDs remain GV-004 and GV-002 even if scheduled/reviewed in this order. Existing live GV-001 / GV-003 are immutable. Everything in this branch is **planning and code-backed truth specification**, NOT a claim of full video rendering or approval. Use the existing local Aside `Python + Pillow + FFmpeg` renderer and `quality/build.py` output pattern. Prior production baseline is PR #3 / IG-OPS-01.

## Brand grammar

Brand headline: **Grey Visual — Guess first. See why.**
- Dark graphite `#252729`, warm ink `#F4F0E7`, lime `#D6DF98`.
- Crisp, normal numeral zero, consistent typographic sizes, phone-legible at 360px, one focal point per time range.
- **Motion must carry mathematical meaning** (geometry with fixed perimeter, birthday count and exact cumulative probability), not needless camera zooms/flash/strobe.
- No false "99% can't solve", fake survey percentages, unlicensed music, copied reels, AI-generated fake experiments or randomly colored 'successes' that look like observed facts.
- Portrait 1080×1920, 30fps H264 yuv420p. Audio: default **silent** to match already released Grey; optional original/licensed sound variant for owner's direct listening, never compulsory.
- No upfront product funnels, paid tools, subscriptions, new accounts or external posting automation.

## Creative-specific cautions

**GV-002:** Compute exact recurrence for P(all different), not 253 independent pairs; n=22 47.569531%, n=23 50.729723%. The number of unordered pairs is `23*22/2=253`, but pair-match events are dependent. Birthday distribution is idealized uniform/independent; no real group is sampled or represented.

**GV-004:** Both outline shapes must preserve **same pixel scale**. Both have `P=100`; areas are 400 and 625. Morph needs `w+h=50` EVERY displayed frame; anchor camera and scale instead of warping drawing with false labels. The square maximizes area **among rectangles** with that perimeter; do not claim this over all planar shapes.

## Minimum creative deliverables per Reel

1. Exact content ID + final JSON spec and evidence/assumptions list.
2. Original source code and parameters; minimal reusable scene module integrated to existing project (don't fork a competing renderer).
3. **Three deliberate motion beats** visible on 360px previews; screenshot of hook/turning point/payoff; 16–24s MP4 preview, 1080×1920 30fps H264.
4. 1 cover PNG and English caption with verified math/scope.
5. Actual `ffprobe`, full decode, 360px text crop, text overlap, safe UI region, no flashy meaningless zoom, factual invariant tests, original rights/license/privacy, `SHA256SUMS.txt` / manifest + audio state.
6. Side-by-side Creative QA discussion: would first 1.5s be understandable without sound; is reveal legible; are surprises explained instead of merely asserted?
7. **Owner-approved exact video** (creative) is separate from **explicit authorization to publish or schedule**. The prior GV-001/GV-003 approval does not transfer. If Instagram publisher fails, check actual profile/post count before any retry.

## Existing results & metrics

- User says both prior published Grey reels exceeded 120 views by 2026-10-26. Treat this as a **user-reported lower bound**, not platform-exported exact Insight.
- The Metricool connected brand `7283977` reports only TikTok and YouTube; **NO Instagram network** for Grey. Do not repurpose it, assume access, invent view stats, or buy a plan.
- Owner-authenticated Instagram Insight for each published URL: capture at same elapsed-age windows 24h/72h/7d if available; no duplicate background automations. Store `views`, `reach`, `non_follower_reach`, `average_watch_seconds`, `shares`, `saves`, `likes`, `follows_attributed`, and time/cost to produce. Unavailable= `NULL`.
- Interpret four posts as a **pilot** not causal A/B: the two new topics are intentionally different. Note topic/timing/runtime as confounders.

## No required deliverable beyond next 2

Do not automatically make GV-005 or go into general templated production. Next user gate: return exactly two full preview packages, one per ID, with evidence and optional rankings of what creative could be improved. No posting in this request without separate explicit user approval.
