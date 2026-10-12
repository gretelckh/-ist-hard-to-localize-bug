# MCP-Fault-Benchmark

**A reproducible fault-injection benchmark for studying fault localization (root-cause
diagnosis) in Model Context Protocol (MCP) pipelines.**

This repository accompanies the manuscript:

> *Why Is It So Hard to Localize Bugs in Model Context Protocol (MCP) Pipelines?
> An Empirical Study with a Reproducible Fault-Injection Benchmark*

---

## What is this?

MCP is a middle-layer protocol that connects large language models (LLMs) to external tools
through four components: **Host**, **Client**, **Server**, and **Transport**. When a fault
occurs, the layer at which the error is *reported* often differs from the layer at which it
*originated*. Worse, some erroneous inputs are silently accepted and return a successful
status without any error flag. Both behaviours make MCP fault localization extremely hard.

This benchmark provides:
- A **four-layer runtime fault taxonomy** (Host scheduling / Client message / Server tool /
  Transport).
- A set of **root-cause fault-injection cases**, each with multiple input variants.
- **Reproducible runners** that execute the cases against the official MCP Python SDK v2 and
  capture the raw SDK return objects.
- **Analysis scripts** that quantify `manifestation-root-cause mismatch` and `silent failure`,
  plus a **diagnosis baseline / intervention** showing how structured observability metadata
  improves root-cause localization.

The benchmark is built on the official **MCP Python SDK v2** (`mcp.server.mcpserver.MCPServer`,
`mcp.client.client.Client`) using **in-memory transport**, so it runs cross-platform with no
stdio I/O.

---

## Repository layout

```
MCP-Fault-Benchmark/
├── README.md                 # this file
├── requirements.txt          # python dependencies
├── faultcases/
│   ├── original/             # the original 20 root-cause cases (4 variants a/b/c/d = 80 runs)
│   │   ├── host/             # Host scheduling-layer faults
│   │   ├── client/           # Client message-layer faults
│   │   ├── server/           # Server tool-layer faults
│   │   └── transport/        # Transport-layer faults
│   └── advanced/             # "real hard" production-style bugs (concurrency / no-timeout / state leak / dup registration)
├── runner/
│   ├── run_all.py            # reproduce all 80 original runs
│   └── run_advanced.py       # run the advanced hard-bug cases
├── data/
│   ├── raw/                  # captured SDK outputs (one file per variant run)
│   ├── dataset_runs.json     # structured dataset (20 cases × 4 variants = 80 runs)
│   ├── advanced_runs.json    # advanced hard-bug runs (6)
│   └── summary.json          # headline metrics (mismatch, silent rates)
├── analysis/
│   ├── parse_runs.py         # parse raw outputs into structured dataset
│   ├── analyze.py            # cross-tab layer×scope, silent + mismatch metrics
│   ├── analyze_advanced.py   # metrics for the advanced hard-bug subset
│   └── make_figs.py          # generate paper figures
├── metrics/
│   ├── predict_deepseek.py   # surface-text diagnoser (strips leaked layer header)
│   └── diagnose.py           # diagnosis baseline + intervention + Top-K/confusion/PR
├── figs/                     # generated paper figures
└── docs/
    └── taxonomy.md           # the four-layer taxonomy and how cases map to it
```

---

## Requirements

- Python 3.11+
- `mcp>=2.0` (the official MCP Python SDK v2; install via `pip install mcp`)
- `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `openpyxl`
- `openai` (for the LLM diagnosis baseline)

```bash
pip install mcp pandas numpy matplotlib scikit-learn openpyxl openai
```

> For the LLM diagnosis baseline you also need an OpenAI-compatible endpoint. Copy `.env.example`
> to `.env` and set `CITYU_BASE_URL`, `CITYU_API_KEY`, `CITYU_MODEL`. The `.env` file is
> gitignored and never committed.

> Note: the original case sources were developed against `mcp.server.mcpserver.MCPServer` and
> `mcp.client.client.Client`, which are the MCP SDK **v2** interfaces. If using older MCP
> (v1 with `FastMCP`), the imports will differ; pin `mcp>=2`.

---

## How to reproduce

1. Install dependencies.
2. Reproduce the original 80 runs:
   ```bash
   python runner/run_all.py
   ```
3. Run the advanced (real-hard) bug cases:
   ```bash
   python runner/run_advanced.py
   ```
4. Rebuild the structured dataset and metrics:
   ```bash
   python analysis/parse_runs.py
   python analysis/exposure_model.py      # three-channel exposure model -> data/summary.json
   python metrics/diagnose.py
   ```
5. Run the genuine LLM diagnosis (requires `.env`):
   ```bash
   python metrics/predict_llm.py          # -> data/llm_answers.json (all 80 runs)
   python metrics/diagnose.py             # now uses the LLM answers as the baseline
   ```
6. Regenerate the paper figures:
   ```bash
   python analysis/make_figs.py
   ```

---

## Main paper figure: origin-layer -> exposure-channel alluvial (Fig. main)

- **Figure file**: `figs/fig_main_alluvial_with_ids.pdf` (vector, for the paper) and
  `figs/fig_main_alluvial_with_ids.png` (raster, dpi=300).
- **Script**: `analysis/make_main_alluvial_with_ids.py`
- **Data source**: `data/full_pool/active_dataset_analysis.json` -> `tier_b.per_bug`
  (each of the 49 reproduced bugs carries `origin` + `channel`).
- **Design**:
  - Left: 4 origin-layer aggregated nodes (Host / Client / Server / Transport), each
    showing its label + total count.
  - Beside each layer node: the issue ids of that layer printed **vertically**.
  - One **thin semi-transparent ribbon per bug** (not aggregated), coloured by the
    bug's origin layer.
  - Connectors are **smooth S-curves (sigmoid)**; palette is a muted / low-saturation
    academic scheme (`Host #8c6d31`, `Client #4c72b0`, `Server #c44e52`,
    `Transport #55a868`); ribbon alpha = `0.30`, ribbon width = `0.40`.
  - Right: exposure-channel nodes (Pushed-to-Server / Silent / Caller-exception /
    Single-layer (genericised) / Single-layer (correct) / Registration) + counts.
- **Regenerate**:
  ```bash
  python analysis/make_main_alluvial_with_ids.py
  ```

---

## Key metrics

- **Three-channel exposure model**: how non-Server faults actually surface. Of the 48
  non-Server runs, 23 are *pushed to the Server* (reported at the wrong layer), 13 are
  *silently swallowed* (no error flag), and 11 surface as *caller exceptions* (raw Python
  errors in the calling code).
- **Silent failure**: the SDK returns a successful status (`is_error=False`) despite an
  underlying logical error. In our data, 18/80 runs (22.5%) across 6 root-cause cases,
  distinguishing *structural* (4/4 variants) from *input-dependent* silent failure. All six
  real production-style hidden faults are silent (6/6 = 100%).
- **LLM diagnosis baseline**: a genuine LLM (DeepSeek-V4 via an OpenAI-compatible proxy)
  reading only the SDK's reported error text achieves **46.2%** root-cause localisation
  accuracy, blaming the Server for 43 of the 48 non-Server faults (0% on Host- and
  Client-origin faults). Attaching structured `actual_fault_source` metadata raises accuracy
  to ~100% (ideal) / 93.8% (realistic).

---

## Citation

If you use this benchmark, please cite the manuscript (see [docs](docs/)).

## License

[Add license here, e.g. MIT]