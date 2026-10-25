# SS-LEARN-002: source and rights record

One review candidate; five 1080 × 1350 cards. No publication action.

## Primary evidence inspected

1. Roediger & Karpicke (2006), *Test-enhanced learning: Taking memory tests improves long-term retention*. DOI 10.1111/j.1467-9280.2006.01693.x. https://pubmed.ncbi.nlm.nih.gov/16507066/
   - Primary abstract inspected via web search retrieval on 2026-10-25. Direct webfetch returned an empty readable body; full text was not inspected.
   - Two experiments: prose passages; free recall without feedback versus restudy; final tests after 5 minutes, 2 days or 1 week. Restudy won at 5 minutes; testing won on delayed tests.
   - Supports the retrieval-versus-familiarity distinction and using a closed-book answer. Does not establish journaling/reflecting as retrieval practice or validate this routine.
2. Butler, Karpicke & Roediger (2008), *Correcting a metacognitive error: Feedback increases retention of low-confidence correct responses*. DOI 10.1037/0278-7393.34.4.918. https://pubmed.ncbi.nlm.nih.gov/18605878/
   - Primary abstract inspected via web search retrieval on 2026-10-25. Direct webfetch returned an empty readable body; full text was not inspected.
   - Two experiments: general-knowledge multiple-choice questions, confidence judgments, feedback for half the questions and final cued recall. Feedback improved retention of initial errors and low-confidence correct responses.
   - Supports answer checking/feedback as a distinct component. Does not make an unsupervised check identical to experimental feedback.

## Boundaries

The exact three-line end-of-day protocol, its dose, and its effectiveness are editorial adaptations, not validated interventions. Reflection alone is not retrieval evidence. A tomorrow retest is a usable scheduling suggestion, not an optimal spacing claim. The percentage-change example is invented and explicitly ILLUSTRATIVE, not observed owner experience. Arithmetic: (100−80)/80 × 100 = 25%; (60−50)/50 × 100 = 20%. No general learning-effect size is claimed.

## Rights

- Copy: original paraphrase and instructional example, not article text reproduction.
- Illustrations: original geometric diagrams rendered with Pillow; no downloaded photos, icons, avatars or private data.
- Research: bibliographic attribution only; no paper figures or screenshots reused.
- Font: external font provided by parent. No font bundled and no proprietary font assumed. Parent must verify open-license terms, redistribution and attribution before publication.
- Candidate needs human review. Renderer has intentionally not been executed in this module; parent supplies Python/Pillow and licensed font paths.

## Rendering

`python squirrel_cards.py content.json --out DIR --font-regular PATH --font-bold PATH`

Outputs five PNG files and layout-qc.json. Text is wrapped and reduced only to the per-block minimum; otherwise rendering fails. All actual text-ink rectangles are logged, checked for containment within their registered panel, and checked for overlaps against all other text lines. Background panels and connecting strokes intentionally sit behind text and are not treated as text collisions. Exit status is nonzero on failed layout; layout-qc.json records failure.
