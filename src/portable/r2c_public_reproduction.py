#!/usr/bin/env python3
"""Current deletion analysis: original 118 operations plus six post hoc NP11 models."""
from __future__ import annotations
from pathlib import Path
from types import SimpleNamespace
import importlib.util, shutil, csv
import numpy as np
from portable.np11_certified_deletion import reproduce as reproduce_np11

def load(path:Path):
    spec=importlib.util.spec_from_file_location("r2c_reference",path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def read(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def write(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def reproduce(repo:Path,out:Path,solve_np11=True):
    code=repo/"src/reference_implementations/robustness/R2C_SINGLE_CRITERION_DELETION.py"
    m=load(code)
    spec_src=repo/"data/standardized/robustness/R2C/historical/R2C_EXECUTION_SPEC.csv"
    out.mkdir(parents=True,exist_ok=True); historical=out/'historical';historical.mkdir(exist_ok=True)
    shutil.copy2(spec_src,historical/"R2C_EXECUTION_SPEC.csv")
    rt=repo/"data/standardized/runtime"
    args=SimpleNamespace(r1a=rt/"R1A",r1b=rt/"R1B",r1c=rt/"R1C",r1d=rt/"R1D",
                         r2a=repo/"data/standardized/robustness/R2A",r2b=rt/"R2B",out=historical)
    inp=m.Inputs(args.r1a,args.r1b,args.r1c,args.r1d,args.r2a,args.r2b)
    m.execute_deletions(args,inp,historical)
    certified=reproduce_np11(repo,out/'NP11',solve=solve_np11)
    old=read(historical/'R2C_DELETION_LEVEL_RESULTS.csv');assert len(old)==118 and not any(r['NP_ID']=='NP11' for r in old)
    new=[];baseline=['S4','S3','S1','S2'];alts=['S1','S2','S3','S4']
    for r in certified:
        rank=r['certified_complete_ranking'].split('>');pos={s:i for i,s in enumerate(rank)};bpos={s:i for i,s in enumerate(baseline)}
        inversions=sum((pos[a]-pos[b])*(bpos[a]-bpos[b])<0 for j,a in enumerate(alts) for b in alts[j+1:])
        row={k:'' for k in old[0]}
        row.update(NP_ID='NP11',configuration_or_branch='LFPP_REDUCED_CRITERIA',deleted_criterion=r['criterion_removed'],operation_type='REDUCED_LFPP_FIXED_LOCAL_ERP_WEIGHTS',status='EXECUTED_POST_HOC',baseline_winner_retained='YES' if r['baseline_winner_retained']=='True' else 'NO',exact_winner_set=rank[0],baseline_top2_both_retained='YES' if set(rank[:2])==set(baseline[:2]) else 'NO',baseline_top2_overlap_share=m.fmt(len(set(rank[:2])&set(baseline[:2]))/2),MARD=m.fmt(np.mean([abs(pos[s]-bpos[s]) for s in alts])),Kendall_tau_b=m.fmt(1-inversions/3),complete_weak_order=' > '.join(rank),native_solver_status='GLOBAL_RANKING_CERTIFIED',method_note='Post hoc; M=1000; original local ERP weights fixed; ranking identified across global criterion optima; scores nonunique and not represented by a single value here')
        new.append(row)
    rows=[dict(r,analysis_origin='ORIGINAL_BENCHMARK',baseline_complete_ranking_retained='') for r in old]+[dict(r,analysis_origin='POST_HOC_NP11_EXTENSION',baseline_complete_ranking_retained=c['baseline_complete_ranking_retained']) for r,c in zip(new,certified)]
    write(out/'R2C_DELETION_LEVEL_RESULTS.csv',rows)
    for name in ('R2C_NP03_PARALLEL_BRANCH_COMPARISON.csv','R2C_NP05_SIX_CONFIGURATION_SUMMARY.csv','R2C_NP12_VIKOR_DELETION_SUMMARY.csv'):shutil.copy2(historical/name,out/name)
    ne=[r for r in read(historical/'R2C_NE_RECORDS.csv') if r['NP_ID']!='NP11'];assert len(ne)==41;write(out/'R2C_NE_RECORDS.csv',ne)
    cases=read(historical/'R2C_CASE_LEVEL_SUMMARY.csv')
    # Ordinal baseline for rank-only metrics; never exported as LFPP scores.
    ordinal_baseline={'scores':np.array([1.,0.,2.,3.]),'alts':alts,'higher':True}
    case=m.case_summary_row('NP11','LFPP_REDUCED_CRITERIA',new,ordinal_baseline)
    case['caveat']='Post hoc; six fixed-local LFPP deletions; rankings globally identified; weights and scores nonunique; complete-ranking retention 3/6; descriptive shares only'
    cases.append(case);cases.sort(key=lambda x:(x['NP_ID'],x['configuration_or_branch']));write(out/'R2C_CASE_LEVEL_SUMMARY.csv',cases)
    cross=read(historical/'R2C_CROSS_CASE_SUMMARY.csv')
    for r in cross:
        if r['NP_ID']=='NP11':r.update(single_criterion_deletion_applicability='APPLICABLE',operation_type='REDUCED_LFPP_FIXED_LOCAL_ERP_WEIGHTS',applicable_deletion_count='6',winner_or_recommendation_retention_share=m.fmt(5/6),winner_or_recommendation_critical_deletions='1',branch_configuration_caveat='POST_HOC_NP11_EXTENSION; complete-ranking retention 3/6; C6 changes S4 to S3; DEMATEL excluded')
    write(out/'R2C_CROSS_CASE_SUMMARY.csv',cross)
    shutil.copy2(repo/'data/standardized/robustness/R2C/R2C_EXECUTION_SPEC.csv',out/'R2C_EXECUTION_SPEC.csv')
    current_note = 'ERP-MCDA benchmark: criterion-deletion methods\n\nThis deterministic single-criterion deletion analysis uses method-compatible recomputation. It contains 118 original operations and six post hoc NP11 deletions. All eight applicable lineages have evaluable outcomes; 41 specification rows are NE.\n\nTotal executed deletion-outcome rows=124\nNP01: 12; NP02: 5; NP03: 30 (15 criteria in each of two branches); NP04: 12; NP05: 30 (five criteria in each of six configurations); NP07: 11; NP11: 6; NP12: 18.\n\nNP01: Remove the subcriterion from its local triangular-fuzzy reciprocal matrix and recompute that fuzzy-AHP weight vector by the geometric-mean/defuzzification rule. Keep the three main-criterion weights fixed, regenerate global weights and recompute TOPSIS.\nNP02: Recompute the reduced criteria AHP matrix by column normalization and row means, then combine the retained local alternative priorities.\nNP03: Remove the criterion from the normalized D2 checkpoint, renormalize the remaining weights and recompute TOPSIS. Evaluate the same 15 deletions separately for A_STRICT_EXPLICIT_DIRECTION and ERP04_COST_PARALLEL.\nNP04: Remove the criterion from the rough-normalized checkpoint derived from the raw source supplement. Keep the remaining printed rough weights fixed and recompute the native rough-WISP K/P aggregates and four utility families.\nNP05: Evaluate C1–C5 for all six CE-I/CE-II × Hamming/Euclidean/Hausdorff configurations. Recompute entropy-distance normalization and the p-HFC/COPRAS chain; q=2 and beta=3 are fixed. C6 is NE because removing the sole cost criterion leaves the native cost-side formula undefined.\nNP06: NE: the source does not define a reduced Choquet capacity. The reported interaction-off comparison is addressed separately under source-defined sensitivity.\nNP07: For the Kılıç et al. (2015) baseline, remove the criterion, renormalize the retained printed ANP weights and recompute PROMETHEE II with V-shape p=2. The linked Temur–Bolat CBDO implementation cannot be reconstructed from the available source material.\nNP08: NE: the source does not identify a unique terminal LP solution or tie-break rule.\nNP09: NE: the literal computational chain becomes nonfinite before producing a terminal result.\nNP10: NE at D0/O3: the operative Qb/Qn mapping and Supplementary Tables S1–S6 are unavailable.\nNP11: Recompute criterion weights with LFPP and M=1000 while holding local ERP weights fixed. All six deletions have certified rankings despite nonunique optimal weights and scores. Winner retention is 5/6; complete-ranking retention is 3/6; C6 changes S4 to S3. SLSQP does not converge for C6; independent convex calculations and rational/interval certificates establish its ranking. DEMATEL is separate from ERP ranking.\nNP12: Renormalize the retained published weights, hold q/v=0.5 fixed and recompute S, R, Q and the native VIKOR compromise conditions. The recommendation set is the primary outcome; the top-Q leader is a secondary diagnostic.\n\nRetention shares describe the finite set of eligible deletions. They do not estimate real-world choice probabilities or literature-wide robustness rates. Files under historical/ preserve the original execution records; their NP11 NE labels denote nonexecution.\n'
    (out/'R2C_CASE_METHOD_NOTES.txt').write_text(current_note)
    return out
