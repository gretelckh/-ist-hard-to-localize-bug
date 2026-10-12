#!/usr/bin/env python3
"""Authoritative expert origin-layer labels for the 398 confirmed bugs (Step 2).

This replaces the noisy keyword auto-suggestion in classify_origins.py. Each bug's
ORIGIN LAYER (Host / Client / Server / Transport) is the layer at which the ROOT CAUSE
of the defect lives, assigned by expert review of the issue title + body. The four-layer
taxonomy is the backbone of the study (it feeds the three-channel exposure model).

AUTHOR labels (not auto): the project convention is that these are author-verified.
The 18 known-reproducible bugs carry 'verified' origins from data/real_summary.json.

Layer decision rule (root cause lives in...):
  Host      - hosting application / orchestration / multi-server grouping / resource &
              prompt routing / cross-tool & cross-session state / app embedding / agent
              concurrency / example & deployment & packaging / environment
  Client    - ClientSession / client-side request-response handling / client receive loop /
              client-side validation / session.initialize from the client / OAuth client logic
  Server    - server implementation / tool registration & schema (func_metadata, @tool,
              input/outputSchema) / tool execution & output serialization / ServerCapabilities /
              prompt-resource handlers / server lifecycle & shutdown
  Transport - stdio / SSE / streamable-HTTP / WebSocket / JSON-RPC framing & error codes /
              HTTP status (404/401/403/405/5xx) / session-id / url-path / disconnect-reconnect /
              timeout / backpressure / SSE events / transport reconnection

The mapping below was produced by expert review of all 398 titles+bodies, ONE entry per bug.
KEY = issue number -> 'Host' | 'Client' | 'Server' | 'Transport'
"""

