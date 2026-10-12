# Top-K diagnostic hit rates over the 49 reproduced bugs

> Computed from `data/full_pool/llm_answers_49.json` (rank/scores produced by 
> `metrics/predict_llm_49.py --topk`, CityU DeepSeek proxy, temperature=0). 
> `rank` is the 4-layer ranking the LLM returned; Top-k hit = the true origin layer 
> appears in the top-k. Overall = all 49; non-Server = the 13 genuinely hard cases. 
> Baseline (single-token answer, no ranking) overall = 77.6%, non-Server = 15.4%.

| Scope | n | Top-1 | Top-2 | Top-3 |
|---|---:|---:|---:|---:|
| All 49 | 49 | 39 (79.6%) | 43 (87.8%) | 47 (95.9%) |
| Non-Server (hard) | 13 | 3 (23.1%) | 7 (53.8%) | 11 (84.6%) |
| Server-origin (ref) | 36 | 36 (100.0%) | 36 (100.0%) | 36 (100.0%) |

## Interpretation

- The overall figure is inflated by the 36 Server-origin bugs, which are correctly 
  reported at the Server layer and almost always ranked first. The **non-Server 
  sub-set is the honest hard-case number**: even allowing the LLM to list its top-3 
  guesses, the true (non-Server) origin is often not among them, because the SDK reports 
  these faults at the Server layer (or silently / as a caller-side exception) and the 
  surface text carries the misleading layer. This reinforces the three-channel claim.

## Per-bug (non-Server) details

| Issue | Origin | Channel | rank (top->bottom) | Top-1 hit |
|---|---|---|---|---|
| #110 | Client | pushed-server | Server, Host, Client, Transport | N |
| #1361 | Client | pushed-server | Server, Host, Client, Transport | N |
| #2057 | Client | silent | Transport, Host, Client, Server | N |
| #2114 | Client | pushed-server | Server, Host, Client, Transport | N |
| #2618 | Transport | silent | Server, Host, Client, Transport | N |
| #2741 | Transport | pushed-server | Server, Host, Client, Transport | N |
| #3556 | Transport | caller-exception | Transport, Host, Client, Server | Y |
| #3557 | Transport | caller-exception | Transport, Host, Client, Server | Y |
| #3560 | Transport | caller-exception | Transport, Host, Client, Server | Y |
| #3572 | Host | pushed-server | Server, Host, Client, Transport | N |
| #3579 | Host | pushed-server | Server, Host, Client, Transport | N |
| #3637 | Host | pushed-server | Server, Host, Client, Transport | N |
| #3646 | Host | silent | Server, Host, Client, Transport | N |
