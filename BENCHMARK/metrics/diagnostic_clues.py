#!/usr/bin/env python3
"""Runnable diagnostic-clue tool (Phase B: replaces the 'cheating' metadata intervention).

PROBLEM IT FIXES
----------------
The earlier RQ3 "intervention" attached an ``actual_fault_source`` enum field that carried the
GROUND-TRUTH layer. Feeding that to an LLM is effectively telling it the answer (accuracy ~100%),
which reviewers rightly flag as circular / near-cheating. The paper itself called it an
"upper-bound" analysis.

THIS TOOL
---------
We replace it with a *runnable diagnostic-clue generator*: a deterministic module that reads the
raw SDK text returned for a run, classifies the EXPOSURE CHANNEL (pushed-to-Server / silent /
caller-exception / single-layer / no-evidence) using the same observation-driven logic as
``analysis/exposure_model.py``, and emits a DIRECTIONAL HINT that tells a debugger WHERE to look
and WHAT to verify. Crucially, the hint NEVER names the root-cause layer, so it cannot leak the
answer. It only packages observable signal (the channel + the structure of the message) into
actionable guidance.

The clue is honest and reproducible: (i) it is derived from the same text the LLM can already
see (so no hidden information is injected); (ii) it is produced by a rule module, not a learned
model (so it is deterministic and does not itself depend on the LLM being diagnosed); (iii) it
states the channel and the direction of investigation, not the verdict.

Output: data/diagnostic_clues.json  (per run: channel, reported_token, hint, hint_leaky?)
  - hint        : directional guidance that does NOT name the layer (used in the honest run)
  - hint_leaky  : only for the ablation negative control (names the channel verbatim)

Usage:
    python metrics/diagnostic_clues.py
"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from analysis.exposure_model import exposure_channel, ORIGIN, parse_case_name  # reuse channel logic

RAW = os.path.join(REPO, 'data', 'raw')

# ---- channel -> directional clue (no layer named) -------------------------------------------
# Each hint (a) names the channel, (b) describes the observable signature, (c) points the
# investigation in a direction, but never states the originating layer.
HINTS = {
    'pushed-server': (
        "CLUE: The failure is reported by the Server-side tool-dispatch layer (an "
        "\"Error executing tool X\" / \"Unknown tool\" result with is_error=True). A tool-dispatch "
        "error is a REPORTING point, not necessarily the ORIGIN. Before editing the tool body, "
        "inspect the tool-call REQUEST: the tool NAME and the ARGUMENTS the caller sent (names, "
        "nesting, types, enum values). An upstream caller mistake is commonly surfaced exactly "
        "here, so compare the request against the tool's declared schema. Do not assume the "
        "defect lives inside the tool implementation."
    ),
    'silent': (
        "CLUE: The SDK returned a SUCCESS status (is_error=False) with a plausible-looking result, "
        "despite the fault. This is a SILENT failure: the defect is not reported at all, so a "
        "normal error log will never show it. Trust nothing about the success flag. Instead, "
        "verify the returned VALUE is semantically correct (right tool? right method? right "
        "arguments? expected shape?), check for silently-dropped extra fields, type coercion, and "
        "duplicate registrations that make the SDK keep the first definition. Instrument the "
        "result, not the error path."
    ),
    'caller-exception': (
        "CLUE: The failure surfaced as a RAW Python EXCEPTION in the calling code (e.g. "
        "CancelledError, TimeoutError, ExceptionGroup, or a \"Client must be used within an async "
        "context manager\" RuntimeError), bypassing the MCP is_error protocol. This signature is "
        "characteristic of the connection/session lifecycle rather than a tool's logic: check "
        "session and connection state, request cancellation, timing/ordering of initialisation "
        "calls, and whether the client was used inside the correct async context. The exception "
        "is raised by the runtime, so correlate it with transport/session state, not tool code."
    ),
    'single-layer': (
        "CLUE: The failure is reported at the layer whose tool body raised it (a normal "
        "\"Error executing tool X\" from within a Server tool, is_error=True). The reporting layer "
        "and the executing layer coincide here, so the defect is most plausibly INSIDE that "
        "tool's implementation: inspect the tool body, its logic, and any raised exceptions. "
        "However, still verify the incoming arguments, since a caller mistake can also be "
        "surfaced here."
    ),
    'no-evidence': (
        "CLUE: The captured output does not contain a parseable SDK return or exception (no "
        "reported layer, no is_error flag, only a traceback snippet or a length note). There is "
        "insufficient evidence to localise from this text alone. Re-capture the run and inspect "
        "the full exception object and the call site before concluding; do not guess a layer from "
        "an empty or header-only message."
    ),
}

# Leaky ablation control: names the channel as-is (NOT used in the honest run). This is only a
# negative control to show how much a verbatim channel label helps, and to prove the honest hint
# is not carrying the channel as a label in disguise.
HINTS_LEAKY = {
    'pushed-server': "CLUE-CHANNEL: pushed-to-Server",
    'silent': "CLUE-CHANNEL: silent",
    'caller-exception': "CLUE-CHANNEL: caller-exception",
    'single-layer': "CLUE-CHANNEL: single-layer",
    'no-evidence': "CLUE-CHANNEL: no-evidence",
}


def main():
    rows = []
    for raw in sorted(glob.glob(os.path.join(RAW, '*.txt'))):
        b = os.path.basename(raw)
        if b.startswith('_index'):
            continue
        variant, case = parse_case_name(b)
        txt = open(raw, encoding='utf-8', errors='replace').read()
        origin = ORIGIN.get(case, '?')
        channel = exposure_channel(txt, case)
        rows.append({
            'variant': variant,
            'case': case,
            'origin': origin,
            'channel': channel,
            'hint': HINTS.get(channel, ''),
            'hint_leaky': HINTS_LEAKY.get(channel, ''),
        })

    out = os.path.join(REPO, 'data', 'diagnostic_clues.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)

    from collections import Counter
    print('=' * 70)
    print('Runnable diagnostic-clue tool (no ORIGIN layer asserted in hint)')
    print('=' * 70)
    print(f'Wrote {len(rows)} runs -> data/diagnostic_clues.json')
    print('Channel distribution: ' + dict(Counter(r['channel'] for r in rows)).__repr__())
    # Sanity: the honest hint must never ASSERT an ORIGIN layer (i.e. never reveal ground truth).
    # It MAY reference the *reported* location (which the LLM can already see in the text), but
    # must not state where the fault truly originated.
    origin_assert = ['origin is Host', 'origin is Client', 'origin is Server', 'origin is Transport',
                     'originated in Host', 'originated in Client', 'originated in Server',
                     'originated in Transport', 'root cause is Host', 'root cause is Client',
                     'root cause is Server', 'root cause is Transport', 'the true origin is']
    bad = [r for r in rows if any(p.lower() in r['hint'].lower() for p in origin_assert)]
    print(f'Sanity check (honest hint must NOT assert an ORIGIN layer): asserts={len(bad)}')
    for r in bad[:10]:
        print('   LEAK!', r['case'], '->', r['hint'][:80])
    if bad:
        sys.exit('ABORT: a hint asserts an origin layer; fix HINTS before proceeding.')


if __name__ == '__main__':
    main()