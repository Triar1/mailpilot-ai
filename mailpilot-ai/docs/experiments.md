# Experiment: rules vs local LLM

## Objective
Evaluate whether a locally hosted language model improves **classification coverage** over a deterministic rule-based baseline on email metadata.

## Data and methodology
- Two personal Gmail accounts; 500 messages sampled from each.
- Gmail API `gmail.readonly`; fetched **From and Subject metadata**, not message bodies.
- Baseline: rule-based classifier (v0.2).
- Alternative: local Ollama model `qwen2.5:3b` (v0.3).
- Outputs are stored locally. No personal emails or individual classifications are included in this repository.

## Observed results

| Metric | Rule-based v0.2 | Ollama v0.3 |
|---|---:|---:|
| Emails processed | 1,000 | 1,000 |
| Classified `other` | 594 | 94 |
| `other` rate | 59.4% | 9.4% |
| Technical model errors reported | Not recorded | 11 (1.1%) |

**Interpretation:** The unclassified rate fell by 50 percentage points. This is a **coverage** improvement, not a measured accuracy gain. Technical errors may overlap with the `other` category because the implementation routes model failures to manual review.

## Limitations
- The dataset is private and not published; findings are not independently reproducible on the same data.
- No representative human-annotated gold-standard evaluation was completed.
- Classifying every email is not always useful: e.g., a post-trip satisfaction survey may not fit a single category.
- A subject line alone cannot reliably reveal every request, deadline, or conversation context.
- Local inference may be slow and can fail due to timeouts or invalid outputs.

## Product learning
The experiment motivated a pivot from **email taxonomy** to **action-oriented email assistance**: detecting invitations, follow-ups, requested documents, and opportunities to draft replies. That next product direction is not part of this v0.3 release.
