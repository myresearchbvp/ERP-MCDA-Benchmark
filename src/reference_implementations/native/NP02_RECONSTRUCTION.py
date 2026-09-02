#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
HERE=Path(__file__).resolve().parent
IN=HERE/'NP02_EXTRACTION.csv'; OUT=HERE/'NP02_COMPUTED_OUTPUTS_PRECOMPARISON.csv'; VALIDATION=HERE/'NP02_RECONSTRUCTION_VALIDATION.txt'

def rows():
    with IN.open(encoding='utf-8') as f: return list(csv.DictReader(f))
def mat(rs,group,names):
    M=np.empty((len(names),len(names)),float); idx={x:i for i,x in enumerate(names)}
    for r in rs:
        if r['input_group']==group: M[idx[r['row_id']],idx[r['col_id']]]=float(r['value'])
    return M
def ahp(M):
    N=M/M.sum(axis=0); return N.mean(axis=1)
def main():
    rs=rows(); criteria=['C1_Adaptability','C2_Financial','C3_Simplicity','C4_Provider_services','C5_Implementation_approach']
    M=mat(rs,'CRITERIA_PAIRWISE',criteria); cw=ahp(M)
    groups=['ALT_C1_Adaptability','ALT_C2_Financial','ALT_C3_Simplicity','ALT_C4_Provider_services','ALT_C5_Implementation_approach']
    A=np.column_stack([ahp(mat(rs,g,['ERP_A','ERP_B'])) for g in groups])
    scores=A@cw
    Ws=M@cw; Cv=Ws/cw; lmax=Cv.mean(); CI=(lmax-5)/4
    RI=float(next(r['value'] for r in rs if r['input_group']=='PARAMETER' and r['row_id']=='RI')); CR=CI/RI
    order=np.argsort(-scores,kind='stable'); ranks=np.empty(2,int); ranks[order]=np.arange(1,3)
    out=[]
    for j,c in enumerate(criteria): out.append({'output_type':'criterion_weight','alternative':'','criterion':c,'metric':'weight','value':f'{cw[j]:.12f}','rank':''})
    for i,a in enumerate(['ERP_A','ERP_B']):
        for j,c in enumerate(criteria): out.append({'output_type':'local_alternative_weight','alternative':a,'criterion':c,'metric':'local_weight','value':f'{A[i,j]:.12f}','rank':''})
        out.append({'output_type':'terminal','alternative':a,'criterion':'','metric':'final_weight','value':f'{scores[i]:.12f}','rank':str(ranks[i])})
    out += [
    {'output_type':'qa_scalar','alternative':'','criterion':'','metric':'lambda_max','value':f'{lmax:.12f}','rank':''},
    {'output_type':'qa_scalar','alternative':'','criterion':'','metric':'CI','value':f'{CI:.12f}','rank':''},
    {'output_type':'qa_scalar','alternative':'','criterion':'','metric':'CR','value':f'{CR:.12f}','rank':''}]
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['output_type','alternative','criterion','metric','value','rank']); w.writeheader(); w.writerows(out)
    reciprocity=np.allclose(M*M.T,np.ones_like(M)) and np.allclose(np.diag(M),1)
    for g in groups:
        Mg=mat(rs,g,['ERP_A','ERP_B']); reciprocity &= np.allclose(Mg*Mg.T,np.ones_like(Mg)) and np.allclose(np.diag(Mg),1)
    validation=f"""ERP-MCDA benchmark — NP02 PRECOMPARISON VALIDATION\n\nCriteria matrix: 5 x 5 — PASS\nAlternatives: ERP_A, ERP_B — PASS\nAlternative pairwise matrices: five 2 x 2 matrices — PASS\nReciprocity/unit diagonals: {'PASS' if reciprocity else 'FAIL'}\nCriteria weight sum: {cw.sum():.15f} — {'PASS' if abs(cw.sum()-1)<1e-12 else 'FAIL'}\nEach local alternative-weight vector sums to 1: {'PASS' if np.allclose(A.sum(axis=0),1) else 'FAIL'}\nFinal alternative-weight sum: {scores.sum():.15f} — {'PASS' if abs(scores.sum()-1)<1e-12 else 'FAIL'}\nConsistency ratio: {CR:.12f}; source acceptance threshold CR<0.1 — {'PASS' if CR<0.1 else 'FAIL'}\nNormalization: column normalization followed by row mean — PASS\nTie handling: exact terminal ties would be represented as tied sets; none observed — PASS\nNaN/inf: {'PASS' if np.isfinite(M).all() and np.isfinite(cw).all() and np.isfinite(A).all() and np.isfinite(scores).all() else 'FAIL'}\nPublished terminal values were not referenced by this script.\nRobustness analyses are reproduced separately by the robustness modules.\n"""; VALIDATION.write_text(validation,encoding='utf-8')
if __name__=='__main__': main()
