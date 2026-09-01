# -*- coding: utf-8 -*-
"""修复重命名后悬空关系: KSP-04方案对抗→创意概念 / UserGate:方案拍板→创意概念拍板"""
import glob
import json

MAP = {
    "KspStep:KSP-04方案对抗": "KspStep:KSP-04创意概念",
    "UserGate:方案拍板": "UserGate:创意概念拍板",
}
fixed = 0
for f in glob.glob(r"F:/AI/kesheng/packs/*/kg.json"):
    try:
        g = json.load(open(f, encoding="utf-8-sig"))
    except Exception:
        continue
    changed = False
    for r in g.get("relations", []):
        for k in ("source", "target"):
            if r.get(k) in MAP:
                r[k] = MAP[r[k]]
                changed = True
    if changed:
        json.dump(g, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        fixed += 1
        print("fixed relations in", f)
print("done, files fixed:", fixed)
