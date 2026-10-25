# IG-DUO-01 local quality revision

Exactly two owner-review candidates: GV-003 and SS-LEARN-002. The original GV-001 and SS-001 are not rendered, edited or posted by these commands. Baseline examples are technical fixtures, not additional publishing candidates.

## Run

Python 3.13/Pillow 13.0.0 was actually tested here. Requirements were widened from <13 to <14 because the pre-existing signed runtime provides Pillow 13; newly downloaded Pillow 12 native extensions were blocked by macOS policy. No shared Python installation was changed. Unmodified original Git tests first failed because its macOS font location was inaccessible. Bundled SIL-OFL Atkinson Hyperlegible fonts fix that without proprietary/system font dependencies.

```sh
python3 -m pip install -r requirements.txt  # optional in a normal new venv; use existing environment if already satisfied
ffmpeg -version
ffprobe -version
python3 -m unittest discover -s tests -v
python3 quality/build.py --out /absolute/output
# Or just the two review candidates:
python3 quality/build.py --out /absolute/output --candidate-only
```

`ffmpeg` and `ffprobe` must be on PATH. On this machine FFmpeg 7.1 is the already-installed imageio-ffmpeg bundled executable, and actual FFprobe n8.1.1 runs through a local Node/WebAssembly adapter because native downloaded FFprobe binaries are blocked. Probe implementation and commands are recorded, not disguised as native FFprobe. The adapter and byte-pinned download instructions are supplied separately in the audit/source packet. It uses real FFmpeg FFprobe, not a lookalike metadata parser. Node v26.5.0 was tested. Regular small MP4 files are copied into memory; large media, playlists and stdin probing are not supported by the adapter.

## Output and gates

Each candidate has media, content.json, caption.txt, cover, layout-qc.json, qc-result.json, build-manifest.json and SHA256SUMS.txt. The source/spec/font hashes, exact commands, Git source revision, environment, actual probe JSON and full decode log are recorded. The external packet adds a human-review QC note and sources/rights list.

No code calls Instagram, schedules, publishes, grants access, touches account settings, collects private footage or spends money. Every candidate remains `public_post_approved=false` and `AWAITING_OWNER_APPROVAL`.

## What changed

- Baseline: explicit packaged open font, Pillow 13 compatibility, reject unbreakable text that exceeds panel width, reject non-false publication flag.
- GV-003: independent Bernoulli complement animation. Exact integer attempt count drives both the shrinking no-success area and the at-least-one-success area, then a probability curve. It is not a simulated run and does not claim 63 successes out of 100. Original synthesized tone cues, no third-party music.
- SS-LEARN-002: five distinct visual layouts, a practical closed-book question/check/correct/next-test sequence, and an explicitly illustrative percentage-change worked example. Research support is separated from the exact unvalidated three-line routine. No invented owner experience.
- Eight additional tests supplement the original two: arithmetic, diminishing returns, publication-gate types, unbreakable text, layout, non-static keyframes, exact area boundary, and carousel overflow rejection.

## Unresolved

Human APPROVE/REVISE still required. No engagement outcome is predicted. The true historical versions and exact render-time source bytes of GV-001/SS-001 remain UNKNOWN; recovered scripts and archived artifacts establish paths and intended engine, not bit-identical historical reproduction. The WASM FFprobe deployment source commit is UNKNOWN, so its actual downloaded bytes and runtime version are pinned separately. Native FFprobe and a fresh Pillow 12 venv remain blocked in this OS environment, with tested existing-runtime/WASM alternatives documented. Font license is in ../fonts/OFL.txt. No Squirrel diary can be made without approved real source footage.
