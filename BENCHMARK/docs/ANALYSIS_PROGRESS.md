# Analysis progress & hand-off (read this on resume)

> Authoritative analysis notes for the MCP-Fault-Benchmark paper. Read this first after a
> restart; do NOT re-run completed analyses.
>
> **For the 49-bug experiment code map, run order and per-script data source, see
> `docs/EXPERIMENTS_49.md` (the detailed hand-off).**

## Dataset (authoritative, self-consistent)

Funnel: **1,343 pure issues -> 439 keyword-BUG -> 398 confirmed -> 56 fixed-in-2.2.0
(removed) -> 342 active -> 49 reproduced / 293 not reproduced**.

- Numbers + prose: `docs/FUNNEL_TABLE.md`; structured: `data/full_pool/funnel_table.json`;
  regenerator: `analysis/make_funnel_table.py`.
- Not-reproducible (293) breakdown: env/transport-config 106, auth 48, not-exercised 88,
  observation/scenario 41, spec-gap 6, external-tool 4 (= 293).
- Active origin distribution: Server 91 / Client 118 / Transport 85 / Host 48 (from
  `active_dataset_analysis.json`).

## 49 reproduced bugs — hard-to-localise analysis (DONE)

- Outputs: `docs/HARD_TO_LOCALIZE_49.md`, `data/full_pool/hard_to_localize_49.json`,
  `analysis/analyze_hard_to_localize.py`.
- Each bug has origin (start layer), channel (exposure layer), and an induced
  hard-to-localise reason read from its ACTUAL reported error (not a preset category).
- Distribution (n=49): genericised 28 / silent-ok 11 / insufficient 4 / registration 3 /
  caller-exception 3.
- Reason semantics:
  - genericised: a generic message replaces the real root cause (`Error executing tool X`,
    `Internal server error`, `Invalid structured content`).
  - silent-ok: success / no-error result (`is_error=False`, HTTP 200/202, plausible value)
    despite a logical error.
  - insufficient: reported at the correct layer but only a vague `Unknown X`.
  - registration: server fails to build / register a tool at startup.
  - caller-exception: a bare exception raised in the calling code, outside the server context.

## 293 not-reproduced bugs — next step (IN PROGRESS)

- These have NO runtime error (could not be reproduced), so exposure channel / hard-to-localise
  reason cannot be induced from evidence. Classify only what is determinable from the issue
  BODY (bug nature / category), leave uncertain fields blank.
- Origin (start layer) is already known: Server 55 / Client 114 / Transport 80 / Host 44 (= 293).
  292 of 293 have a full body (via `data/full_pool/origin_labels.json`).
- Build the 293 list: `confirmed_bugs.json` (398) minus `fixed_removed.json` (56) = 342 active,
  minus the 49 reproduced issues.
- CAUTION: do NOT use the Taraghi taxonomy in this classification (see below).

## Diagnosis LLM experiment over the 49 real bugs (DONE — baseline)

- Script: `metrics/predict_llm_49.py` (reads `data/full_pool/diag_dataset_49.json`, built by
  `analysis/build_diag_dataset_49.py` from the real SDK output in `data/real_raw/`).
- Output: `data/full_pool/llm_answers_49.json` (49 records: issue, origin, channel,
  surface_text, pred).
- Model: CityU DeepSeek proxy (from `.env`), temperature=0, single-token layer answer.
- RESULT (baseline, surface text only, NO metadata):
  - **Overall accuracy: 77.6%** (38/49).
  - **Non-Server-origin accuracy: 15.4%** (2/13) — the genuinely hard cases.
  - Per-layer (correct/total): Server 36/36 (100%), Transport 2/5 (40%),
    Host 0/4 (0%), Client 0/4 (0%).
  - Confusion (true x pred): Host -> Server (4), Client -> Server (3) + Transport (1),
    Transport -> Server (3) + correct (2), Server -> correct (36).
