# Match score rubric

Score = 100 x (2 x required hits + 1 x preferred hits + 0.5 x other hits) / (2 x required + preferred + 0.5 x other)

- A term hits if it appears (word-boundary, with a small synonym map: JS to JavaScript, K8s to Kubernetes, etc.) in the corpus.
- Corpus for the **profile score** = whole profile (what is possible). Corpus for the **CV score** = the tailored CV (what you actually show).
- Large gap between the two: you left relevant evidence out. Small CV score with high profile score: rewrite bullets.
- Gaps are never filled by invention. Ask the user, or accept the gap.
- This is a proxy for keyword match, not any employer's real score. Optional upgrade: map terms to ESCO (EU) or O*NET (US) skills before matching.
