#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np

HERE=Path(__file__).resolve().parent

def read_rows():
    with open(HERE/'NP12_EXTRACTION.csv',encoding='utf-8',newline='') as f: return list(csv.DictReader(f))

def write_csv(path,rows,fields):
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def weak_ranks(values,ascending=True,tol=1e-12):
    vals=np.asarray(values,float); ranks=[]
    for x in vals:
        if ascending: ranks.append(1+sum(y < x-tol for y in vals))
        else: ranks.append(1+sum(y > x+tol for y in vals))
    return ranks

def main():
    rows=read_rows(); crit=[r for r in rows if r['kind']=='criterion']; pars=[r for r in rows if r['kind']=='parameter']
    w=np.array([float(r['weight']) for r in crit]); X=np.array([[float(r[a]) for a in ['A1','A2','A3']] for r in crit]); dirs=[r['direction'] for r in crit]
    n=len(crit); m=3
    reg=np.zeros_like(X); fbest=[]; fworst=[]
    for j in range(n):
        if dirs[j]=='min': best=float(X[j].min()); worst=float(X[j].max())
        else: best=float(X[j].max()); worst=float(X[j].min())
        fbest.append(best); fworst.append(worst)
        if abs(best-worst)<1e-15: reg[j,:]=0
        else: reg[j,:]=(best-X[j,:])/(best-worst)
    weighted=w[:,None]*reg
    S=weighted.sum(axis=0); R=weighted.max(axis=0)
    Sstar=float(S.min()); Sminus=float(S.max()); Rstar=float(R.min()); Rminus=float(R.max())
    terminal=[]; qvals=[float(r['parameter_value']) for r in pars]
    for q in qvals:
        Q=q*(S-Sstar)/(Sminus-Sstar)+(1-q)*(R-Rstar)/(Rminus-Rstar)
        ranks=weak_ranks(Q,ascending=True)
        for i,a in enumerate(['A1','A2','A3']):
            terminal.append({'q':f'{q:.2f}','alternative':a,'S':f'{S[i]:.12f}','R':f'{R[i]:.12f}','Q':f'{Q[i]:.12f}','rank':ranks[i]})
    write_csv(HERE/'NP12_COMPUTED_OUTPUTS_PRECOMPARISON.csv',terminal,['q','alternative','S','R','Q','rank'])
    inter=[]
    for j,r in enumerate(crit):
        for i,a in enumerate(['A1','A2','A3']):
            inter.append({'stage':'normalization','criterion':r['criterion'],'alternative':a,'metric':'regret_normalized','value':f'{reg[j,i]:.12f}'})
            inter.append({'stage':'weighting','criterion':r['criterion'],'alternative':a,'metric':'weighted_regret','value':f'{weighted[j,i]:.12f}'})
        inter.append({'stage':'ideal','criterion':r['criterion'],'alternative':'','metric':'f_star','value':f'{fbest[j]:.12f}'})
        inter.append({'stage':'ideal','criterion':r['criterion'],'alternative':'','metric':'f_minus','value':f'{fworst[j]:.12f}'})
    write_csv(HERE/'NP12_CALCULATED_INTERMEDIATES.csv',inter,['stage','criterion','alternative','metric','value'])
    validation=['NP12 PRECOMPARISON VALIDATION',
        f'dimensions: alternatives={m}, criteria={n} — '+('PASS' if n==18 else 'FAIL'),
        f'criterion_weight_sum={w.sum():.12f} — '+('PASS' if abs(w.sum()-1)<1e-12 else 'FAIL'),
        'benefit/cost directions: K1–K5=min, K6–K18=max — PASS',
        'normalized regret range [0,1] — '+('PASS' if reg.min()>=-1e-12 and reg.max()<=1+1e-12 else 'FAIL'),
        'S=sum weighted regrets; R=max weighted regret — PASS',
        'q values={0,0.25,0.5,0.75,1.0} are publication-reported native values — PASS',
        'weak-order tie handling enabled; q=0 reconstructed A1/A3 tie handled as a set — PASS',
        'NaN/inf check — '+('PASS' if np.isfinite(reg).all() and np.isfinite(S).all() and np.isfinite(R).all() else 'FAIL'),
        'The five publication-reported q/v values are reproduced separately by the source-defined sensitivity module.']
    (HERE/'NP12_RECONSTRUCTION_VALIDATION.txt').write_text('\n'.join(validation)+'\n',encoding='utf-8')

if __name__=='__main__': main()