- KEY INSIGHT (supports the paper): every non-Server origin bug is reported at the Server layer
  and the LLM is misled to Server; Host- and Client-origin bugs get **0%** correct.
  The 36 Server-origin bugs inflate the overall figure, so report the 13 non-Server (15.4%)
  as the honest hard-case number.

## Diagnosis Top-K over the 49 real bugs (DONE — 2026-10-11)

- Run: `python metrics/predict_llm_49.py --topk` (CityU DeepSeek proxy, temp=0, 4-layer score
  ranking per bug). Writes rank/scores into `data/full_pool/llm_answers_49.json`.
  (Baseline single-token backup kept at `data/full_pool/llm_answers_49_baseline_backup.json`.)
- Top-K computed by `analysis/compute_topk_49.py` -> `docs/TopK_49_RESULTS.md` +
  `data/full_pool/topk_49.json`. Note: the topk pass re-calls the LLM so pred/overall differs
  slightly from the baseline single-token pass (79.6% vs 77.6%); the top-k RANK is the intended
  measure.
- Top-K hit rate (rank lists):
  - **All 49**: Top-1 79.6% / Top-2 87.8% / Top-3 95.9%.
  - **Non-Server (13 hard)**: Top-1 23.1% (3/13) / Top-2 53.8% (7/13) / Top-3 84.6% (11/13).
  - Server-origin (36, ref): Top-1/2/3 = 100%.
- INSIGHT: even allowing the LLM top-3 guesses, 2 of the 13 non-Server origins are still missed
  (#2057 silent, #2618 silent — both reported at a misleading layer with no error); the caller-
  exception (Transport) bugs are the only non-Server class reliably caught (3/3 Top-1). This
  reinforces three-channel (hardest = silent + pushed-server).

## Diagnosis diagnostic-clue intervention (Phase B) over the 49 real bugs (DONE — 2026-10-11)

- Migrated the clue tool to the 49 bugs: `analysis/make_diag_clues_49.py` -> `data/full_pool/diag_clues_49.json`
  (per-bug channel + directional hint from `metrics/diagnostic_clues.py`, NEVER names the origin layer).
  Channels mapped: pushed-server/silent/caller-exception/single-layer-(masked|correct)/registration.
  Sanity check: no hint asserts an origin layer (asserts=0).
- Ran `metrics/predict_llm_49.py --clues` -> `data/full_pool/llm_answers_49_clues.json` and
  `--clues-leaky` -> `llm_answers_49_leaky.json` (CityU DeepSeek, temp=0).
- Compared by `analysis/compare_clues_49.py` -> `docs/CLUES_49_RESULTS.md` + `data/full_pool/clues_49_summary.json`:
  | Condition | Overall (49) | Non-Server (13) |
  |---|---|---|
  | Baseline (no clue) | 77.6% | 15.4% |
  | +Honest directional clue | 79.6% | **23.1%** |
  | +Leaky channel label (control) | 73.5% | **0.0%** |
  - **Delta (honest vs baseline, non-Server): +7.7pp**.
- KEY INSIGHT: the honest clue helps on the hard non-Server cases (+7.7pp), while the leaky
  negative control (verbatim channel label) does NOT help (flat/lower, 0% on non-Server) — proving
  the gain comes from the guidance content, not a leaked layer label. This rules out the
  circular-intervention critique (matches the old synthetic-set direction: 45% -> 52.5%, control 41.2%).
- TODO (next): repair experiment (Phase C) — needs a decision on auto-verifiability of the 49 real
  bugs; then write the 49-bug narrative into the paper.

## Taraghi taxonomy — DO NOT USE in analysis

- Per decision: the Taraghi et al. category is NOT used in our classification. It is only
  mentioned in Related Work to explain WHY we do not adopt it. Do not classify bugs by Taraghi.

## Outstanding items

- Dataset anonymous repo / DOI link (hard blocker; needs author-provided link).
- Re-run the diagnosis LLM experiment on the new 49 bugs.
- Re-run the repair experiment on the new data.
- Integrate the 342 / 49 narrative into the final .tex.
- Package the deliverables into a zip.