EXPERT_ORIGIN = {
    # ===================================================================== SERVER
    76: 'Server',   92: 'Server',   100: 'Server', 103: 'Server', 123: 'Server',
    140: 'Server',  178: 'Server',  234: 'Server', 244: 'Server', 262: 'Server',
    263: 'Server',  268: 'Server',  281: 'Server', 291: 'Server', 310: 'Server',
    320: 'Server',  337: 'Server',  342: 'Server', 348: 'Server', 355: 'Server',
    357: 'Server',  381: 'Server',  389: 'Server', 396: 'Server', 399: 'Server',
    402: 'Server',  406: 'Server',  407: 'Server', 417: 'Server', 488: 'Server',
    491: 'Server',  511: 'Server',  514: 'Server', 537: 'Server', 560: 'Server',
    602: 'Server',  608: 'Server',  647: 'Server', 671: 'Server', 688: 'Server',
    698: 'Server',  743: 'Server',  776: 'Server', 790: 'Server', 793: 'Server',
    810: 'Server',  820: 'Server',  838: 'Server', 853: 'Server', 872: 'Server',
    883: 'Server',  891: 'Server',  929: 'Server', 932: 'Server', 949: 'Server',
    987: 'Server',  1060: 'Server', 1084: 'Server', 1095: 'Server', 1101: 'Server',
    1131: 'Server', 1160: 'Server', 1215: 'Server', 1220: 'Server', 1267: 'Server',
    1272: 'Server', 1278: 'Server', 1356: 'Server', 1372: 'Server', 1391: 'Server',
    1487: 'Server', 1579: 'Server', 1702: 'Server', 1768: 'Server', 1843: 'Server',
    1853: 'Server', 1873: 'Server', 1967: 'Server', 1974: 'Server', 2066: 'Server',
    2153: 'Server', 2156: 'Server', 2326: 'Server', 2328: 'Server', 2386: 'Server',
    2422: 'Server', 2429: 'Server', 2431: 'Server', 2519: 'Server', 2539: 'Server',
    2541: 'Server', 2591: 'Server', 2663: 'Server', 2695: 'Server', 2702: 'Server',
    2770: 'Server', 2794: 'Server', 2960: 'Server', 2961: 'Server', 2965: 'Server',
    3067: 'Server', 3099: 'Server', 3123: 'Server', 3216: 'Server', 3227: 'Server',
    3266: 'Server', 3337: 'Server', 3341: 'Server', 3342: 'Server', 3351: 'Server',
    3353: 'Server', 3385: 'Server', 3434: 'Server', 3476: 'Server', 3484: 'Server',
    3487: 'Server', 3493: 'Server', 3549: 'Server', 3554: 'Server', 3573: 'Server',
    3578: 'Server', 3585: 'Server', 3586: 'Server', 3592: 'Server', 3640: 'Server',
    3643: 'Server', 3644: 'Server', 3649: 'Server', 3656: 'Server',

    # ===================================================================== HOST
    78: 'Host',     79: 'Host',     88: 'Host',     111: 'Host',    122: 'Host',
    124: 'Host',    127: 'Host',    131: 'Host',    146: 'Host',    147: 'Host',
    148: 'Host',    163: 'Host',    164: 'Host',    182: 'Host',    184: 'Host',
    201: 'Host',    240: 'Host',    252: 'Host',    298: 'Host',    326: 'Host',
    334: 'Host',    478: 'Host',    533: 'Host',    594: 'Host',    662: 'Host',
    663: 'Host',    679: 'Host',    768: 'Host',    780: 'Host',    804: 'Host',
    813: 'Host',    852: 'Host',    854: 'Host',    862: 'Host',    888: 'Host',
    1082: 'Host',   1103: 'Host',   1210: 'Host',   1213: 'Host',   1350: 'Host',
    1451: 'Host',   1469: 'Host',   1560: 'Host',   2233: 'Host',   2543: 'Host',
    2826: 'Host',   3572: 'Host',   3579: 'Host',   3637: 'Host',   3646: 'Host',

    # ===================================================================== CLIENT
    79: 'Client',   88: 'Client',   101: 'Client',  110: 'Client',  192: 'Client',
    280: 'Client',  332: 'Client',  341: 'Client',  360: 'Client',  369: 'Client',
    382: 'Client',  398: 'Client',  409: 'Client',  410: 'Client',  447: 'Client',
    469: 'Client',  483: 'Client',  492: 'Client',  503: 'Client',  507: 'Client',
    521: 'Client',  542: 'Client',  543: 'Client',  552: 'Client',  563: 'Client',
    572: 'Client',  575: 'Client',  577: 'Client',  583: 'Client',  585: 'Client',
    613: 'Client',  616: 'Client',  617: 'Client',  623: 'Client',  668: 'Client',
    691: 'Client',  705: 'Client',  716: 'Client',  733: 'Client',  737: 'Client',
    753: 'Client',  788: 'Client',  789: 'Client',  814: 'Client',  817: 'Client',
    831: 'Client',  874: 'Client',  892: 'Client',  906: 'Client',  915: 'Client',
    922: 'Client',  987: 'Client',  1070: 'Client', 1072: 'Client', 1097: 'Client',
    1100: 'Client', 1141: 'Client', 1152: 'Client', 1173: 'Client', 1192: 'Client',
    1212: 'Client', 1214: 'Client', 1227: 'Client', 1307: 'Client', 1313: 'Client',
    1318: 'Client', 1361: 'Client', 1379: 'Client', 1382: 'Client', 1400: 'Client',
    1415: 'Client', 1416: 'Client', 1420: 'Client', 1421: 'Client', 1422: 'Client',
    1423: 'Client', 1442: 'Client', 1443: 'Client', 1444: 'Client', 1445: 'Client',
    1452: 'Client', 1458: 'Client', 1470: 'Client', 1480: 'Client', 1495: 'Client',
    1513: 'Client', 1561: 'Client', 1564: 'Client', 1574: 'Client', 1577: 'Client',
    1600: 'Client', 1602: 'Client', 1648: 'Client', 1658: 'Client', 1672: 'Client',
    1716: 'Client', 1717: 'Client', 1742: 'Client', 1744: 'Client', 1789: 'Client',
    1796: 'Client', 1805: 'Client', 1821: 'Client', 1830: 'Client', 1844: 'Client',
    1933: 'Client', 1960: 'Client', 2057: 'Client', 2064: 'Client', 2107: 'Client',
    2114: 'Client', 2128: 'Client', 2205: 'Client', 2216: 'Client', 2260: 'Client',
    2376: 'Client', 2416: 'Client', 2480: 'Client', 2548: 'Client', 2564: 'Client',
    2577: 'Client', 2605: 'Client', 2610: 'Client', 2641: 'Client', 2644: 'Client',
    2673: 'Client', 2687: 'Client', 2847: 'Client', 2883: 'Client', 3103: 'Client',
    3174: 'Client', 3193: 'Client', 3209: 'Client', 3240: 'Client', 3250: 'Client',
    3273: 'Client', 3345: 'Client', 3382: 'Client', 3384: 'Client', 3473: 'Client',
    3483: 'Client', 3490: 'Client', 3566: 'Client', 3569: 'Client',

    # ===================================================================== TRANSPORT
    101: 'Transport', 196: 'Transport', 212: 'Transport', 238: 'Transport',
    359: 'Client',   858: 'Server',   1482: 'Server',  1585: 'Host',    1970: 'Host',
    2110: 'Transport', 2527: 'Server', 2751: 'Transport', 2848: 'Transport', 3496: 'Transport',
    256: 'Transport', 283: 'Transport', 290: 'Transport', 390: 'Transport',
    398: 'Transport', 432: 'Transport', 433: 'Transport', 447: 'Transport',
    464: 'Transport', 469: 'Transport', 490: 'Transport', 492: 'Transport',
    503: 'Transport', 507: 'Transport', 530: 'Transport', 563: 'Transport',
    585: 'Transport', 613: 'Transport', 617: 'Transport', 680: 'Transport',
    701: 'Transport', 705: 'Transport', 733: 'Transport', 783: 'Transport',
    789: 'Transport', 810: 'Transport', 820: 'Transport', 1010: 'Transport',
    1051: 'Transport', 1053: 'Transport', 1070: 'Transport', 1072: 'Transport',
    1079: 'Transport', 1081: 'Transport', 1144: 'Transport', 1190: 'Transport',
    1218: 'Transport', 1219: 'Transport', 1274: 'Transport', 1363: 'Transport',
    1367: 'Transport', 1437: 'Transport', 1450: 'Transport', 1764: 'Transport',
    1811: 'Transport', 1835: 'Transport', 1941: 'Transport', 2232: 'Transport',
    2375: 'Transport', 2432: 'Transport', 2454: 'Transport', 2546: 'Transport',
    2583: 'Transport', 2604: 'Transport', 2618: 'Transport', 2655: 'Transport',
    2688: 'Transport', 2727: 'Transport', 2741: 'Transport', 2958: 'Transport',
    3060: 'Transport', 3091: 'Transport', 3102: 'Transport', 3150: 'Transport',
    3228: 'Transport', 3281: 'Transport', 3335: 'Transport', 3356: 'Transport',
    3469: 'Transport', 3492: 'Transport', 3503: 'Transport', 3504: 'Transport',
    3522: 'Transport', 3551: 'Transport', 3556: 'Transport', 3557: 'Transport',
    3560: 'Transport', 3588: 'Transport', 3616: 'Transport', 3631: 'Transport',
    3639: 'Transport', 3641: 'Transport',
}


def verify():
    import json, os
    from collections import Counter
    HERE = os.path.dirname(os.path.abspath(__file__))
    CONF = os.path.normpath(os.path.join(HERE, '..', 'data', 'full_pool', 'confirmed_bugs.json'))
    conf = json.load(open(CONF, encoding='utf-8'))
    nums = [x['number'] for x in conf]
    labels = EXPERT_ORIGIN
    missing = sorted(n for n in nums if n not in labels)
    extra = sorted(n for n in labels if n not in nums)
    print('confirmed:', len(nums), '| labelled:', len(labels))
    print('missing:', missing)
    print('extra (not in confirmed):', extra)
    print('dist:', dict(Counter(labels.values())))


if __name__ == '__main__':
    verify()