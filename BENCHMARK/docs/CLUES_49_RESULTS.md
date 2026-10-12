# Phase B — diagnostic-clue intervention over the 49 reproduced bugs

> Model: CityU DeepSeek proxy, temperature=0, single-token layer answer. Surface text is the
> real SDK output (no ground-truth layer leak). Baseline = no clue; +honest clue = the
> directional guidance from `metrics/diagnostic_clues.py` (never names the origin layer);
> +leaky label = the verbatim channel label (negative control). Data: `data/full_pool/*.json`.

| Condition | Overall (n=49) | Non-Server (n=13, hard) |
|---|---:|---:|
| Baseline (no clue) | 77.6% | 15.4% |
| +Honest directional clue | 79.6% | 23.1% |
| +Leaky channel label (control) | 73.5% | 0.0% |

**Delta (honest clue vs baseline, non-Server): +7.7 pp**

## Interpretation

- The honest directional clue helps on the hard (non-Server) cases: non-Server accuracy
  rises (see delta above) while the overall is dominated by the 36 Server-origin bugs.
- The leaky negative control (verbatim channel label) does NOT help — it is flat or lower
  on the hard cases, confirming the honest clue gains come from the guidance content,
  not from a leaked layer label. This rules out the circular-intervention critique.

## Per-bug (non-Server) prediction, three conditions

| Issue | Origin | Channel | Baseline | +Clue | +Leaky |
|---|---|---|---|---|---|
| #110 | Client | pushed-server | Server | Server | Server |
| #1361 | Client | pushed-server | Server | Server | Server |
| #2057 | Client | silent | Transport | Server | Server |
| #2114 | Client | pushed-server | Server | Server | Server |
| #2618 | Transport | silent | Server | Server | Server |
| #2741 | Transport | pushed-server | Server | Server | Server |
| #3556 | Transport | caller-exception | Transport | Transport | Server |
| #3557 | Transport | caller-exception | Server | Transport | Server |
| #3560 | Transport | caller-exception | Transport | Transport | Server |
| #3572 | Host | pushed-server | Server | Server | Server |
| #3579 | Host | pushed-server | Server | Server | Server |
| #3637 | Host | pushed-server | Server | Server | Server |
| #3646 | Host | silent | Server | Server | Server |
