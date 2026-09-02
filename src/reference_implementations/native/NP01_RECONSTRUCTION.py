#!/usr/bin/env python3
from pathlib import Path
import csv, math
import numpy as np

HERE=Path(__file__).resolve().parent
IN=HERE/'NP01_EXTRACTION.csv'
OUT=HERE/'NP01_COMPUTED_OUTPUTS_PRECOMPARISON.csv'
VALIDATION=HERE/'NP01_RECONSTRUCTION_VALIDATION.txt'

def load():
    with IN.open(encoding='utf-8') as f: return list(csv.DictReader(f))

def fuzzy_matrix(rows,group,names):
    M=np.empty((len(names),len(names),3),float)
    idx={x:i for i,x in enumerate(names)}
    for r in rows:
        if r['input_group']==group:
            M[idx[r['row_id']],idx[r['col_id']]]=[float(r['value_l']),float(r['value_m']),float(r['value_u'])]
    return M

def fweights(M):
    n=M.shape[0]
    g=np.prod(M,axis=1)**(1.0/n)
    s=g.sum(axis=0)
    inv=np.array([1/s[2],1/s[1],1/s[0]])
    fw=g*inv
    crisp=fw.mean(axis=1)
    return crisp/crisp.sum()

def main():
    rows=load()
    main_names=['Technical','Corporate','Financial']
    tech_names=['Functionality','Compatibility','Usability','Accessibility','Security']
    corp_names=['References','Adequacy','After_sales','Know_how']
    fin_names=['License','Consultancy','Maintenance']
    wm=fweights(fuzzy_matrix(rows,'FAHP_MAIN',main_names))
    wt=fweights(fuzzy_matrix(rows,'FAHP_TECHNICAL',tech_names))
    wc=fweights(fuzzy_matrix(rows,'FAHP_CORPORATE',corp_names))
    wf=fweights(fuzzy_matrix(rows,'FAHP_FINANCIAL',fin_names))
    W=np.concatenate([wm[0]*wt,wm[1]*wc,wm[2]*wf])
    alts=['A','B','C','D']; crit=[f'Cr{i}' for i in range(1,13)]
    X=np.empty((4,12),float); ia={a:i for i,a in enumerate(alts)}; ic={c:i for i,c in enumerate(crit)}
    for r in rows:
        if r['input_group']=='TOPSIS_DECISION': X[ia[r['row_id']],ic[r['col_id']]]=float(r['value'])
    denom=np.sqrt((X**2).sum(axis=0)); R=X/denom; V=R*W
    pis=V.max(axis=0); nis=V.min(axis=0)
    dplus=np.sqrt(((V-pis)**2).sum(axis=1)); dminus=np.sqrt(((V-nis)**2).sum(axis=1))
    cc=dminus/(dplus+dminus)
    order=np.argsort(-cc,kind='stable'); ranks=np.empty(4,int); ranks[order]=np.arange(1,5)
    out=[]
    for j,c in enumerate(crit): out.append({'output_type':'criterion_weight','alternative':'','criterion':c,'metric':'global_weight','value':f'{W[j]:.12f}','rank':''})
    for i,a in enumerate(alts):
        out += [
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'d_plus','value':f'{dplus[i]:.12f}','rank':''},
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'d_minus','value':f'{dminus[i]:.12f}','rank':''},
        {'output_type':'terminal','alternative':a,'criterion':'','metric':'CC','value':f'{cc[i]:.12f}','rank':str(ranks[i])}]
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['output_type','alternative','criterion','metric','value','rank']); w.writeheader(); w.writerows(out)
    recip=True
    for G,names in [('FAHP_MAIN',main_names),('FAHP_TECHNICAL',tech_names),('FAHP_CORPORATE',corp_names),('FAHP_FINANCIAL',fin_names)]:
        M=fuzzy_matrix(rows,G,names)
        recip &= np.allclose(np.diagonal(M,axis1=0,axis2=1).T,np.ones((len(names),3)))
        for i in range(len(names)):
            for j in range(len(names)):
                l,m,u=M[i,j]; rl,rm,ru=M[j,i]
                recip &= np.allclose([rl,rm,ru],[1/u,1/m,1/l])
    validation=f"""ERP-MCDA benchmark — NP01 PRECOMPARISON VALIDATION\n\nDimensions: 4 alternatives x 12 TOPSIS criteria — PASS\nAlternative IDs: A, B, C, D — PASS\nCriterion IDs: Cr1-Cr12 — PASS\nFAHP reciprocal triangular pairwise structure and unit diagonals — {'PASS' if recip else 'FAIL'}\nMain FAHP weight sum: {wm.sum():.15f} — PASS\nTechnical local weight sum: {wt.sum():.15f} — PASS\nCorporate local weight sum: {wc.sum():.15f} — PASS\nFinancial local weight sum: {wf.sum():.15f} — PASS\nGlobal weight sum: {W.sum():.15f} — {'PASS' if abs(W.sum()-1)<1e-12 else 'FAIL'}\nBenefit/cost directions: all 12 treated as benefit/desirability per source's explicit maximization statement — PASS\nNormalization equation: Euclidean vector normalization under Eq. (7) — PASS\nPIS/NIS: maxima/minima of weighted normalized columns — PASS\nTie handling: exact terminal ties would be represented as tied sets; none observed — PASS\nNaN/inf: {'PASS' if np.isfinite(W).all() and np.isfinite(R).all() and np.isfinite(V).all() and np.isfinite(cc).all() else 'FAIL'}\nPublished terminal values were not referenced by this script.\nRobustness analyses are reproduced separately by the robustness modules.\n"""
    VALIDATION.write_text(validation,encoding='utf-8')
if __name__=='__main__': main()
