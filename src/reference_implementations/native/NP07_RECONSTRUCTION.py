#!/usr/bin/env python3
import csv, math
from pathlib import Path
import numpy as np

OUT=Path(__file__).with_name('NP07_COMPUTED_OUTPUTS_PRECOMPARISON.csv')
weights=np.array([10.99,4.39,3.61,1.25,8.67,22.18,12.40,10.16,7.72,16.41,2.22],dtype=float)/100.0
alts=['A','B','C','D','E']
scores=np.array([
[4,5,5,4,2,2,1,3,5,3,3],
[4,2,3,4,2,2,2,3,4,3,3],
[3,3,3,3,2,2,2,4,4,3,3],
[2,2,2,2,3,3,4,2,3,3,2],
[2,2,1,3,3,3,4,2,2,4,2]],dtype=float)
p=2.0
n=len(alts)
pi=np.zeros((n,n),dtype=float)
for a in range(n):
    for b in range(n):
        if a==b: continue
        d=scores[a]-scores[b]
        P=np.where(d<=0.0,0.0,np.where(d<p,d/p,1.0))
        pi[a,b]=float(np.dot(weights,P))
phi_plus=pi.sum(axis=1)/(n-1)
phi_minus=pi.sum(axis=0)/(n-1)
phi=phi_plus-phi_minus
order=np.argsort(-phi,kind='stable')
ranks=np.empty(n,int)
for r,idx in enumerate(order,1): ranks[idx]=r
rows=[]
for i,a in enumerate(alts):
    rows.append({'publication_model':'NP07_Kilic_2015 Kılıç et al. 2015 — ANP + PROMETHEE II','status':'EVALUABLE','alternative':a,'positive_flow':format(phi_plus[i],'.15g'),'negative_flow':format(phi_minus[i],'.15g'),'net_flow':format(phi[i],'.15g'),'rank':int(ranks[i]),'winner':'YES' if ranks[i]==1 else 'NO','note':'literal printed D2 checkpoint'})
rows.append({'publication_model':'NP07_Temur_Bolat_2018 Temur & Bolat 2018 — CBDO robust reanalysis','status':'NOT_EVALUABLE_AT_D3_FROM_PUBLIC_SOURCE','alternative':'','positive_flow':'','negative_flow':'','net_flow':'','rank':'','winner':'','note':'unseeded random CBDO GUI starting points/cloud state and implementation codes are not public in available source materials; no surrogate run performed'})
with OUT.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# deterministic validation assertions for evaluable component
assert scores.shape==(5,11)
assert abs(weights.sum()-1.0)<1e-12
assert np.isfinite(pi).all() and np.isfinite(phi).all()
assert set(ranks)==set(range(1,6))
