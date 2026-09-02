#!/usr/bin/env python3
import csv, math
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE/"NP05_EXTRACTION.csv").open(encoding="utf-8")))
scale={}
ratings=defaultdict(list)
directions={}
const={}
for r in rows:
    if r["input_group"]=="linguistic_scale":
        scale[r["linguistic_term"]]=float(r["value"])
    elif r["input_group"]=="linguistic_rating":
        ratings[(r["alternative"],r["criterion"])].append((r["decision_maker"],r["linguistic_term"]))
        directions[r["criterion"]]=r["direction"]
    elif r["input_group"]=="method_constant":
        const[r["parameter"]]=float(r["value"])

alts=["A1","A2","A3"]
criteria=[f"C{i}" for i in range(1,7)]
assert set(scale)=={"EG","VVG","VG","G","MG","F","MP","P","VP","VVP"}
assert all(len(ratings[(a,c)])==4 for a in alts for c in criteria)
assert {c for c in criteria if directions[c]=="cost"}=={"C6"}
assert const["q_CE_I"]==2 and const["beta_CE_II"]==3
assert const["HFEE_reference"]==1 and const["utility_percent_scale"]==100

# Article Step 1 / Table 3: duplicate membership degrees are retained only once.
hfe={}
for a in alts:
    for c in criteria:
        hfe[(a,c)]=sorted(set(scale[t] for dm,t in ratings[(a,c)]))

def ce1(h,q):
    # Literal Eq. (18).
    hs=sorted(h); L=len(h)
    T=(1+q)*math.log(1+q) - (2+q)*(math.log(2+q)-math.log(2))
    s=0.0
    for t in range(L):
        a=hs[t]
        b=1-hs[L-1-t]
        mid=(2+q*a+q*b)/2
        s += ((1+q*a)*math.log(1+q*a))/2
        s += ((1+q*b)*math.log(1+q*b))/2
        s -= mid*math.log(mid)
    return 2*s/(L*T)

def ce2(h,beta):
    # Literal Eq. (19), without adding any unprinted factor.
    hs=sorted(h); L=len(h)
    denom=(1-2**(1-beta))*L
    s=0.0
    for t in range(L):
        a=hs[t]
        b=1-hs[L-1-t]
        s += a**beta/2 + b**beta/2 - ((a+b)/2)**beta
    return s/denom

def entropy(kind,h):
    return 1-(ce1(h,const["q_CE_I"]) if kind=="CE-I" else ce2(h,const["beta_CE_II"]))

def criterion_weights(kind,dist):
    ds=[]
    E={}
    for c in criteria:
        ev=[entropy(kind,hfe[(a,c)]) for a in alts]
        E[c]=ev
        dif=[const["HFEE_reference"]-x for x in ev]
        if dist=="Hamming":
            d=sum(abs(x) for x in dif)/len(dif)
        elif dist=="Euclidean":
            d=math.sqrt(sum(x*x for x in dif)/len(dif))
        elif dist=="Hausdorff":
            d=max(abs(x) for x in dif)
        else:
            raise ValueError(dist)
        ds.append(d)
    total=sum(ds)
    assert total>0
    return [d/total for d in ds], E, ds

def weighted_hfe(h,w):
    # Eq. (4) as invoked by Eq. (30): lambda h = {1-(1-mu)^lambda}.
    return [1-(1-mu)**w for mu in h]

def phfe_score(vals):
    # Eqs. (32)-(33), followed by Eq. (20).
    s=sum(vals)
    assert s>0
    p=[v/s for v in vals]
    assert abs(sum(p)-1)<1e-12
    return sum(v*pi for v,pi in zip(vals,p))/sum(p)

def run_model(kind,dist):
    w,E,ds=criterion_weights(kind,dist)
    assert abs(sum(w)-1)<1e-12 and all(0<=x<=1 for x in w)
    sc={}
    for a in alts:
        for j,c in enumerate(criteria):
            wh=weighted_hfe(hfe[(a,c)],w[j])
            sc[(a,c)]=phfe_score(wh)
    z={}
    for c in criteria:
        den=sum(sc[(a,c)] for a in alts)
        assert den>0
        for a in alts:
            z[(a,c)]=sc[(a,c)]/den
        assert abs(sum(z[(a,c)] for a in alts)-1)<1e-12
    sben={a:sum(z[(a,c)] for c in criteria if directions[c]=="benefit") for a in alts}
    scost={a:sum(z[(a,c)] for c in criteria if directions[c]=="cost") for a in alts}
    mincost=min(scost.values())
    sumcost=sum(scost.values())
    denom=sum(mincost/scost[a] for a in alts)
    Q={a:sben[a]+(mincost*sumcost)/(scost[a]*denom) for a in alts}
    maxQ=max(Q.values())
    U={a:const["utility_percent_scale"]*Q[a]/maxQ for a in alts}
    order=sorted(alts,key=lambda a:(-U[a],a))
    rank={a:i+1 for i,a in enumerate(order)}
    return w,E,ds,sc,z,sben,scost,Q,U,rank

model_specs=[("CE-I","Hamming"),("CE-I","Euclidean"),("CE-I","Hausdorff"),
             ("CE-II","Hamming"),("CE-II","Euclidean"),("CE-II","Hausdorff")]

out=[]
inter=[]
for kind,dist in model_specs:
    model=f"p-HFC_{kind}_{dist}"
    w,E,ds,sc,z,sben,scost,Q,U,rank=run_model(kind,dist)
    for j,c in enumerate(criteria):
        inter.append({"model":model,"record_type":"criterion_weight","criterion":c,"alternative":"",
                      "value":format(w[j],".15g"),"aux1":format(ds[j],".15g"),"aux2":""})
        for ai,a in enumerate(alts):
            inter.append({"model":model,"record_type":"entropy","criterion":c,"alternative":a,
                          "value":format(E[c][ai],".15g"),"aux1":"","aux2":""})
    for a in alts:
        inter.append({"model":model,"record_type":"COPRAS_components","criterion":"","alternative":a,
                      "value":format(Q[a],".15g"),"aux1":format(sben[a],".15g"),"aux2":format(scost[a],".15g")})
        out.append({"model":model,"cross_entropy":kind,"distance":dist,"alternative":a,
                    "U_percent":format(U[a],".15g"),"Q":format(Q[a],".15g"),"rank":rank[a]})
        assert math.isfinite(U[a]) and math.isfinite(Q[a])

with (HERE/"NP05_COMPUTED_OUTPUTS_PRECOMPARISON.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["model","cross_entropy","distance","alternative","U_percent","Q","rank"]
    wri=csv.DictWriter(f,fieldnames=fields); wri.writeheader(); wri.writerows(out)
with (HERE/"NP05_INTERMEDIATES.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["model","record_type","criterion","alternative","value","aux1","aux2"]
    wri=csv.DictWriter(f,fieldnames=fields); wri.writeheader(); wri.writerows(inter)

print("NP05 reconstruction complete")
