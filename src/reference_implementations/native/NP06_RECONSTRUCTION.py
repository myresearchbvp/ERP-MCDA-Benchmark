#!/usr/bin/env python3
import csv, math
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE/"NP06_EXTRACTION.csv").open(encoding="utf-8")))
weights={}
perf={}
cluster={}
param={}
for r in rows:
    if r["input_group"]=="subcriterion_weight":
        weights[r["criterion"]]=float(r["value"]); cluster[r["criterion"]]=r["cluster"]
    elif r["input_group"]=="alternative_subcriterion_performance":
        perf[(r["alternative"],r["criterion"])]=float(r["value"]); cluster[r["criterion"]]=r["cluster"]
    elif r["input_group"]=="choquet_parameter":
        param[r["parameter"]]=float(r["value"])

alts=["A1","A2","A3","A4"]
clusters=["VRC","CRC","SRC"]
subcriteria=[f"C1{i}" for i in range(1,7)]+[f"C2{i}" for i in range(1,5)]+[f"C3{i}" for i in range(1,7)]
assert set(weights)==set(subcriteria)
assert all((a,c) in perf for a in alts for c in subcriteria)
for cl in clusters:
    assert abs(sum(weights[c] for c in subcriteria if cluster[c]==cl)-1)<1e-12

# D2 reconstruction of criterion-level performance from Table 6 weights and Table 8 values.
crit={}
for a in alts:
    for cl in clusters:
        crit[(a,cl)]=sum(weights[c]*perf[(a,c)] for c in subcriteria if cluster[c]==cl)

# Article p208 Eqs. (3)-(4): capacities from Shapley indices and interactions.
phi=[param["phi1"],param["phi2"],param["phi3"]]
I={(0,1):param["I12"],(0,2):param["I13"],(1,2):param["I23"]}
def inter(i,j): return I[tuple(sorted((i,j)))]
mu={frozenset():0.0,frozenset({0,1,2}):1.0}
for i in range(3):
    mu[frozenset({i})]=phi[i]-0.5*sum(inter(i,j) for j in range(3) if j!=i)
for i in range(3):
    other=frozenset(j for j in range(3) if j!=i)
    mu[other]=1-phi[i]-0.5*sum(inter(i,j) for j in range(3) if j!=i)

# Fuzzy-measure invariants.
assert abs(sum(phi)-1)<1e-12
for s,v in mu.items():
    assert -1e-12 <= v <= 1+1e-12
# Monotonicity for all subset inclusions.
sets=list(mu)
for s in sets:
    for t in sets:
        if s.issubset(t):
            assert mu[s] <= mu[t]+1e-12

def choquet(vals):
    # Appendix A Eq. (A.1): ascending elementary performances.
    pairs=sorted(enumerate(vals),key=lambda x:x[1])
    total=0.0; prev=0.0
    for k,(idx,val) in enumerate(pairs):
        upper=frozenset(i for i,v in pairs[k:])
        total += (val-prev)*mu[upper]
        prev=val
    return total

score={}
for a in alts:
    vals=[crit[(a,cl)] for cl in clusters]
    score[a]=choquet(vals)
    assert math.isfinite(score[a])

order=sorted(alts,key=lambda a:(-score[a],a))
rank={a:i+1 for i,a in enumerate(order)}

with (HERE/"NP06_INTERMEDIATES.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["record_type","alternative","item","value"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for a in alts:
        for cl in clusters:
            w.writerow({"record_type":"criterion_performance","alternative":a,"item":cl,
                        "value":format(crit[(a,cl)],".15g")})
    for s,v in sorted(mu.items(),key=lambda kv:(len(kv[0]),sorted(kv[0]))):
        lab="EMPTY" if not s else "{" + ",".join(str(i+1) for i in sorted(s)) + "}"
        w.writerow({"record_type":"capacity","alternative":"","item":lab,"value":format(v,".15g")})

with (HERE/"NP06_COMPUTED_OUTPUTS_PRECOMPARISON.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["alternative","final_Choquet_score","rank"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for a in alts:
        w.writerow({"alternative":a,"final_Choquet_score":format(score[a],".15g"),"rank":rank[a]})
print("NP06 reconstruction complete")
