#!/usr/bin/env python3
import csv, math
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
EXTRACTION = HERE / "NP04_EXTRACTION.csv"
OUT = HERE / "NP04_COMPUTED_OUTPUTS_PRECOMPARISON.csv"
INTER = HERE / "NP04_INTERMEDIATES.csv"

rows=list(csv.DictReader(EXTRACTION.open(encoding="utf-8")))
ratings=defaultdict(list)
weights={}
directions={}
for r in rows:
    if r["input_group"]=="manager_rating":
        ratings[(r["alternative"],r["criterion"])].append(float(r["value"]))
        directions[r["criterion"]]=r["direction"]
    elif r["input_group"]=="global_rough_weight":
        weights[r["criterion"]]=(float(r["value_low"]),float(r["value_high"]))
        directions[r["criterion"]]=r["direction"]

alts=sorted({a for a,c in ratings}, key=lambda x:int(x.split("-")[1]))
criteria=["EIS","SR","CMI","CS","EU","RS","SFR","QSS","F","IC","PC","MSC"]

assert alts == [f"SFT-{i}" for i in range(1,7)]
assert set(criteria)==set(weights)
assert all(len(ratings[(a,c)])==7 for a in alts for c in criteria)
assert all(directions[c] in {"benefit","cost"} for c in criteria)
assert {c for c in criteria if directions[c]=="cost"}=={"IC","PC","MSC"}

def rough_group(vals):
    # Eqs. (3)-(5): individual lower/upper approximation means,
    # then the group rough interval is the average of managers' individual limits.
    lows=[]; highs=[]
    for v in vals:
        lows.append(sum(x for x in vals if x<=v)/sum(1 for x in vals if x<=v))
        highs.append(sum(x for x in vals if x>=v)/sum(1 for x in vals if x>=v))
    return sum(lows)/len(lows), sum(highs)/len(highs)

rough={(a,c):rough_group(ratings[(a,c)]) for a in alts for c in criteria}
max_upper={c:max(rough[(a,c)][1] for a in alts) for c in criteria}
norm={(a,c):(rough[(a,c)][0]/max_upper[c],rough[(a,c)][1]/max_upper[c]) for a in alts for c in criteria}

def prod(xs):
    p=1.0
    for x in xs: p*=x
    return p

inter_rows=[]
raw_util={}
for a in alts:
    b=[c for c in criteria if directions[c]=="benefit"]
    k=[c for c in criteria if directions[c]=="cost"]
    kp=(sum(norm[(a,c)][0]*weights[c][0] for c in b),
        sum(norm[(a,c)][1]*weights[c][1] for c in b))
    km=(sum(norm[(a,c)][0]*weights[c][0] for c in k),
        sum(norm[(a,c)][1]*weights[c][1] for c in k))
    pp=(prod(norm[(a,c)][0]*weights[c][0] for c in b),
        prod(norm[(a,c)][1]*weights[c][1] for c in b))
    pm=(prod(norm[(a,c)][0]*weights[c][0] for c in k),
        prod(norm[(a,c)][1]*weights[c][1] for c in k))
    ysd=(kp[0]-km[1], kp[1]-km[0])
    ytd=(pp[0]-pm[1], pp[1]-pm[0])
    ysr=(kp[0]/km[1], kp[1]/km[0])
    ytr=(pp[0]/pm[1], pp[1]/pm[0])
    raw_util[a]={"K+":kp,"K-":km,"P+":pp,"P-":pm,"Ysd":ysd,"Ytd":ytd,"Ysr":ysr,"Ytr":ytr}

# Eqs. (25)-(28): each utility family normalized using maximum upper endpoint.
norm_util={}
for key in ["Ysd","Ytd","Ysr","Ytr"]:
    den=1+max(raw_util[a][key][1] for a in alts)
    for a in alts:
        lo,hi=raw_util[a][key]
        norm_util[(a,key)]=((1+lo)/den,(1+hi)/den)

terminal=[]
for a in alts:
    low=sum(norm_util[(a,k)][0] for k in ["Ysd","Ytd","Ysr","Ytr"])/4
    high=sum(norm_util[(a,k)][1] for k in ["Ysd","Ytd","Ysr","Ytr"])/4
    crisp=(low+high)/2
    terminal.append((a,low,high,crisp))
terminal_sorted=sorted(terminal,key=lambda r:(-r[3],r[0]))
rank={a:i+1 for i,(a,*_) in enumerate(terminal_sorted)}

with INTER.open("w",newline="",encoding="utf-8") as f:
    fields=["alternative","criterion","rough_low","rough_high","normalized_low","normalized_high","weight_low","weight_high","direction"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for a in alts:
        for c in criteria:
            w.writerow({"alternative":a,"criterion":c,
                        "rough_low":format(rough[(a,c)][0],".15g"),"rough_high":format(rough[(a,c)][1],".15g"),
                        "normalized_low":format(norm[(a,c)][0],".15g"),"normalized_high":format(norm[(a,c)][1],".15g"),
                        "weight_low":format(weights[c][0],".15g"),"weight_high":format(weights[c][1],".15g"),
                        "direction":directions[c]})

with OUT.open("w",newline="",encoding="utf-8") as f:
    fields=["alternative","RN_Y_low","RN_Y_high","Y_crisp","rank"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for a,low,high,crisp in terminal:
        assert math.isfinite(low) and math.isfinite(high) and math.isfinite(crisp)
        assert low <= high
        w.writerow({"alternative":a,"RN_Y_low":format(low,".15g"),"RN_Y_high":format(high,".15g"),
                    "Y_crisp":format(crisp,".15g"),"rank":rank[a]})

print("NP04 reconstruction complete:", OUT.name)
