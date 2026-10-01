#!/usr/bin/env python3
"""Experiment-only deterministic pairwise scorer for personal-taste backtest 01.
No production imports or writes."""
import math

ANCHORS = {
  "Half-Life": 12.5,
  "Fallout 4": 25,
  "Deus Ex: Human Revolution": 37.5,
  "Stray": 50,
  "Tomb Raider (2013)": 62.5,
  "Batman: Arkham Asylum": 75,
  "Red Dead Redemption II": 87.5
}

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def fit_pairwise(relations, model="bt"):
    grid = [i / 100.0 for i in range(-400, 401)]
    rows = []
    for u in grid:
        ll = 0.0
        for row in relations:
            ua = (ANCHORS[row["anchor_game"]] - 50.0) / 20.0
            p = sigmoid(u - ua) if model == "bt" else normal_cdf((u - ua) / math.sqrt(2.0))
            p = min(max(p, 1e-9), 1.0 - 1e-9)
            y = 1.0 if row["relation"] == "candidate_better" else 0.0 if row["relation"] == "anchor_better" else 0.5
            ll += y * math.log(p) + (1.0-y) * math.log(1.0-p)
        rows.append((u,ll))
    best=max(rows,key=lambda x:x[1])[0]
    max_ll=max(x[1] for x in rows)
    weights=[math.exp(ll-max_ll) for _,ll in rows]
    z=sum(weights)
    c=0.0; lo=hi=None
    for (u,_),w in zip(rows,weights):
        c += w/z
        if lo is None and c >= .05: lo=u
        if hi is None and c >= .95: hi=u; break
    conv=lambda u:max(0.0,min(100.0,50.0+20.0*u))
    return {"score_0_100":round(conv(best),1),"interval_90":[round(conv(lo),1),round(conv(hi),1)]}
