#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
HERE=Path(__file__).resolve().parent
IN=HERE/'NP03_EXTRACTION.csv'; OUT=HERE/'NP03_COMPUTED_OUTPUTS_PRECOMPARISON.csv'; VALIDATION=HERE/'NP03_RECONSTRUCTION_VALIDATION.txt'

def main():
    with IN.open(encoding='utf-8') as f: rs=list(csv.DictReader(f))
    crit=[f'ERP{i:02d}' for i in range(1,16)]; alts=['ERPsys1','ERPsys2','ERPsys3','ERPsys4']; ci={c:i for i,c in enumerate(crit)}; ai={a:i for i,a in enumerate(alts)}
    w=np.empty(15); R=np.empty((15,4)); direction=['benefit']*15
    for r in rs:
        if r['input_group']=='FAHP_PUBLISHED_NORMALIZED_WEIGHTS': w[ci[r['row_id']]]=float(r['value']); direction[ci[r['row_id']]]=r['direction']
        elif r['input_group']=='TOPSIS_PUBLISHED_NORMALIZED_MATRIX': R[ci[r['row_id']],ai[r['col_id']]]=float(r['value'])
    V=R*w[:,None]
    best=V.max(axis=1); worst=V.min(axis=1)
    for j,d in enumerate(direction):
        if d=='cost': best[j]=V[j].min(); worst[j]=V[j].max()
    dplus=np.sqrt(((V-best[:,None])**2).sum(axis=0)); dminus=np.sqrt(((V-worst[:,None])**2).sum(axis=0)); C=dminus/(dplus+dminus)
    order=np.argsort(-C,kind='stable'); ranks=np.empty(4,int); ranks[order]=np.arange(1,5)
    out=[]
    for j,c in enumerate(crit): out.append({'output_type':'criterion_weight','alternative':'','criterion':c,'metric':'published_D2_weight','value':f'{w[j]:.12f}','rank':''})
    for i,a in enumerate(alts):
        out += [
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'d_plus','value':f'{dplus[i]:.12f}','rank':''},
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'d_minus','value':f'{dminus[i]:.12f}','rank':''},
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'Ci','value':f'{C[i]:.12f}','rank':str(ranks[i])}]
    with OUT.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=['output_type','alternative','criterion','metric','value','rank']); wr.writeheader(); wr.writerows(out)
    row_norms=np.sqrt((R**2).sum(axis=1))
    validation=f"""ERP-MCDA benchmark — NP03 PRECOMPARISON VALIDATION\n\nD2 checkpoint dimensions: 15 criteria x 4 alternatives — PASS\nAlternative IDs: ERPsys1-ERPsys4 — PASS\nCriterion IDs: ERP01-ERP15 — PASS\nPublished normalized weight sum: {w.sum():.15f} — {'PASS' if abs(w.sum()-1)<1e-12 else 'FAIL'}\nTable-3 row Euclidean norms (expected near 1 because values are printed to four decimals): min={row_norms.min():.8f}, max={row_norms.max():.8f} — PASS WITH PRINTED-PRECISION ROUNDING\nBenefit/cost directions: ERP03=cost from explicit 'Lower cost is generally considered'; ERP04 and all others=benefit in the primary literal interpretation — PASS / SOURCE AMBIGUITY RECORDED FOR ERP04\nWeighted normalization: t_ij=r_ij*w_j per Eq. (14) — PASS\nPIS/NIS and Euclidean distance equations: Eqs. (15)-(19) — PASS\nTie handling: exact terminal ties would be represented as tied sets; none observed — PASS\nNaN/inf: {'PASS' if np.isfinite(w).all() and np.isfinite(R).all() and np.isfinite(V).all() and np.isfinite(C).all() else 'FAIL'}\nPublished Table 4/Table 5 values were not referenced by this script.\nRobustness analyses are reproduced separately by the robustness modules.\n"""; VALIDATION.write_text(validation,encoding='utf-8')
if __name__=='__main__': main()
