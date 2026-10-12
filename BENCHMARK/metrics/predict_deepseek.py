#!/usr/bin/env python3
"""DEPRECATED: kept for reference / reproducibility of the earlier hand-rule baseline.

This file formerly produced data/db_answers.json using a deterministic if/else RULE classifier
(not an LLM). It is superseded by metrics/predict_llm.py, which runs a GENUINE LLM
(DeepSeek-V4-Flash-FP8 via the CityU proxy) and writes data/llm_answers.json. metrics/diagnose.py
now prefers llm_answers.json. The rules below are retained only as a deterministic cross-check.

Rule diagnostics (surface text only):
  - "Unknown tool: <name>"                      -> Host
  - "Error executing tool <x>" (args/validation) -> Server
  - "返回长度: <n>" (oversized response)          -> Server
  - a genuine CancelledError / 'async context manager' -> Transport
  - silent success (is_error=False) or no signal -> Server

Usage:
    python metrics/predict_deepseek.py    # writes data/db_answers.json (legacy rules)
"""
import os, sys, json, glob
sys.stdout.reconfigure(encoding='utf-8')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, 'data', 'raw')
ds = json.load(open(os.path.join(REPO, 'data', 'dataset_runs.json'), encoding='utf-8'))

# Tokens that mark a genuine Transport-layer lifecycle problem in the REAL exception text
# (note: no Chinese 'Transport传输层' layer-name leak here).
TRANSPORT_SIGNALS = ['async context manager', 'CancelledError', 'cancelled by',
                     'before', 'after the session', 'session was closed', 'closed connection']

# case-script layer-naming header to strip (the leak)
LEAKY = ['故障类型', 'Transport传输层', 'Host调度层', 'Client报文层', 'Server工具层']


def surface_text(txt):
    """Rebuild an honest surface-text input from the raw captured output.

    Prefer the SDK `meta=...` return line (the real error/success object). If absent, use the
    real Python exception type and message, and STRIP the case-script's layer-naming header.
    """
    for line in txt.splitlines():
        ls = line.strip()
        if 'meta=' in ls and 'io.modelcontextprotocol' in ls:
            return ls
    # no SDK return line -> gather real exception info, dropping the leaky header
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    useful = []
    for l in lines:
        if any(k in l for k in LEAKY):
            continue
        if set(l) <= set('=-'):
            continue
        useful.append(l)
    return ' | '.join(useful) if useful else lines[0] if lines else ''


def predict(text):
    if 'Unknown tool' in text:
        return 'Host'
    if any(s in text for s in TRANSPORT_SIGNALS):
        return 'Transport'
    if '返回长度' in text:
        return 'Server'
    if 'Error executing tool' in text:
        return 'Server'
    return 'Server'   # silent success / no clear error signal -> default manifestation layer


records = []
for i, r in enumerate(ds):
    layerkey = {'Host调度层': 'host', 'Client报文层': 'client',
                'Server工具层': 'server', 'Transport传输层': 'transport'}[r['layer']]
    rawfile = f"{r['variant']}_{r['case']}_{layerkey}.txt"
    rawpath = os.path.join(RAW, rawfile)
    txt = open(rawpath, encoding='utf-8', errors='replace').read() if os.path.exists(rawpath) else ''
    stext = surface_text(txt)
    pred = predict(stext)
    records.append({'index': i, 'variant': r['variant'], 'case': r['case'],
                    'truth': r['layer'], 'surface_text': stext, 'pred': pred})
    print(f"[{i}] {r['case']:<40s} truth={r['layer']:<12s} pred={pred:<8s} | {stext[:90]}")

out = os.path.join(REPO, 'data', 'db_answers.json')
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(records, fh, ensure_ascii=False, indent=1)

def l(x): return x.replace('Host调度层','Host').replace('Client报文层','Client').replace('Server工具层','Server').replace('Transport传输层','Transport')
acc = sum(1 for rec in records if rec['pred'] == l(rec['truth'])) / len(records) * 100
print(f'\nWrote {len(records)} diagnostic answers -> {out}')
print(f'HONEST surface-text (no layer leak) overall accuracy: {acc:.1f}%')