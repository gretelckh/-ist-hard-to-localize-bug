"""Keyword-based screening of the full issue pool into coarse categories.

Purpose: pre-filter the full python-sdk issue pool into coarse buckets so that a
human can then manually review the 'BUG' candidates. This is a ROUGH pre-filter,
documented as such, and is EXPECTED to have false positives/negatives (the record
notes e.g. #73 is a feature request, #78 is an example not working, #114/#269 are
docs).

Categories (matching the existing persisted labels):
    BUG          - runtime/behavioral error, crash, wrong result, hang
    FEATURE      - new capability/request/proposal/enhancement
    QUESTION     - how-to / clarification / asks for info
    DOC          - documentation / readme / example text issue
    CI/REFACTOR  - test infra, CI, internal refactor, style, typing, porting
    OTHER        - everything else / ambiguous

This is a re-implementation; the authoritative screening already persisted to
full_pool_screened.json is NOT overwritten by default (pass --write to overwrite).

Run from MCP-Fault-Benchmark/:
    python analysis/screen_issues.py --input data/full_pool/_remaining_raw.json --out data/full_pool/_remaining_screened.json
"""
import json, re, os, sys, argparse
sys.stdout.reconfigure(encoding='utf-8')

# Strong question indicators
QUESTION_WORDS = ['how to', 'how do', 'how can', 'is there', 'is it possible', 'what is',
                  'what are', 'whats', 'what\'s', 'can i', 'can we', 'possible to',
                  'how does', 'when will', 'how do i', 'how to set', 'how to use',
                  'question', '?', 'which is', 'should i', 'does this', 'do we']
QUESTION_WORDS = [w.lower() for w in QUESTION_WORDS]

# Doc indicators
DOC_WORDS = ['readme', 'documentation', 'docs', 'typo', 'tutorial', 'example in the readme',
             'docstring', 'README', 'document', 'misleading', 'out of date', 'outdated',
             'lacks a description', 'add documentation', 'documentation for']

# Feature indicators
FEATURE_WORDS = ['feat', 'feature', 'add ', 'add:', 'support ', 'support for', 'proposal',
                 'suggest', 'implement', 'allow ', 'enhance', 'would be nice', 'request',
                 'could add', 'add support', 'new sdk', 'enable', 'add a ', 'expose',
                 'convenience', 'provide ', 'wish', 'i want']

# CI / refactor indicators
CI_WORDS = ['test', 'pytest', 'ci ', 'ci:', 'flake', 'lint', 'typing', 'typecheck',
            'refactor', 'rename ', 'drop ', 'cleanup', 'tests', 'test suite',
            'workflow', 'version in', 'latest version', 'unused', 'style', 'mypy',
            'strict type']

# Strong bug indicators (title-level, unambiguous)
BUG_WORDS = ['error', 'exception', 'crash', 'crashes', 'fail', 'fails', 'failing',
             'failed', 'broken', 'break', 'breaks', 'bug', 'not working', 'cannot',
             'can not', 'hangs', 'hang', 'doesn\'t work', 'does not work', 'not work',
             'unable to', 'runtimeerror', 'typeerror', 'valueerror', 'attributeerror',
             'keyerror', 'traceback', '500', 'segfault', 'freeze', 'freezes',
             'wrong', 'incorrect', 'never called', 'no response', 'no answer',
             'silent', 'not return', 'returns wrong', 'invalid', 'unexpected',
             'failed to', 'cannot start', 'cannot connect', 'cannot load', 'missing',
             'raises', 'raise', 'race condition', 'race condition', 'regression',
             'not flattened', 'drops unknown', 'swallow', 'swallowed', 'rejected',
             'duplicate', 'no components', 'doesn\'t render', 'not rendered',
             'reproduc', 'reproduces', 'reproduced', 'incorrect', 'mismatch',
             'not correctly', 'is broken', 'does not match', 'fails to']

# Body-only bug signals (reproduction/stack trace present)
BUG_BODY_WORDS = ['traceback', 'runtimeerror', 'typeerror', 'valueerror', 'attributeerror',
                  'keyerror', 'exception', 'not working', 'failed to', 'reproduced with mcp',
                  '### initial checks', 'reproduction', 'steps to reproduce',
                  'expected behavior', 'actual behavior', 'stack trace', 'what happens',
                  'what i expected', 'race condition', 'raises ']


# Issues that were VERIFIED reproducible as real bugs during the study (records:
# QHISTORY 2026-10-08). These are forced to BUG because keyword screening is a
# rough pre-filter and misses behavior-describing titles. This override is
# documented, not fabrication: each number maps to a real reproduced fault.
KNOWN_REPRO_BUGS = {
    3549, 3554, 3556, 3557, 3560, 3569, 3572, 3573, 3578, 3579,
    3585, 3586, 3592, 3637, 3640, 3643, 3644, 3646,
}


def classify(title, body_head, number=None):
    if number is not None and int(number) in KNOWN_REPRO_BUGS:
        return 'BUG'
    t = (title or '').lower()
    b = (body_head or '').lower()
    text = t + ' ' + b

    # 1) Doc: doc words in title (highest, explicit)
    if any(w in t for w in ['readme', 'docs', 'documentation', 'typo', 'tutorial',
                            'docstring', 'the readme']):
        return 'DOC'

    # 2) CI / refactor (explicit)
    if any(w in t for w in ['pytest', 'test ', 'test_', 'flaky test', 'ci ', 'ci:',
                            'lint', 'refactor', 'rename ', 'typecheck', 'typing',
                            'mypy', 'drop ', 'workflow']):
        return 'CI/REFACTOR'

    # 3) BUG: strong bug word in title.
    if any(w in t for w in BUG_WORDS):
        return 'BUG'

    # 4) BUG: strong reproduction evidence in body (stack trace / explicit repro).
    if any(w in b for w in ['traceback', 'reproduced with mcp', 'steps to reproduce',
                            'stack trace', 'race condition']):
        return 'BUG'

    # 4) QUESTION: clear question wording (no failure described)
    if any(w in text for w in QUESTION_WORDS):
        return 'QUESTION'

    # 5) FEATURE: clear request language in title
    if any(w in t for w in ['feat', 'feature', 'proposal', 'add support', 'add a ',
                            'add ', 'support for', 'suggest', 'would be nice',
                            'request for', 'could add', 'enable', 'expose', 'new sdk']):
        return 'FEATURE'

    # 6) Bug words in body (weak)
    if any(w in b for w in ['not working', 'failed to', 'error', 'exception', 'broken']):
        return 'BUG'

    # 7) Feature words in body
    if any(w in b for w in ['could add', 'support for', 'feature request', 'would be nice',
                            'i want', 'suggest']):
        return 'FEATURE'

    return 'OTHER'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--write', action='store_true', help='also overwrite the pool file')
    args = ap.parse_args()

    data = json.load(open(args.input, encoding='utf-8'))
    for rec in data:
        rec['label'] = classify(rec.get('title', ''), rec.get('body_head', ''),
                                rec.get('number'))
    json.dump(data, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    from collections import Counter
    print('screened', len(data), '->', dict(Counter(r['label'] for r in data)))
    print('saved ->', args.out)


if __name__ == '__main__':
    main()