# IG-DUO-01 — Minimal reproducible media pipeline v0.1

Two real Instagram accounts, one lightweight shared production harness. This is a **new offline baseline**, not a claim to reproduce GV-001/SS-001 pixel-for-pixel. The actual first published posts were approved and recorded at the [Notion control hub](https://app.notion.com/p/4037b981c514815e9eb1f5f5aacdb658) and [Jira KAN-438](https://bluebluerize900.atlassian.net/browse/KAN-438).

## Executable source

Uses **Python + Pillow + ffmpeg/ffprobe**. No Instagram API calls, OAuth code, credentials, paid software, scheduling or publishing.

```bash
python3 -m pip install -r requirements.txt
ffmpeg -version
python3 -m unittest discover -s tests -v
python3 render.py specs/SS-LEARN-002.json --out build/SS-LEARN-002
python3 render.py specs/GV-003.json --out build/GV-003
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -of json build/GV-003/GV-003.mp4
```

Expected outputs: 1080×1350 carousel PNGs, 1080×1920 30fps H.264/AAC 18s Reel, original frames, caption.txt, build-manifest.json with source + output SHA256 and measured codecs/duration. An offline version was test executed in ChatGPT on 2026-10-25: 2 tests PASS, ffprobe H.264/AAC 30fps 1080×1920, full video decode PASS, 5 PNG decode PASS. **Run the Git checkout and test it separately** before treating Git source as validated; do not claim unverified deployment.

## Workflows and gates

- **Grey**: original fact/puzzle → claim & mathematical assumption check → original drawing/meaningful visual proof → first hook + beat map → render preview → factual/rights/vertical/text/audio QA → owner approval → owner-published/approved official integration → native Insights.
- **Squirrel educational**: evidence-backed useful tip → 4–6 cards → explain limits + cite → render → privacy/rights/visual QA → owner approval → publish → review.
- **Squirrel diary**: optional real owner-approved clips and one genuine thought from the day → ingest only explicit private files → redact personal data → authentic edit; NO fabricated diary. The diary editor is **NOT** implemented in v0.1.
- **Do not automate public publishing**. First GV-001/SS-001 approval was per two exact posts only. A created MP4 is not permission to publish further posts.
- Public Git holds generic code/templates/brand assets only, never private Squirrel images, location, camera-roll backups, auth cookies or unredacted screenshots.

States: IDEA → CLAIM_QA → SOURCE_APPROVED → SCRIPT → RENDERED → TECH_QA → EDITORIAL_QA → AWAITING_OWNER_APPROVAL → APPROVED → POSTED → OBSERVED.

Source spec fields: id, account, format, title, rights, evidence[], items[]. Reel scenes need duration in seconds. Renderer rejects missing rights declaration and rejects a source claiming the post is already approved. Rights is an **attestation, not an automated license check**. Outputs always say public_post_approved: false.

## Important quality note

This MVP demonstrates a standard reproducible media pipeline and QA contract. The video uses **static scene cuts** with a simple probability grid. It is not yet the dynamic visual storytelling needed to optimize Grey engagement. Aside should add *content-specific* motion modules only after storyboards are approved: e.g. animated time scale, exact probability reveal, original physical/geometric animation. Do not mass-upload variations of one generic template or embellish with needless zooms. For Squirrel, prioritize visually relaxed real materials over overdesigned AI-looking cards.

## Ownership and next proof tasks

1. Aside checks out this Git branch and reports tests, actual ffprobe and source code hash.
2. Recover/source-audit **actual GV-001 and SS-001 project code** from creator session. Jira attachment has final binaries and QA bundle but no verified renderer library names. Do not invent the original source pipeline.
3. Refine one Grey scene animation and one Squirrel sample carousel with before/after previews and QA.
4. Maintain one content_id and build-manifest.json per exported asset; attach hash/preview and actual post ID to Jira/Notion.
5. Capture 24h/72h/7d native Insights for both existing posts. Aside already scheduled follow-up checks, so do not duplicate.

[Official Instagram Reel upload specifications](https://www.postman.com/meta/instagram/folder/y6xustx/reels-publishing).
