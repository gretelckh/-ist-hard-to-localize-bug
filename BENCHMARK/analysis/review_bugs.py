"""Manual review verdicts for the 439 keyword-BUG candidates.

IMPORTANT (per user): keep EVERY real bug, including the "feature-missing /
spec-non-compliance" type defects. Those are genuine defects (a capability the
SDK should have but lacks, or behavior that violates the MCP spec) and may be
analysed for other insights. Only exclude items that are genuinely NOT a bug
(usage question, pure feature request, environment/dependency issue, other-SDK,
CI/packaging, duplicate, or unverifiable).

Verdict categories:
    BUG              - real defect (runtime fault, silent failure, misattribution,
                       OR feature-missing / spec-non-compliance). Kept.
    NOT_BUG          - genuinely not a bug (usage question, pure feature request,
                       env/dependency, other SDK, CI/packaging, duplicate, unverifiable).
    Excluded from the bug dataset.

The 18 KNOWN_REPRO bugs are always BUG (verified reproducible in the study).
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'full_pool_screened.json'))
OUT = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'bug_review_verdicts.json'))

# NOT_BUG items. key = issue number -> (reason, dup_of).
# These are genuinely NOT a defect (usage question / pure feature / env / other SDK /
# CI / packaging / duplicate / unverifiable).
NOT_BUG = {
    # --- Usage question / how-to / discussion (not a defect) ---
    173: ('usage question (set client session timeout)', None),
    189: ('usage question (run uv without full path)', None),
    344: ('usage question (duplicate request IDs)', None),
    493: ('usage question (available_tools)', None),
    670: ('usage/feature request (check JSON-RPC compliance)', None),
    710: ('usage question (trigger resources_changed)', None),
    875: ('usage question (broadcast list_changed)', None),
    965: ('usage question (avoid endpoint origin mismatch)', None),
    1064: ('usage question (env vars in stdio)', None),
    1167: ('usage question (session id)', None),
    1358: ('usage question (handle exception in ClientSession)', None),
    1393: ('usage question (lazy http error handling)', None),
    1401: ('usage question (client error handling design)', None),
    1428: ('usage question (elicitation timeout)', None),
    1612: ('usage question (middleware not work)', None),
    1628: ('usage question (SSL verification)', None),
    1798: ('usage question/guide (DNS rebinding)', None),
    1814: ('usage question (what is the problem)', None),
    2288: ('usage question (unicode validation)', None),
    2517: ('usage question (why connect fails)', None),
    3646: ('discussion/feature (opt-in rejection of unknown args)', None),

    # --- Pure feature request (not a defect) ---
    73: ('feature request (better logging)', None),
    643: ('feature request (run() args)', None),
    1690: ('feature/refactor (shared transport abstraction)', None),
    1788: ('feature/design (extensible pattern)', None),

    # --- Not the Python SDK (TS/Node) ---
    532: ('other SDK (TypeScript/Node), not python-sdk', None),
    1096: ('other SDK (TypeScript/Node), not python-sdk', None),

    # --- Environment / dependency / packaging (not SDK code bug) ---
    454: ('env/packaging (uv-dynamic-versioning)', None),
    570: ('env (pydantic_core build in alpine container)', None),
    571: ('env (mysql connector dep)', None),
    579: ('packaging (pip install script placement)', None),
    605: ('env (missing sqlalchemy dep)', None),
    660: ('env/packaging (hatchling/uv build)', None),
    803: ('env (uv dependency resolution)', None),

    # --- CI / test / refactor ---
    462: ('CI/test (tests fail with Pydantic 2.11)', None),
    2385: ('CI/packaging (packit upstream pull)', None),
    2563: ('CI/packaging (packit upstream pull)', None),
    2575: ('refactor (raise-site chaining)', None),
    3136: ('perf/refactor (smart union scores all branches)', None),

    # --- Duplicates ---
    547: ('duplicate', 552),
    855: ('duplicate', 854),
    3596: ('duplicate', 3551),

    # --- Unverifiable (reporter says it actually works) ---
    129: ('unverifiable (reporter says it works)', None),
}

# The 18 verified-reproducible bugs are always BUG.
KNOWN_REPRO = {
    3549, 3554, 3556, 3557, 3560, 3569, 3572, 3573, 3578, 3579,
    3585, 3586, 3592, 3637, 3640, 3643, 3644, 3646,
}


def main():
    pool = json.load(open(POOL, encoding='utf-8'))
    bugs = [x for x in pool if x['label'] == 'BUG']
    bugs.sort(key=lambda x: x['number'])

    verdicts = {}
    for x in bugs:
        n = x['number']
        if n in KNOWN_REPRO:
            verdicts[n] = {'verdict': 'BUG', 'bug_type': 'verified-repro', 'reason': 'verified reproducible in study', 'dup_of': None}
        elif n in NOT_BUG:
            reason, dup = NOT_BUG[n]
            verdicts[n] = {'verdict': 'NOT_BUG', 'bug_type': None, 'reason': reason, 'dup_of': dup}
        else:
            # Everything not explicitly flagged is a real defect (runtime fault,
            # silent failure, misattribution, or feature-missing/spec-non-compliance).
            verdicts[n] = {'verdict': 'BUG', 'bug_type': 'defect', 'reason': 'real defect (runtime fault / feature-missing / spec-non-compliance)', 'dup_of': None}

    data = {'total_initial': len(bugs), 'verdicts': verdicts}
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    from collections import Counter
    print('reviewed', len(bugs))
    print('verdict counts:', dict(Counter(v['verdict'] for v in verdicts.values())))
    print('BUG =', sum(1 for v in verdicts.values() if v['verdict'] == 'BUG'))
    print('NOT_BUG =', sum(1 for v in verdicts.values() if v['verdict'] == 'NOT_BUG'))
    print('saved ->', OUT)


if __name__ == '__main__':
    main()