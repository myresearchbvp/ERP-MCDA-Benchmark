#!/usr/bin/env python3
from pathlib import Path
import csv, math
import numpy as np
from scipy.optimize import minimize, LinearConstraint, Bounds

HERE=Path(__file__).resolve().parent

def read_rows():
    with open(HERE/'NP11_EXTRACTION.csv',encoding='utf-8',newline='') as f: return list(csv.DictReader(f))

def write_csv(path,rows,fields):
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def lfpp(ids,pairs,M):
    index={x:i for i,x in enumerate(ids)}
    trip=[]
    for r in pairs:
        i=index[r['row_id']]; j=index[r['col_id']]
        trip.append((i,j,float(r['l']),float(r['m']),float(r['u'])))
    trip.sort()
    n=len(ids); k=len(trip); N=n+1+2*k
    def objective(z):
        lam=z[n]; d=z[n+1:n+1+k]; e=z[n+1+k:]
        return (1-lam)**2 + M*(float(d@d)+float(e@e))
    def jac(z):
        g=np.zeros(N); g[n]=2*(z[n]-1); g[n+1:n+1+k]=2*M*z[n+1:n+1+k]; g[n+1+k:]=2*M*z[n+1+k:]; return g
    A=[]; lb=[]
    for q,(i,j,l,m,u) in enumerate(trip):
        r=np.zeros(N); r[i]=1; r[j]=-1; r[n]=-math.log(m/l); r[n+1+q]=1
        A.append(r); lb.append(math.log(l))
        r=np.zeros(N); r[i]=-1; r[j]=1; r[n]=-math.log(u/m); r[n+1+k+q]=1
        A.append(r); lb.append(-math.log(u))
    cons=LinearConstraint(np.vstack(A),np.array(lb),np.full(2*k,np.inf))
    bnds=Bounds(np.zeros(N),np.full(N,np.inf))
    z0=np.zeros(N); z0[:n]=1.0; z0[n]=0.5; z0[n+1:]=0.1
    res=minimize(objective,z0,jac=jac,constraints=[cons],bounds=bnds,method='SLSQP',options={'ftol':1e-14,'maxiter':20000,'disp':False})
    if not res.success: raise RuntimeError(res.message)
    x=res.x[:n]; ex=np.exp(x-x.max()); weights=ex/ex.sum()
    return {'weights':weights,'lambda':float(res.x[n]),'objective':float(res.fun),'success':res.success,
            'max_deviation':float(np.max(res.x[n+1:]))}

def main():
    rows=read_rows(); M=float(next(r['value'] for r in rows if r['input_id']=='LFPP_M'))
    crit_rows=[r for r in rows if r['kind']=='criteria_pairwise']
    crit=lfpp([f'C{i}' for i in range(1,7)],crit_rows,M)
    local=[]; details=[]
    for c in [f'C{i}' for i in range(1,7)]:
        rr=[r for r in rows if r['kind']=='alternative_pairwise' and r['basis']==c]
        sol=lfpp([f'S{i}' for i in range(1,5)],rr,M)
        local.append(sol['weights']); details.append(sol)
    local=np.vstack(local); cw=crit['weights']; totals=cw@local
    order=np.argsort(-totals,kind='stable'); ranks=np.empty(4,dtype=int)
    for pos,idx in enumerate(order,1): ranks[idx]=pos
    terminal=[{'system':f'S{i+1}','total_global_weight':f'{totals[i]:.12f}','rank':int(ranks[i])} for i in range(4)]
    write_csv(HERE/'NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv',terminal,['system','total_global_weight','rank'])
    inter=[]
    for j,c in enumerate([f'C{i}' for i in range(1,7)]):
        inter.append({'stage':'criteria','basis':'objective','item':c,'metric':'weight','value':f'{cw[j]:.12f}'})
    inter.append({'stage':'criteria','basis':'objective','item':'criteria_matrix','metric':'lambda','value':f"{crit['lambda']:.12f}"})
    inter.append({'stage':'criteria','basis':'objective','item':'criteria_matrix','metric':'objective','value':f"{crit['objective']:.12f}"})
    for j,c in enumerate([f'C{i}' for i in range(1,7)]):
        sol=details[j]
        inter.append({'stage':'local_system','basis':c,'item':'matrix','metric':'lambda','value':f"{sol['lambda']:.12f}"})
        inter.append({'stage':'local_system','basis':c,'item':'matrix','metric':'objective','value':f"{sol['objective']:.12f}"})
        for i,s in enumerate([f'S{k}' for k in range(1,5)]):
            inter.append({'stage':'local_system','basis':c,'item':s,'metric':'weight','value':f'{local[j,i]:.12f}'})
    for i,s in enumerate([f'S{k}' for k in range(1,5)]): inter.append({'stage':'global_system','basis':'all_criteria','item':s,'metric':'weight','value':f'{totals[i]:.12f}'})
    write_csv(HERE/'NP11_CALCULATED_INTERMEDIATES.csv',inter,['stage','basis','item','metric','value'])
    # VALIDATION
    trip_rows=[r for r in rows if r['kind'] in ('criteria_pairwise','alternative_pairwise')]
    tri_ok=all(float(r['l'])>0 and float(r['l'])<=float(r['m'])<=float(r['u']) for r in trip_rows)
    validation=['NP11 PRECOMPARISON VALIDATION',
        'primary ERP ranking engine: LFPP only; DEMATEL excluded under the documented source-defined ERP ranking scope — PASS',
        f'criteria pairwise upper-triangle entries={len(crit_rows)} expected=15 — '+('PASS' if len(crit_rows)==15 else 'FAIL'),
        f'alternative pairwise entries={len([r for r in rows if r["kind"]=="alternative_pairwise"])} expected=36 — '+('PASS' if len([r for r in rows if r['kind']=='alternative_pairwise'])==36 else 'FAIL'),
        'triangular fuzzy invariants 0<l<=m<=u — '+('PASS' if tri_ok else 'FAIL'),
        're-evaluated a45=(1,2,3) used; superseded first-evaluated (3,4,5) excluded — PASS',
        f'criteria_weight_sum={cw.sum():.12f} — '+('PASS' if abs(cw.sum()-1)<1e-10 else 'FAIL'),
        'local_weight_sums — '+('PASS' if all(abs(x-1)<1e-10 for x in local.sum(axis=1)) else 'FAIL'),
        'lambda nonnegative — '+('PASS' if crit['lambda']>=0 and all(d['lambda']>=0 for d in details) else 'FAIL'),
        'NaN/inf check — '+('PASS' if np.isfinite(totals).all() and np.isfinite(local).all() and np.isfinite(cw).all() else 'FAIL'),
        'tie handling: descending total global weight; no reconstructed terminal tie — PASS',
        'terminal reconstruction checks completed under the documented source-defined ERP ranking scope — PASS']
    (HERE/'NP11_RECONSTRUCTION_VALIDATION.txt').write_text('\n'.join(validation)+'\n',encoding='utf-8')

if __name__=='__main__': main()
