# KAN-449 / IG-DUO-01 candidate revision r2

Scope: revise only the existing GV-003 and SS-LEARN-002 review candidates. Owner disposition remains REVISE for both. No publishing, scheduling, account/profile edits, prior-post edits, new content IDs, or analytics-routine creation. KAN-449 remains In Review. GV-001 and SS-001 are not recreated.

## Shared typography
Lato Regular/Bold replaces the slashed-zero default through typography.py in both quality adapters and the base renderer. Bundled unmodified binaries and Lato-OFL.txt are from https://github.com/google/fonts/tree/main/ofl/lato (SIL OFL 1.1). Default zero has a clear center at the diagnostic size in both weights. Required arrow and math glyphs are checked against the missing-glyph mask. Font side bearings are accounted for in actual ink-bound positioning. Old Atkinson binaries are retained for provenance, not used by the revised defaults. A preliminary Noto Sans preview failed arrow-glyph coverage and was rejected before final output; it is not bundled as the chosen font.

## Grey: 29 seconds to 22 seconds
- 0–2.5s: establish the same independent 1% model and show a proportional area rather than simulated outcomes.
- 2.5–6s: compact counter/area progression to 68.
- 6–9.5s: hold 69 tries, first strictly above 50%: 50.016%; show 68 tries: 49.51% for comparison. Exact probabilities are 1 − 0.99^n; displayed percentages are rounded.
- 9.5–12.5s: compact progression from 69 to 100.
- 12.5–16.5s: hold 100 tries: 63.4%, alongside the 36.6% no-success complement.
- 16.5–22s: short complement derivation and a labelled diminishing-returns curve. Keep the model assumption and area-not-outcome disclosure visible; no luck or personal-diary framing.
- Three original synthesized cues align with 6.0/12.5/16.5s. Technical peak/timing checks do not constitute listening.

## Squirrel: concrete denominator error, not another generic study routine
Five illustrative cards: hook 80→100; diagnose 20/100 as the wrong growth base; establish (100−80)/80=25% using four original 20-unit parts; reverse-check 80×1.25=100 versus 80×1.20=96; transfer to 50→60 and 100→80. Keep arithmetic and reference bases distinct. Every card is labelled ILLUSTRATIVE EXAMPLE; no claim about the owner's life.

Actual visible-copy tokenizer: trim each rendered string and split on whitespace. Numeric and standalone-symbol tokens count; caption, alt descriptions, metadata duplicate titles and research annotations are excluded. Original 385 tokens; revised 304 tokens: 78.96% of before, 21.04% shorter. Original per-card counts 65/69/69/84/98; revised 47/63/68/58/68. Runtime layout QA records the actual text bounds for all rendered strings.

The two existing DOI records remain in the caption, with abstract-only evidence limits and study conditions. Neither paper is represented as testing these cards, the exact percentage-change task, a universal optimal interval, or guaranteed transfer.

## Reproduce only these two candidates
```sh
python3 -m unittest discover -s tests -v
python3 quality/build.py --candidate-only --out /absolute/output/path
```
The candidate-only flag intentionally avoids baseline/extra renders. 18 tests pass before the full encoded build. Render-time source hashes, font hashes, versions, logs and decoded-media QC are recorded by the build. Historical production tool versions and source-byte identity for GV-001/SS-001 remain UNKNOWN; this revision does not change that finding.

## Approval and unresolved review
Both candidates remain REVISE and public_post_approved=false. Technical QC PASS is not creative approval or publication authority.

[blocked] Direct human audio listening for volume, timbre and cue comfort is unavailable in this environment. Native decode, peak and measured event timing must be reported separately, never as a listening pass. Owner visual/audio and final-card approval remains pending after inspectable file delivery.
