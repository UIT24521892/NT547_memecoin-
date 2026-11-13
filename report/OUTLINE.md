# Report outline (skeleton) — NT547 Meme Coin Manipulation

> Created 2026-11-13 [claude] following `docs/WRITING_GUIDE.md` (skill `research-paper-writing`, step "build a mini-outline before drafting prose").
> **No results yet.** Every claim below is a *planned* claim with `Status: needs evidence`. Prose drafting starts 14/12 (PLAN §8). Rewrite the story once results exist; if a result contradicts a planned claim, change the claim, not the analysis.
> Format: English, IEEE two-column (PLAN §10 default).

## Story (one paragraph, to be rewritten with real numbers)

Mongardini & Mei (USENIX Sec 2026) showed that wash trading and liquidity-pool price inflation (LPI) often appear before pump-and-dump and rug-pull events in 2024–2025 meme coins, but they did not measure how early these signals appear or how often price-based screening flags legitimate tokens. We re-implement their wash-trading and LPI indicators on a fresh 2026 sample of ~300 tokens across Base, Ethereum and Solana, collected only from public data and including dead pools. We then ask whether behaviour observable before a cutoff predicts a severe collapse within 30 days under a strict temporal split, and how badly the naive "price > +100%" rule performs.

## Planned sections (mini-outline)

1. **Introduction** — problem (manipulation in meme coins), gap (no lead time, no false-positive analysis), what we do, contributions.
2. **Background** — AMM x·y=k (worked example: 0.01 ETH / 100 MEME, buy 50 → +300%), wash trading, LPI, rug pull / collapse.
3. **Data collection** — sources per chain (PLAN §6), candidate discovery from pool-creation logs (survivorship), sampling funnel A/B/C, cutoff rule, data card.
4. **Indicators** — IND-1 wash trading (screen → zero-risk / circular / coordinated), IND-2 LPI; what follows the paper vs. what we changed and why; thresholds from `configs/thresholds.yaml`.
5. **Risk score** — naive baseline, rule-based score with reasons, logistic regression (+ gradient boosting if gate 29/11 passes); temporal split T0–T3 with 30-day gaps.
6. **Evaluation** — RQ1 replication vs. paper; RQ2 prediction (PR-AUC, precision@k, calibration); RQ3 feature-group ablation; RQ4 false positives incl. group C; threshold sensitivity; manual validation precision and Cohen's kappa.
7. **Limitations** — see `docs/WRITING_GUIDE.md` §5.
8. **Ethics** — public read-only data, no deanonymisation, outputs are risk signals.
9. **Conclusion**.

## Claim–evidence map

| # | Planned claim | Evidence needed (script → output; source, collection date, chain, period) | Status |
|---|---|---|---|
| C1 | The sample includes pools that later died (reduced survivorship bias) | Discovery from factory/migration logs, counts per chain (`data/interim/task2/`) | needs evidence |
| C2 | Wash-trading / LPI prevalence among surging tokens in 2026 is [similar to / different from] the paper | IND-1/IND-2 run on group A, compared with paper tables (cite page) | needs evidence |
| C3 | Pre-cutoff features [do / do not] predict severe collapse within 30 days | Test-set PR-AUC, precision@k vs. baseline, run once | needs evidence |
| C4 | Signals appear on average N days before the collapse (lead time) | Per-token gap between first flagged day and label event | needs evidence |
| C5 | Feature group G contributes most | RQ3 ablation on validation, confirmed on test | needs evidence |
| C6 | The "price > +100%" rule produces many false positives | RQ4 confusion matrix on A+B and on group C separately | needs evidence |
| C7 | Indicator precision after manual review is P | `validation/sample.csv`, kappa | needs evidence |

Known risk to the story (2026-11-12 measurement, Solana only, n=69 train+val): positive rate 7.2%, near the lower bound of the 5–50% gate, and many tokens had already collapsed before cutoff. If this holds, C3/C4 may need to be weakened or framed as exploratory (PLAN §7 gate 29/11).

## Figures and tables (planned)

- Fig. 1: data funnel per chain (candidates → has cutoff → A/B/C → swaps).
- Fig. 2: one manually verified example of wash-trading signals (explorer links).
- Table: thresholds (paper vs. ours, with page numbers).
- Table: RQ2 metrics, naive baseline vs. rule score vs. models, per chain where counts allow.
- Table: RQ3 ablation by feature group.
