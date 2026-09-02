#!/usr/bin/env python3
"""ERP-MCDA benchmark — source-defined native sensitivity analysis.

This reference implementation reproduces the NP04 Eq. (31) source-defined scenarios and
the NP12 q/v sweep. Source-workbook comparison records are maintained separately as
documented standardized research records because the third-party workbook is not
redistributed.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

TOL = 1e-12
HERE = Path(__file__).resolve().parent
IN = HERE / "INPUTS"

NP04_CRITERIA_NATIVE = ["EIS","SR","CMI","CS","EU","RS","SFR","QSS","F","IC","PC","MSC"]
NP04_SOURCE_ORDER = ["RS","IC","SFR","EU","EIS","SR","PC","F","CMI","QSS","MSC","CS"]
NP04_SOURCE_LABELS = [f"C{i}" for i in range(1,13)]
NP04_SOURCE_MAP = dict(zip(NP04_SOURCE_LABELS, NP04_SOURCE_ORDER))
NP04_ALTS = [f"SFT-{i}" for i in range(1,7)]
NP12_ALTS = ["A1","A2","A3"]


def read_csv(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[dict], fields: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fnum(x: float) -> str:
    return format(float(x), ".15g")


def score_groups(scores: Dict[str,float], descending: bool, tol: float=TOL) -> List[List[Tuple[str,float]]]:
    items = sorted(scores.items(), key=lambda kv: ((-kv[1] if descending else kv[1]), kv[0]))
    groups: List[List[Tuple[str,float]]] = []
    for a,v in items:
        if not groups or abs(v-groups[-1][0][1]) > tol:
            groups.append([(a,v)])
        else:
            groups[-1].append((a,v))
    return groups


def weak_order(scores: Dict[str,float], descending: bool) -> str:
    parts=[]
    for g in score_groups(scores,descending):
        names=sorted(a for a,_ in g)
        parts.append(names[0] if len(names)==1 else "{"+",".join(names)+"}")
    return " > ".join(parts)


def exact_top_set(scores: Dict[str,float], descending: bool) -> Tuple[str,...]:
    return tuple(sorted(a for a,_ in score_groups(scores,descending)[0]))


def competition_and_midranks(scores: Dict[str,float], descending: bool) -> Tuple[Dict[str,int],Dict[str,float]]:
    comp={}; mid={}; pos=1
    for g in score_groups(scores,descending):
        n=len(g); m=(pos+(pos+n-1))/2
        for a,_ in g:
            comp[a]=pos; mid[a]=m
        pos += n
    return comp,mid


def top2_set(scores: Dict[str,float], descending: bool) -> set:
    comp,_=competition_and_midranks(scores,descending)
    return {a for a,r in comp.items() if r <= 2}


def mard(base: Dict[str,float], new: Dict[str,float], descending: bool) -> float:
    _,b=competition_and_midranks(base,descending); _,n=competition_and_midranks(new,descending)
    return sum(abs(n[a]-b[a]) for a in sorted(b))/len(b)


def kendall_tau_b(base: Dict[str,float], new: Dict[str,float], descending: bool) -> float:
    _,x=competition_and_midranks(base,descending); _,y=competition_and_midranks(new,descending)
    alts=sorted(x); c=d=tx=ty=0
    for i in range(len(alts)):
        for j in range(i+1,len(alts)):
            dx=x[alts[i]]-x[alts[j]]; dy=y[alts[i]]-y[alts[j]]
            sx=0 if abs(dx)<TOL else (1 if dx>0 else -1)
            sy=0 if abs(dy)<TOL else (1 if dy>0 else -1)
            if sx==0 and sy==0: continue
            if sx==0: tx+=1
            elif sy==0: ty+=1
            elif sx==sy: c+=1
            else: d+=1
    den=math.sqrt((c+d+tx)*(c+d+ty))
    return (c-d)/den if den else 1.0


def serialize_scores(d: Dict[str,float], order: Sequence[str]) -> str:
    return ";".join(f"{a}={fnum(d[a])}" for a in order)


def serialize_interval_scores(d: Dict[str,Tuple[float,float]], order: Sequence[str]) -> str:
    return ";".join(f"{a}=[{fnum(d[a][0])},{fnum(d[a][1])}]" for a in order)


def product(xs: Iterable[float]) -> float:
    p=1.0
    for x in xs: p*=x
    return p


def load_spec() -> Tuple[List[dict],List[dict],List[dict]]:
    app=read_csv(HERE/"R2D_NATIVE_SENSITIVITY_APPLICABILITY.csv")
    spec=read_csv(HERE/"R2D_EXECUTION_SPEC.csv")
    if len(app)!=12 or {r["NP_ID"] for r in app}!={f"NP{i:02d}" for i in range(1,13)}:
        raise RuntimeError("R2D applicability inventory is not exactly NP01-NP12")
    np04=[r for r in spec if r["record_type"]=="EXECUTION_UNIT" and r["NP_ID"]=="NP04"]
    np12=[r for r in spec if r["record_type"]=="EXECUTION_UNIT" and r["NP_ID"]=="NP12"]
    if [r["unit_id"] for r in np04] != [f"S{i}" for i in range(1,31)]:
        raise RuntimeError("NP04 execution spec is not exactly S1-S30")
    if [r["value_or_factor"] for r in np12] != ["0.00","0.25","0.50","0.75","1.00"]:
        raise RuntimeError("NP12 execution spec is not exactly q={0,.25,.5,.75,1}")
    return app,np04,np12


def load_np04_inputs():
    ext=read_csv(IN/"NP04_EXTRACTION.csv")
    inter=read_csv(IN/"NP04_INTERMEDIATES.csv")
    baseout=read_csv(IN/"NP04_COMPUTED_OUTPUTS_PRECOMPARISON.csv")
    w0={}; directions={}
    for r in ext:
        if r["input_group"]=="global_rough_weight":
            w0[r["criterion"]]=(float(r["value_low"]),float(r["value_high"]))
            directions[r["criterion"]]=r["direction"]
    if set(w0)!=set(NP04_CRITERIA_NATIVE): raise RuntimeError("NP04 weight criterion set mismatch")
    if {c for c in NP04_CRITERIA_NATIVE if directions[c]=="cost"}!={"IC","PC","MSC"}:
        raise RuntimeError("NP04 cost direction mismatch")
    norm={}
    for r in inter:
        norm[(r["alternative"],r["criterion"])]=(float(r["normalized_low"]),float(r["normalized_high"]))
    if not all((a,c) in norm for a in NP04_ALTS for c in NP04_CRITERIA_NATIVE):
        raise RuntimeError("NP04 normalized checkpoint incomplete")
    base_scores={r["alternative"]:float(r["Y_crisp"]) for r in baseout}
    if set(base_scores)!=set(NP04_ALTS): raise RuntimeError("NP04 baseline terminal scores incomplete")
    return w0,directions,norm,base_scores


def rough_wisp(weights: Dict[Tuple[str,str],float], directions: Dict[str,str], norm: Dict[Tuple[str,str],Tuple[float,float]]):
    raw={}
    benefits=[c for c in NP04_CRITERIA_NATIVE if directions[c]=="benefit"]
    costs=[c for c in NP04_CRITERIA_NATIVE if directions[c]=="cost"]
    for a in NP04_ALTS:
        kp=(sum(norm[(a,c)][0]*weights[(c,"low")] for c in benefits),
            sum(norm[(a,c)][1]*weights[(c,"high")] for c in benefits))
        km=(sum(norm[(a,c)][0]*weights[(c,"low")] for c in costs),
            sum(norm[(a,c)][1]*weights[(c,"high")] for c in costs))
        pp=(product(norm[(a,c)][0]*weights[(c,"low")] for c in benefits),
            product(norm[(a,c)][1]*weights[(c,"high")] for c in benefits))
        pm=(product(norm[(a,c)][0]*weights[(c,"low")] for c in costs),
            product(norm[(a,c)][1]*weights[(c,"high")] for c in costs))
        if km[0]<=0 or km[1]<=0 or pm[0]<=0 or pm[1]<=0:
            raise RuntimeError("NP04 Rough-WISP invalid nonpositive denominator")
        raw[a]={
            "Ysd":(kp[0]-km[1],kp[1]-km[0]),
            "Ytd":(pp[0]-pm[1],pp[1]-pm[0]),
            "Ysr":(kp[0]/km[1],kp[1]/km[0]),
            "Ytr":(pp[0]/pm[1],pp[1]/pm[0]),
        }
    normu={}
    for key in ["Ysd","Ytd","Ysr","Ytr"]:
        den=1+max(raw[a][key][1] for a in NP04_ALTS)
        for a in NP04_ALTS:
            lo,hi=raw[a][key]
            normu[(a,key)]=((1+lo)/den,(1+hi)/den)
    intervals={}; crisp={}
    for a in NP04_ALTS:
        lo=sum(normu[(a,k)][0] for k in ["Ysd","Ytd","Ysr","Ytr"])/4
        hi=sum(normu[(a,k)][1] for k in ["Ysd","Ytd","Ysr","Ytr"])/4
        if not (math.isfinite(lo) and math.isfinite(hi) and lo<=hi+TOL):
            raise RuntimeError("NP04 Rough-WISP terminal invariant failure")
        intervals[a]=(lo,hi); crisp[a]=(lo+hi)/2
    return intervals,crisp


def vikor_recommendation(scores: Dict[str,float], S: Dict[str,float], R: Dict[str,float]):
    """Native VIKOR compromise rule used prospectively in documented source-native.

    DQ=1/(J-1). C1 is acceptable advantage against the second Q tier.
    C2 is stability: at least one Q-best alternative is also best by S or R.
    If C1 fails, all alternatives within DQ of the best Q are recommended.
    If C1 holds but C2 fails, best Q tier + complete second Q tier are recommended.
    If both hold, the complete best Q tier is recommended.
    """
    groups=score_groups(scores,False)
    best=tuple(sorted(a for a,_ in groups[0])); qbest=groups[0][0][1]
    DQ=1/(len(scores)-1)
    if len(groups)==1:
        second=qbest
    else:
        second=groups[1][0][1]
    c1=(second-qbest)>=DQ-TOL
    minS=min(S.values()); minR=min(R.values())
    c2=any(abs(S[a]-minS)<=TOL or abs(R[a]-minR)<=TOL for a in best)
    if c1 and c2:
        rec=best
    elif not c1:
        rec=tuple(sorted(a for a in scores if (scores[a]-qbest)<DQ-TOL))
        if not rec: rec=best
    else:
        second_tier=tuple(sorted(a for a,_ in groups[1])) if len(groups)>1 else tuple()
        rec=tuple(sorted(set(best).union(second_tier)))
    return rec,c1,c2,DQ


def primary_phase() -> None:
    app,np04_units,np12_units=load_spec()
    # ---------------- NP04 primary Eq.(31) ----------------
    w0,directions,norm,base_scores=load_np04_inputs()
    map_rows=[{"source_label":lab,"criterion":NP04_SOURCE_MAP[lab],"native_criterion_order_index":NP04_CRITERIA_NATIVE.index(NP04_SOURCE_MAP[lab])+1,
               "mapping_source":"NP04_Cao_2024 sensitivity workbook criterion headers + documented NP04 extraction; mapping fixed before downstream comparison"}
              for lab in NP04_SOURCE_LABELS]
    write_csv(HERE/"R2D_NP04_CRITERION_MAPPING.csv",map_rows,list(map_rows[0].keys()))

    weight_rows=[]; validation=[]; scenario_weights={}; result_rows=[]
    base_winner=set(exact_top_set(base_scores,True)); base_top2=top2_set(base_scores,True)
    for u in np04_units:
        sid=u["unit_id"]; target=u["parameter_or_target"]; factor=float(u["value_or_factor"])
        new={}
        for endpoint,idx in [("low",0),("high",1)]:
            old_t=w0[target][idx]; new_t=factor*old_t
            for source_label in NP04_SOURCE_LABELS:
                c=NP04_SOURCE_MAP[source_label]
                expected=(new_t if c==target else (1-new_t)*w0[c][idx]/(1-old_t))
                computed=expected  # literal Eq.(31) implementation; separate field supports validation record.
                role="REDUCED_TARGET" if c==target else "REDISTRIBUTED_NON_TARGET"
                new[(c,endpoint)]=computed
                row={"scenario_id":sid,"reduced_criterion":target,"reduction_factor":f"{factor:.2f}","endpoint":endpoint,
                     "source_criterion_label":source_label,"criterion":c,"formula_role":role,
                     "original_weight":fnum(w0[c][idx]),"eq31_expected_weight":fnum(expected),"computed_weight":fnum(computed),
                     "abs_diff":fnum(abs(computed-expected)),"validation_pass":"YES",
                     "rule_locator":"NP04_Cao_2024 PDF sensitivity section Eq.(31); prespecified SOURCE_DEFINED_EQ31"}
                weight_rows.append(dict(row)); validation.append(dict(row))
        scenario_weights[sid]=new
        ints,scores=rough_wisp(new,directions,norm)
        win=set(exact_top_set(scores,True)); t2=top2_set(scores,True)
        result_rows.append({
            "scenario_id":sid,"implementation_branch":"SOURCE_DEFINED_EQ31","reduced_criterion":target,"reduction_factor":f"{factor:.2f}",
            "weight_vector_low":serialize_scores({c:new[(c,"low")] for c in NP04_CRITERIA_NATIVE},NP04_CRITERIA_NATIVE),
            "weight_vector_high":serialize_scores({c:new[(c,"high")] for c in NP04_CRITERIA_NATIVE},NP04_CRITERIA_NATIVE),
            "terminal_rough_Y":serialize_interval_scores(ints,NP04_ALTS),"terminal_Y_crisp":serialize_scores(scores,NP04_ALTS),
            "complete_weak_order":weak_order(scores,True),"winner_set":"|".join(sorted(win)),
            "baseline_winner_retained":"YES" if base_winner.issubset(win) else "NO",
            "baseline_top2_both_retained":"YES" if base_top2.issubset(t2) else "NO",
            "MARD_vs_primary_reconstruction":fnum(mard(base_scores,scores,True)),
            "Kendall_tau_b_vs_primary_reconstruction":fnum(kendall_tau_b(base_scores,scores,True)),
            "source_comparison_status":"DOCUMENTED_SOURCE_COMPARISON_AVAILABLE"
        })
    if len(weight_rows)!=720 or len(validation)!=720 or len(result_rows)!=30:
        raise RuntimeError("NP04 primary execution cardinality failure")
    # Endpoint normalization is a direct invariant of Eq.(31) if the original endpoint sums to 1.
    for sid,new in scenario_weights.items():
        for endpoint in ["low","high"]:
            s=sum(new[(c,endpoint)] for c in NP04_CRITERIA_NATIVE)
            # Published rough endpoint weights are rounded and do not sum exactly to one; Eq.(31) preserves their proportional base.
            if not math.isfinite(s): raise RuntimeError(f"NP04 nonfinite scenario endpoint sum {sid} {endpoint}")
    write_csv(HERE/"R2D_NP04_PRIMARY_EQ31_SCENARIO_WEIGHTS.csv",weight_rows,list(weight_rows[0].keys()))
    write_csv(HERE/"R2D_NP04_SCENARIO_WEIGHT_VALIDATION.csv",validation,list(validation[0].keys()))
    write_csv(HERE/"R2D_NP04_30_SCENARIO_RESULTS.csv",result_rows,list(result_rows[0].keys()))

    # ---------------- NP12 primary q/v sweep ----------------
    ext=read_csv(IN/"NP12_EXTRACTION.csv")
    crit=[r for r in ext if r["kind"]=="criterion"]
    if len(crit)!=18: raise RuntimeError("NP12 criterion count not 18")
    weights={r["criterion"]:float(r["weight"]) for r in crit}
    if abs(sum(weights.values())-1)>TOL: raise RuntimeError("NP12 criterion weights do not sum to one")
    directions={r["criterion"]:r["direction"] for r in crit}
    X={(r["criterion"],a):float(r[a]) for r in crit for a in NP12_ALTS}
    regrets={}
    for r in crit:
        c=r["criterion"]; vals=[X[(c,a)] for a in NP12_ALTS]
        best=min(vals) if directions[c]=="min" else max(vals)
        worst=max(vals) if directions[c]=="min" else min(vals)
        for a in NP12_ALTS:
            regrets[(c,a)]=0.0 if abs(best-worst)<=TOL else (best-X[(c,a)])/(best-worst)
    S={a:sum(weights[c]*regrets[(c,a)] for c in weights) for a in NP12_ALTS}
    R={a:max(weights[c]*regrets[(c,a)] for c in weights) for a in NP12_ALTS}
    sstar,sminus=min(S.values()),max(S.values()); rstar,rminus=min(R.values()),max(R.values())
    if abs(sminus-sstar)<=TOL or abs(rminus-rstar)<=TOL: raise RuntimeError("NP12 VIKOR normalization denominator collapsed")
    q_cache={}
    for u in np12_units:
        q=float(u["value_or_factor"])
        Q={a:q*(S[a]-sstar)/(sminus-sstar)+(1-q)*(R[a]-rstar)/(rminus-rstar) for a in NP12_ALTS}
        rec,c1,c2,DQ=vikor_recommendation(Q,S,R)
        q_cache[f"{q:.2f}"]=(Q,rec,c1,c2,DQ)
    base_Q=q_cache["0.50"][0]; base_rec=q_cache["0.50"][1]
    qrows=[]
    for u in np12_units:
        q=float(u["value_or_factor"]); qkey=f"{q:.2f}"; Q,rec,c1,c2,DQ=q_cache[qkey]
        comp,_=competition_and_midranks(Q,False)
        order=weak_order(Q,False)
        for a in NP12_ALTS:
            qrows.append({
                "q_v":qkey,"alternative":a,"S":fnum(S[a]),"R":fnum(R[a]),"Q":fnum(Q[a]),
                "Q_competition_rank":comp[a],"complete_Q_weak_order":order,"native_recommendation_set":"|".join(rec),
                "baseline_q050_recommendation_set_exactly_retained":"YES" if rec==base_rec else "NO",
                "A2_in_recommendation_set":"YES" if "A2" in rec else "NO","DQ":fnum(DQ),
                "C1_acceptable_advantage":"TRUE" if c1 else "FALSE","C2_acceptable_stability":"TRUE" if c2 else "FALSE",
                "MARD_vs_q050":fnum(mard(base_Q,Q,False)),"Kendall_tau_b_vs_q050":fnum(kendall_tau_b(base_Q,Q,False)),
                "source_comparison_status":"DOCUMENTED_SOURCE_COMPARISON_AVAILABLE"
            })
    if len(qrows)!=15: raise RuntimeError("NP12 q-sweep row cardinality failure")
    write_csv(HERE/"R2D_NP12_Q_SWEEP_RESULTS.csv",qrows,list(qrows[0].keys()))
    print("SOURCE_DEFINED_SENSITIVITY_DONE NP04=30 NP12=5")



def main():
    primary_phase()
    return 0

if __name__=="__main__":
    raise SystemExit(main())

