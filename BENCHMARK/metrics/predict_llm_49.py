#!/usr/bin/env python3
"""LLM fault-localization diagnosis over the 49 genuinely reproduced real bugs.

For each of the 49 bugs we give the LLM only the real SDK output (surface text, no
ground-truth leak) and ask it to predict the layer at which the fault ORIGINATED
(Host / Client / Server / Transport). We then compare with the true origin layer.

Reports:
  - overall accuracy over all 49
  - accuracy over the 13 NON-Server-origin bugs (the genuinely hard cases)
  - per-layer accuracy + confusion matrix
  - Top-K (if --topk)

Data: data/full_pool/diag_dataset_49.json (built by analysis/build_diag_dataset_49.py).
Output: data/full_pool/llm_answers_49.json  (+ _clues / _leaky variants if --clues).

Run from MCP-Fault-Benchmark/:
    python metrics/predict_llm_49.py --pilot 3
    python metrics/predict_llm_49.py            # all 49
    python metrics/predict_llm_49.py --topk     # also collect Top-K scores
"""
import os, sys, json, time, argparse, re as _re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'data', 'full_pool')
DIAG = os.path.join(FP, 'diag_dataset_49.json')
LAYERS = ['Host', 'Client', 'Server', 'Transport']


def load_env():
    p = os.path.join(REPO, '.env')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


def prompt_for(surface, clue=None):
    return (
        "You are diagnosing a failure in a Model Context Protocol (MCP) pipeline, which "
        "connects an LLM (Host) to external tools (Server) via a Client and a Transport "
        "layer. Given only the raw error / SDK output below, predict the layer at which the "
        "fault ORIGINATED (the true root cause), not where it is merely reported.\n"
        "Choose exactly one of: Host, Client, Server, Transport.\n"
        "If the output shows a successful result (no error) yet you suspect a silent logical "
        "fault, still pick the layer you believe the fault originated in; if you genuinely "
        "cannot tell, pick the layer the message points to.\n"
        "Reply with a single token: Host, Client, Server, or Transport.\n\n"
        "RAW SDK OUTPUT:\n" + surface
        + (("\n\nDIAGNOSTIC GUIDANCE (direction only, does NOT state the answer):\n" + clue) if clue else "")
    )


def call_llm(client, model, surface, clue=None):
    resp = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt_for(surface, clue)}],
        temperature=0.0,
        max_tokens=16,
    )
    text = (resp.choices[0].message.content or '').strip()
    m = _re.search(r'\b(Host|Client|Server|Transport)\b', text)
    return m.group(1) if m else 'Unknown'


def rank_prompt(surface, clue=None):
    return (
        "You are diagnosing a failure in a Model Context Protocol (MCP) pipeline, which "
        "connects an LLM (Host) to external tools (Server) via a Client and a Transport "
        "layer. Given only the raw error / SDK output below, score how likely the fault "
        "ORIGINATED in each of the four layers. Scores are integers 0-100; they need not sum "
        "to 100.\n"
        "Return ONLY a JSON object with the four keys Host, Client, Server, Transport, e.g. "
        "{\"Host\":10,\"Client\":0,\"Server\":90,\"Transport\":0}.\n\n"
        "RAW SDK OUTPUT:\n" + surface
        + (("\n\nDIAGNOSTIC GUIDANCE (direction only, does NOT state the answer):\n" + clue) if clue else "")
    )


def rank_llm(client, model, surface, clue=None):
    resp = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': rank_prompt(surface, clue)}],
        temperature=0.0,
        max_tokens=160,
    )
    text = (resp.choices[0].message.content or '').strip()
    m = _re.search(r'\{.*\}', text, _re.S)
    scores = {}
    if m:
        try:
            raw = json.loads(m.group(0))
            scores = {k: max(0, min(100, int(raw[k]))) for k in LAYERS if k in raw}
        except Exception:
            scores = {}
    if scores:
        rank = sorted(LAYERS, key=lambda L: scores.get(L, 0), reverse=True)
        return rank, scores
    pred = call_llm(client, model, surface)
    return [pred] + [L for L in LAYERS if L != pred], {pred: 100}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', type=int, default=0)
    ap.add_argument('--delay', type=float, default=0.0)
    ap.add_argument('--topk', action='store_true')
    ap.add_argument('--clues', action='store_true')
    ap.add_argument('--clues-leaky', action='store_true')
    ap.add_argument('--out', default='llm_answers_49.json')
    args = ap.parse_args()
    load_env()

    base = os.environ['CITYU_BASE_URL']
    key = os.environ['CITYU_API_KEY']
    model = os.environ['CITYU_MODEL']

    from openai import OpenAI
    client = OpenAI(base_url=base, api_key=key, timeout=120)

    ds = json.load(open(DIAG, encoding='utf-8'))
    if args.pilot:
        ds = ds[:args.pilot]

    # optional diagnostic-clue file (Phase B) keyed by issue
    clues = None
    if args.clues or args.clues_leaky:
        cpath = os.path.join(FP, 'diag_clues_49.json')
        if os.path.exists(cpath):
            clues = {c['issue']: c for c in json.load(open(cpath, encoding='utf-8'))}
            if args.clues_leaky:
                for k, c in clues.items():
                    c['hint'] = c.get('hint_leaky', c.get('hint', ''))
        else:
            print('warn: diag_clues_49.json not found; ignoring --clues')

    records = []
    for i, r in enumerate(ds):
        clue = (clues.get(r['issue'], {}).get('hint') if clues else None)
        pred = 'Pending'; rank = []; scores = {}; ok = False
        for attempt in range(3):
            try:
                if args.topk:
                    rank, scores = rank_llm(client, model, r['surface_text'], clue)
                    pred = rank[0] if rank else 'Unknown'
                else:
                    pred = call_llm(client, model, r['surface_text'], clue)
                ok = True
                break
            except Exception as e:
                print(f'  [retry {attempt}] #{r["issue"]}: {type(e).__name__}: {e}', file=sys.stderr)
                time.sleep(2)
        records.append({'issue': r['issue'], 'origin': r['origin'], 'channel': r['channel'],
                        'surface_text': r['surface_text'], 'pred': pred,
                        'rank': rank, 'scores': scores, 'ok': ok})
        print(f"[{i}] #{r['issue']:<5d} truth={r['origin']:<10s} pred={pred:<10s} {'OK' if ok else 'FAIL'}")

    out = os.path.join(FP, args.out)
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(records, fh, ensure_ascii=False, indent=1)

    # metrics
    okr = [x for x in records if x['pred'] in LAYERS]
    acc = sum(1 for x in okr if x['pred'] == x['origin']) / len(okr) * 100
    nonserver = [x for x in okr if x['origin'] != 'Server']
    acc_ns = sum(1 for x in nonserver if x['pred'] == x['origin']) / len(nonserver) * 100 if nonserver else 0
    from collections import Counter
    print(f'\n-> {out}  ({len(records)} records)')
    print(f'Overall accuracy (n={len(okr)}): {acc:.1f}%')
    print(f'Non-Server-origin accuracy (n={len(nonserver)}): {acc_ns:.1f}%  <- the hard cases')
    # confusion
    print('\nConfusion (true row x predicted col):')
    print('          ' + ''.join(f'{p:>8s}' for p in LAYERS))
    conf = Counter()
    for x in okr:
        conf[(x['origin'], x['pred'])] += 1
    for t in LAYERS:
        print(f'    {t:<7s}' + ''.join(f'{conf.get((t,p),0):8d}' for p in LAYERS))


if __name__ == '__main__':
    main()