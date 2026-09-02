#!/usr/bin/env python3
"""ERP-MCDA benchmark R2B — terminal-weight perturbation terminal-weight stress only.

This implementation consumes the prespecified execution specification plus prespecified
native reconstruction artifacts. It performs no single-criterion deletion, no
native sensitivity, no decision-matrix perturbation, and no literature/reconstruction
retuning.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

DELTAS = (0.05, 0.10, 0.20, 0.30, 0.40)
EXPECTED_DRAWS = 10000


def read_csv(path: Path) -> List[dict]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def deterministic_gzip_csv(path: Path, rows: Iterable[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 and filename='' make the gzip container byte-deterministic.
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding='utf-8', newline='') as txt:
                w = csv.DictWriter(txt, fieldnames=fieldnames, lineterminator='\n')
                w.writeheader()
                w.writerows(rows)


def parse_weight_vector(text: str) -> Tuple[List[str], np.ndarray]:
    labels, vals = [], []
    for part in text.split(';'):
        part = part.strip()
        if not part:
            continue
        k, v = part.split('=', 1)
        labels.append(k.strip())
        vals.append(float(v))
    w = np.asarray(vals, dtype=float)
    if not np.all(np.isfinite(w)) or not np.all(w > 0):
        raise ValueError('baseline weights must be finite and strictly positive')
    return labels, w


def normalized(w: np.ndarray) -> np.ndarray:
    s = w.sum(axis=-1, keepdims=True)
    if np.any(s <= 0) or not np.all(np.isfinite(s)):
        raise ValueError('non-positive/non-finite weight sum')
    return w / s


def canonical_set_labels(mask: np.ndarray, alternatives: List[str]) -> np.ndarray:
    """Convert boolean draw x alternative masks to canonical set labels."""
    powers = (1 << np.arange(len(alternatives), dtype=np.int64))
    codes = mask.astype(np.int64) @ powers
    mapping = {}
    for code in np.unique(codes):
        labs = [alternatives[i] for i in range(len(alternatives)) if code & (1 << i)]
        mapping[int(code)] = '|'.join(labs)
    return np.asarray([mapping[int(c)] for c in codes], dtype=object)


def one_order_text(scores: np.ndarray, alternatives: List[str], higher: bool) -> str:
    pref = np.asarray(scores, float) if higher else -np.asarray(scores, float)
    better = np.array([np.sum(pref > pref[i]) for i in range(len(pref))], dtype=int)
    rank = 1 + better
    chunks = []
    for r in sorted(set(rank.tolist())):
        labs = [alternatives[i] for i, rr in enumerate(rank) if rr == r]
        chunks.append(' = '.join(labs))
    return ' > '.join(chunks)


def ranking_metrics(scores: np.ndarray, baseline_scores: np.ndarray, alternatives: List[str], higher: bool) -> dict:
    """Prospectively defined weak-order metrics, with exact floating equality as tie rule."""
    scores = np.asarray(scores, dtype=float)
    baseline_scores = np.asarray(baseline_scores, dtype=float)
    if scores.ndim != 2 or baseline_scores.shape != (scores.shape[1],):
        raise ValueError('bad score dimensions')
    if not np.all(np.isfinite(scores)) or not np.all(np.isfinite(baseline_scores)):
        raise ValueError('non-finite terminal score')
    pref = scores if higher else -scores
    b = baseline_scores if higher else -baseline_scores
    # For each alternative i, count j that is strictly better than i and exactly tied with i.
    better = np.sum(pref[:, None, :] > pref[:, :, None], axis=2)
    equal = np.sum(pref[:, None, :] == pref[:, :, None], axis=2)
    comp_rank = 1 + better
    midrank = 1.0 + better + (equal - 1) / 2.0
    winner_mask = comp_rank == 1
    top2_mask = comp_rank <= 2

    b_better = np.array([np.sum(b > b[i]) for i in range(len(b))], dtype=int)
    b_equal = np.array([np.sum(b == b[i]) for i in range(len(b))], dtype=int)
    b_comp = 1 + b_better
    b_mid = 1.0 + b_better + (b_equal - 1) / 2.0
    b_win = np.flatnonzero(b_comp == 1)
    if len(b_win) != 1:
        raise ValueError('ordinary R2B case baseline winner must be unique')
    b_top2 = np.flatnonzero(b_comp <= 2)
    if len(b_top2) != 2:
        raise ValueError('baseline top-2 must contain exactly two alternatives in R2B applicable cases')

    winner_retained = winner_mask[:, b_win[0]]
    top2_both = np.all(top2_mask[:, b_top2], axis=1)
    top2_overlap = np.sum(top2_mask[:, b_top2], axis=1) / 2.0
    mard = np.mean(np.abs(midrank - b_mid[None, :]), axis=1)

    # Kendall tau-b from pairwise weak-order relations. Handles exact ties without scipy loops.
    ndraw, nalt = pref.shape
    C = np.zeros(ndraw, dtype=float)
    D = np.zeros(ndraw, dtype=float)
    Tx = np.zeros(ndraw, dtype=float)  # baseline tied, perturbation untied
    Ty = np.zeros(ndraw, dtype=float)  # perturbation tied, baseline untied
    for i in range(nalt - 1):
        for j in range(i + 1, nalt):
            br = 1 if b[i] > b[j] else (-1 if b[i] < b[j] else 0)
            pr = np.sign(pref[:, i] - pref[:, j])
            if br == 0:
                Tx += (pr != 0)
            else:
                C += (pr == br)
                D += (pr == -br)
                Ty += (pr == 0)
    denom = np.sqrt((C + D + Tx) * (C + D + Ty))
    tau = np.full(ndraw, np.nan, dtype=float)
    ok = denom > 0
    tau[ok] = (C[ok] - D[ok]) / denom[ok]
    if not np.all(np.isfinite(tau)):
        raise ValueError('undefined Kendall tau-b encountered')

    return {
        'competition_ranks': comp_rank,
        'midranks': midrank,
        'winner_mask': winner_mask,
        'winner_labels': canonical_set_labels(winner_mask, alternatives),
        'top2_mask': top2_mask,
        'winner_retained': winner_retained,
        'top2_both': top2_both,
        'top2_overlap': top2_overlap,
        'mard': mard,
        'tau': tau,
        'baseline_competition_ranks': b_comp,
        'baseline_midranks': b_mid,
        'baseline_winner_index': int(b_win[0]),
        'baseline_top2_indices': b_top2,
    }


class Inputs:
    def __init__(self, r1a: Path, r1b: Path, r1c: Path, r1d: Path):
        self.r1a, self.r1b, self.r1c, self.r1d = r1a, r1b, r1c, r1d
        self._load_np01()
        self._load_np02()
        self._load_np03()
        self._load_np05()
        self._load_np07()
        self._load_np11()
        self._load_np12()

    def _load_np01(self):
        rows = read_csv(self.r1a/'NP01'/'NP01_EXTRACTION.csv')
        alts = ['A','B','C','D']; crit = [f'Cr{i}' for i in range(1,13)]
        X = np.empty((4,12), float); ai={a:i for i,a in enumerate(alts)}; ci={c:i for i,c in enumerate(crit)}
        for r in rows:
            if r['input_group']=='TOPSIS_DECISION': X[ai[r['row_id']],ci[r['col_id']]] = float(r['value'])
        self.np01_R = X / np.sqrt((X**2).sum(axis=0))

    def _load_np02(self):
        rows = read_csv(self.r1a/'NP02'/'NP02_COMPUTED_OUTPUTS_PRECOMPARISON.csv')
        alts=['ERP_A','ERP_B']; crit=['C1_Adaptability','C2_Financial','C3_Simplicity','C4_Provider_services','C5_Implementation_approach']
        A=np.empty((2,5),float); ai={a:i for i,a in enumerate(alts)}; ci={c:i for i,c in enumerate(crit)}
        for r in rows:
            if r['output_type']=='local_alternative_weight': A[ai[r['alternative']],ci[r['criterion']]]=float(r['value'])
        self.np02_local=A

    def _load_np03(self):
        rows=read_csv(self.r1a/'NP03'/'NP03_EXTRACTION.csv')
        crit=[f'ERP{i:02d}' for i in range(1,16)]; alts=['ERPsys1','ERPsys2','ERPsys3','ERPsys4']
        R=np.empty((15,4),float); ci={c:i for i,c in enumerate(crit)}; ai={a:i for i,a in enumerate(alts)}
        for r in rows:
            if r['input_group']=='TOPSIS_PUBLISHED_NORMALIZED_MATRIX': R[ci[r['row_id']],ai[r['col_id']]]=float(r['value'])
        self.np03_R=R

    def _load_np05(self):
        rows=read_csv(self.r1b/'NP05'/'NP05_EXTRACTION.csv')
        scale={}; ratings=defaultdict(list); directions={}
        for r in rows:
            if r['input_group']=='linguistic_scale': scale[r['linguistic_term']]=float(r['value'])
            elif r['input_group']=='linguistic_rating':
                ratings[(r['alternative'],r['criterion'])].append(scale.get(r['linguistic_term'], r['linguistic_term']))
                directions[r['criterion']]=r['direction']
        # The scale rows precede rating rows in the prespecified extraction. Convert any deferred strings defensively.
        for k,vals in list(ratings.items()): ratings[k]=[float(scale[v]) if isinstance(v,str) else float(v) for v in vals]
        self.np05_hfe={k:np.asarray(sorted(set(v)),float) for k,v in ratings.items()}
        if {c for c,d in directions.items() if d=='cost'} != {'C6'}:
            raise ValueError('NP05 expected C6 sole cost criterion')

    def _load_np07(self):
        rows=read_csv(self.r1c/'NP07'/'NP07_EXTRACTION.csv')
        crit=[r['criterion'] for r in rows if r['input_group']=='criterion_weight' and r['publication'].startswith('NP07_Kilic_2015')]
        # preserve extraction order and de-duplicate
        crit=list(dict.fromkeys(crit)); alts=['A','B','C','D','E']
        X=np.empty((5,len(crit)),float); ai={a:i for i,a in enumerate(alts)}; ci={c:i for i,c in enumerate(crit)}
        p=np.empty(len(crit),float)
        for r in rows:
            if not r['publication'].startswith('NP07_Kilic_2015'): continue
            if r['input_group']=='alternative_score': X[ai[r['alternative']],ci[r['criterion']]]=float(r['value'])
            elif r['input_group']=='preference_function': p[ci[r['criterion']]]=float(r['value'])
        P=np.zeros((len(crit),5,5),float)
        for j in range(len(crit)):
            for a in range(5):
                for b in range(5):
                    if a==b: continue
                    d=X[a,j]-X[b,j]
                    P[j,a,b]=0.0 if d<=0 else (d/p[j] if d<p[j] else 1.0)
        self.np07_criteria=crit; self.np07_P=P

    def _load_np11(self):
        rows=read_csv(self.r1d/'NP11'/'NP11_CALCULATED_INTERMEDIATES.csv')
        local=np.empty((6,4),float)
        ci={f'C{i}':i-1 for i in range(1,7)}; si={f'S{i}':i-1 for i in range(1,5)}
        for r in rows:
            if r['stage']=='local_system' and r['metric']=='weight':
                local[ci[r['basis']],si[r['item']]]=float(r['value'])
        self.np11_local=local

    def _load_np12(self):
        rows=read_csv(self.r1d/'NP12'/'NP12_EXTRACTION.csv')
        cr=[r for r in rows if r['kind']=='criterion']; alts=['A1','A2','A3']
        X=np.array([[float(r[a]) for a in alts] for r in cr],float)
        dirs=[r['direction'] for r in cr]
        reg=np.zeros_like(X)
        for j in range(len(cr)):
            if dirs[j]=='min': best=float(X[j].min()); worst=float(X[j].max())
            else: best=float(X[j].max()); worst=float(X[j].min())
            reg[j]=(best-X[j])/(best-worst) if best!=worst else 0.0
        self.np12_reg=reg

    def score_np01(self, W):
        V=self.np01_R[None,:,:]*W[:,None,:]
        pis=V.max(axis=1); nis=V.min(axis=1)
        dp=np.sqrt(((V-pis[:,None,:])**2).sum(axis=2)); dm=np.sqrt(((V-nis[:,None,:])**2).sum(axis=2))
        return dm/(dp+dm)

    def score_np02(self, W):
        return W @ self.np02_local.T

    def score_np03(self, W, erp04_cost: bool):
        V=W[:,:,None]*self.np03_R[None,:,:]
        dirs=np.array(['benefit']*15,dtype=object); dirs[2]='cost'
        if erp04_cost: dirs[3]='cost'
        best=V.max(axis=2); worst=V.min(axis=2)
        cost=np.flatnonzero(dirs=='cost')
        if len(cost):
            best[:,cost]=V[:,cost,:].min(axis=2); worst[:,cost]=V[:,cost,:].max(axis=2)
        dp=np.sqrt(((V-best[:,:,None])**2).sum(axis=1)); dm=np.sqrt(((V-worst[:,:,None])**2).sum(axis=1))
        return dm/(dp+dm)

    def score_np05(self, W):
        # Native downstream from unweighted HFEs: Eq.(4) weighted-HFE -> P-HFE score ->
        # column normalization -> COPRAS benefit/cost sums -> Q -> U%.
        D=W.shape[0]; alts=['A1','A2','A3']; crit=[f'C{i}' for i in range(1,7)]
        sc=np.empty((D,3,6),float)
        for j,c in enumerate(crit):
            exponents=W[:,j,None]
            for i,a in enumerate(alts):
                mu=self.np05_hfe[(a,c)][None,:]
                wh=1.0 - np.power(1.0-mu, exponents)
                den=wh.sum(axis=1)
                sc[:,i,j]=(wh*wh).sum(axis=1)/den
        z=sc/sc.sum(axis=1,keepdims=True)
        sben=z[:,:,:5].sum(axis=2); scost=z[:,:,5]
        mincost=scost.min(axis=1); sumcost=scost.sum(axis=1)
        denom=(mincost[:,None]/scost).sum(axis=1)
        Q=sben + (mincost*sumcost)[:,None]/(scost*denom[:,None])
        U=100.0*Q/Q.max(axis=1,keepdims=True)
        return U

    def score_np07(self, W):
        pi=np.einsum('dj,jab->dab',W,self.np07_P,optimize=True)
        n=pi.shape[1]
        plus=pi.sum(axis=2)/(n-1); minus=pi.sum(axis=1)/(n-1)
        return plus-minus

    def score_np11(self, W):
        return W @ self.np11_local

    def score_np12(self, W):
        weighted=W[:,:,None]*self.np12_reg[None,:,:]
        S=weighted.sum(axis=1); R=weighted.max(axis=1)
        ss=S.min(axis=1); sm=S.max(axis=1); rs=R.min(axis=1); rm=R.max(axis=1)
        if np.any(sm==ss) or np.any(rm==rs):
            raise ValueError('NP12 VIKOR denominator collapsed in an terminal-weight perturbation draw')
        q=0.5
        Q=q*(S-ss[:,None])/(sm-ss)[:,None] + (1-q)*(R-rs[:,None])/(rm-rs)[:,None]
        return Q,S,R


def vikor_recommendation(Q: np.ndarray, S: np.ndarray, R: np.ndarray) -> dict:
    """Source-native VIKOR compromise set at q=0.5, J=3.

    C1: Q(second)-Q(best) >= DQ, DQ=1/(J-1).
    C2: Q-best alternative is also best by S or R.
    If C1 fails, recommend all alternatives with Q-Q(best) < DQ.
    If C1 holds but C2 fails, recommend best and the complete second-Q tier.
    If both hold, recommend the exact Q-best tier (unique whenever C1 holds here).
    """
    D,n=Q.shape; DQ=1.0/(n-1)
    order=np.argsort(Q,axis=1,kind='stable')
    rows=np.arange(D); best_idx=order[:,0]; second_idx=order[:,1]
    qbest=Q[rows,best_idx]; qsecond=Q[rows,second_idx]
    c1=(qsecond-qbest)>=DQ
    smin=S.min(axis=1); rmin=R.min(axis=1)
    c2=(S[rows,best_idx]==smin) | (R[rows,best_idx]==rmin)
    rec=np.zeros_like(Q,dtype=bool)
    both=c1 & c2
    rec[both] = (Q[both] == qbest[both,None])
    c1only=c1 & (~c2)
    if np.any(c1only):
        sec=Q[rows[c1only],second_idx[c1only]]
        rec[c1only]=(Q[c1only]==qbest[c1only,None]) | (Q[c1only]==sec[:,None])
    noc1=~c1
    if np.any(noc1):
        rec[noc1]=(Q[noc1]-qbest[noc1,None]) < DQ
    if np.any(rec.sum(axis=1)<1):
        raise ValueError('empty NP12 VIKOR recommendation set')
    return {'mask':rec,'condition1':c1,'condition2':c2,'DQ':DQ}


def baseline_validation(spec_rows: List[dict], inp: Inputs) -> List[str]:
    notes=[]
    for r in spec_rows:
        labels,w=parse_weight_vector(r['baseline_weight_vector']); W=normalized(w[None,:])
        npid=r['NP_ID']; cfg=r['configuration_or_branch']; alts=r['alternatives'].split('|')
        if npid=='NP01': scores=inp.score_np01(W)[0]
        elif npid=='NP02': scores=inp.score_np02(W)[0]
        elif npid=='NP03': scores=inp.score_np03(W,cfg=='ERP04_COST_PARALLEL')[0]
        elif npid=='NP05': scores=inp.score_np05(W)[0]
        elif npid=='NP07':
            if labels!=inp.np07_criteria: raise ValueError('NP07 weight label/order mismatch vs extraction')
            scores=inp.score_np07(W)[0]
        elif npid=='NP11': scores=inp.score_np11(W)[0]
        elif npid=='NP12':
            Q,S,R=inp.score_np12(W); scores=Q[0]
            rec=vikor_recommendation(Q,S,R)['mask'][0]
            if canonical_set_labels(rec[None,:],alts)[0] != 'A2':
                raise ValueError('NP12 baseline native recommendation set is not A2')
        else: raise ValueError(npid)
        higher=r['score_direction']=='HIGHER_IS_BETTER'
        observed=one_order_text(scores,alts,higher)
        expected=r['baseline_complete_weak_order'].replace('  ',' ')
        if observed!=expected:
            raise ValueError(f'{npid}/{cfg} baseline order mismatch: observed={observed!r} expected={expected!r}')
        notes.append(f'{npid}/{cfg}: baseline order {observed} — PASS')
    return notes


def summarize(npid: str, cfg: str, delta: float, alts: List[str], metrics: dict, baseline_order: str,
              baseline_winner_or_rec: str, np12_extra: dict|None=None) -> dict:
    mard=metrics['mard']; tau=metrics['tau']; top2=metrics['top2_both']; overlap=metrics['top2_overlap']
    row={
        'NP_ID':npid,'configuration_or_branch':cfg,'delta':f'{delta:.2f}','draws':str(len(mard)),
        'baseline_complete_weak_order':baseline_order,
        'baseline_winner_or_recommendation_set':baseline_winner_or_rec,
        'winner_retention_frequency':'',
        'baseline_recommendation_set_retention_frequency':'',
        'baseline_A2_in_recommendation_set_frequency':'',
        'baseline_top2_both_retained_frequency':f'{top2.mean():.12f}',
        'mean_baseline_top2_overlap_share':f'{overlap.mean():.12f}',
        'MARD_mean':f'{mard.mean():.12f}','MARD_median':f'{np.median(mard):.12f}',
        'MARD_max':f'{mard.max():.12f}','MARD_p95':f'{np.quantile(mard,0.95):.12f}',
        'Kendall_tau_b_mean':f'{tau.mean():.12f}','Kendall_tau_b_median':f'{np.median(tau):.12f}',
        'Kendall_tau_b_min':f'{tau.min():.12f}','Kendall_tau_b_p05':f'{np.quantile(tau,0.05):.12f}',
        'TRIVIAL_BY_ALTERNATIVE_COUNT':'YES' if npid=='NP02' else 'NO',
        'interpretation':'stress-test frequency under declared terminal-weight perturbation design; NOT probability ERP is truly best'
    }
    if np12_extra is None:
        row['winner_retention_frequency']=f"{metrics['winner_retained'].mean():.12f}"
    else:
        row['baseline_recommendation_set_retention_frequency']=f"{np12_extra['baseline_rec_retained'].mean():.12f}"
        row['baseline_A2_in_recommendation_set_frequency']=f"{np12_extra['A2_in_rec'].mean():.12f}"
    return row


def add_distribution_rows(out: List[dict], npid: str, cfg: str, delta: float, alternatives: List[str],
                          exact_labels: np.ndarray, member_mask: np.ndarray, exact_type: str, marginal_type: str,
                          note: str=''):
    n=len(exact_labels); counts=Counter(exact_labels.tolist())
    for lab in sorted(counts):
        c=counts[lab]
        out.append({'NP_ID':npid,'configuration_or_branch':cfg,'delta':f'{delta:.2f}',
                    'distribution_type':exact_type,'label':lab,'count':str(c),'frequency':f'{c/n:.12f}','note':note})
    for j,a in enumerate(alternatives):
        c=int(member_mask[:,j].sum())
        out.append({'NP_ID':npid,'configuration_or_branch':cfg,'delta':f'{delta:.2f}',
                    'distribution_type':marginal_type,'label':a,'count':str(c),'frequency':f'{c/n:.12f}','note':note})


def execute(spec_rows: List[dict], inp: Inputs, output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    by_np=defaultdict(list)
    for r in spec_rows: by_np[r['NP_ID']].append(r)
    expected_order=['NP01','NP02','NP03','NP05','NP07','NP11','NP12']
    if list(by_np.keys()) != expected_order:
        raise ValueError(f'spec NP order unexpected: {list(by_np.keys())}')

    summary_rows=[]; dist_rows=[]; draw_rows=[]; np03_rows=[]; np05_rows=[]
    factor_hashes={}

    for npid in expected_order:
        rows=by_np[npid]
        seeds={int(r['seed']) for r in rows}; draws={int(r['draws_per_delta']) for r in rows}
        if len(seeds)!=1 or draws!={EXPECTED_DRAWS}: raise ValueError(f'{npid} seed/draw spec mismatch')
        seed=next(iter(seeds))
        rng=np.random.Generator(np.random.PCG64(seed))
        parsed={r['configuration_or_branch']:parse_weight_vector(r['baseline_weight_vector']) for r in rows}
        ncrit=len(next(iter(parsed.values()))[1])
        if any(len(x[1])!=ncrit for x in parsed.values()): raise ValueError(f'{npid} paired weight lengths differ')
        baseline={}
        for r in rows:
            cfg=r['configuration_or_branch']; w=normalized(parsed[cfg][1][None,:])
            if npid=='NP01': bs=inp.score_np01(w)[0]
            elif npid=='NP02': bs=inp.score_np02(w)[0]
            elif npid=='NP03': bs=inp.score_np03(w,cfg=='ERP04_COST_PARALLEL')[0]
            elif npid=='NP05': bs=inp.score_np05(w)[0]
            elif npid=='NP07': bs=inp.score_np07(w)[0]
            elif npid=='NP11': bs=inp.score_np11(w)[0]
            elif npid=='NP12':
                bq,bs_,br_=inp.score_np12(w); bs=bq[0]
                brec=vikor_recommendation(bq,bs_,br_)['mask'][0]
                baseline['NP12_REC_MASK']=brec
            baseline[cfg]=bs

        for delta in DELTAS:
            # First and only RNG call for this NP/delta. Paired branches/configurations reuse this exact factor matrix.
            epsilon=rng.uniform(-delta,+delta,size=(EXPECTED_DRAWS,ncrit))
            factors=1.0+epsilon
            fh=hashlib.sha256(np.ascontiguousarray(factors).tobytes()).hexdigest()
            factor_hashes[(npid,delta)]=fh
            cfg_results={}
            for r in rows:
                cfg=r['configuration_or_branch']; alts=r['alternatives'].split('|'); higher=r['score_direction']=='HIGHER_IS_BETTER'
                labels,basew=parsed[cfg]
                W=normalized(basew[None,:]*factors)
                if npid=='NP01': scores=inp.score_np01(W); extra=None
                elif npid=='NP02': scores=inp.score_np02(W); extra=None
                elif npid=='NP03': scores=inp.score_np03(W,cfg=='ERP04_COST_PARALLEL'); extra=None
                elif npid=='NP05': scores=inp.score_np05(W); extra=None
                elif npid=='NP07': scores=inp.score_np07(W); extra=None
                elif npid=='NP11': scores=inp.score_np11(W); extra=None
                elif npid=='NP12':
                    scores,S,R=inp.score_np12(W)
                    v=vikor_recommendation(scores,S,R)
                    recmask=v['mask']; reclabels=canonical_set_labels(recmask,alts)
                    brec=baseline['NP12_REC_MASK']
                    rec_retained=np.all(recmask==brec[None,:],axis=1)
                    A2_idx=alts.index('A2'); A2_in=recmask[:,A2_idx]
                    extra={'recmask':recmask,'reclabels':reclabels,'baseline_rec_retained':rec_retained,
                           'A2_in_rec':A2_in,'condition1':v['condition1'],'condition2':v['condition2']}
                else: raise ValueError(npid)
                met=ranking_metrics(scores,baseline[cfg],alts,higher)
                cfg_results[cfg]={'scores':scores,'metrics':met,'extra':extra,'spec':r}
                bwr='A2' if npid=='NP12' else r['baseline_winner']
                summary_rows.append(summarize(npid,cfg,delta,alts,met,r['baseline_complete_weak_order'],bwr,extra))

                if npid!='NP12':
                    add_distribution_rows(dist_rows,npid,cfg,delta,alts,met['winner_labels'],met['winner_mask'],
                                          'EXACT_WINNER_SET','MARGINAL_TOP_RANK_MEMBERSHIP')
                else:
                    add_distribution_rows(dist_rows,npid,cfg,delta,alts,extra['reclabels'],extra['recmask'],
                                          'EXACT_NATIVE_RECOMMENDATION_SET','MARGINAL_RECOMMENDATION_MEMBERSHIP',
                                          'PRIMARY native VIKOR compromise recommendation set')
                    add_distribution_rows(dist_rows,npid,cfg,delta,alts,met['winner_labels'],met['winner_mask'],
                                          'TOP_Q_LEADER_SET_SECONDARY','MARGINAL_TOP_Q_LEADER_MEMBERSHIP_SECONDARY',
                                          'SECONDARY diagnostic only; not equivalent to native VIKOR recommendation set')

                # Draw-level rows; draw index is 1-based and perturbation vectors are regenerable from seed/spec/code.
                for i in range(EXPECTED_DRAWS):
                    if npid=='NP12':
                        winner_or_rec=extra['reclabels'][i]; bwin=''; brec='TRUE' if extra['baseline_rec_retained'][i] else 'FALSE'
                        a2='TRUE' if extra['A2_in_rec'][i] else 'FALSE'; topq=met['winner_labels'][i]
                    else:
                        winner_or_rec=met['winner_labels'][i]; bwin='TRUE' if met['winner_retained'][i] else 'FALSE'
                        brec=''; a2=''; topq=''
                    draw_rows.append({
                        'NP_ID':npid,'configuration_or_branch':cfg,'delta':f'{delta:.2f}','draw_index':str(i+1),
                        'winner_or_recommendation_set':winner_or_rec,
                        'baseline_winner_retained':bwin,
                        'baseline_recommendation_set_retained':brec,
                        'baseline_A2_in_recommendation_set':a2,
                        'top_Q_leader_set_secondary':topq,
                        'baseline_top2_both_retained':'TRUE' if met['top2_both'][i] else 'FALSE',
                        'baseline_top2_overlap_share':f"{met['top2_overlap'][i]:.1f}",
                        'MARD':f"{met['mard'][i]:.12f}",
                        'Kendall_tau_b':f"{met['tau'][i]:.12f}"
                    })

            if npid=='NP03':
                p=cfg_results['A_STRICT_EXPLICIT_DIRECTION']; a=cfg_results['ERP04_COST_PARALLEL']
                pm=p['metrics']; am=a['metrics']
                same_winner=(pm['winner_labels']==am['winner_labels'])
                same_order=np.all(pm['midranks']==am['midranks'],axis=1)
                np03_rows.append({
                    'delta':f'{delta:.2f}','paired_draws':str(EXPECTED_DRAWS),'paired_factor_sha256':fh,
                    'primary_winner_retention_frequency':f"{pm['winner_retained'].mean():.12f}",
                    'ERP04_cost_winner_retention_frequency':f"{am['winner_retained'].mean():.12f}",
                    'identical_exact_winner_set_frequency':f'{same_winner.mean():.12f}',
                    'identical_complete_weak_order_frequency':f'{same_order.mean():.12f}',
                    'primary_MARD_mean':f"{pm['mard'].mean():.12f}",'ERP04_cost_MARD_mean':f"{am['mard'].mean():.12f}",
                    'primary_Kendall_tau_b_mean':f"{pm['tau'].mean():.12f}",'ERP04_cost_Kendall_tau_b_mean':f"{am['tau'].mean():.12f}",
                    'rule':'descriptive paired branch comparison only; branches are not pooled or selected by outcome'
                })
            if npid=='NP05':
                metric_extract={
                    'winner_retention_frequency':lambda z: z['winner_retained'].mean(),
                    'baseline_top2_both_retained_frequency':lambda z: z['top2_both'].mean(),
                    'mean_baseline_top2_overlap_share':lambda z: z['top2_overlap'].mean(),
                    'MARD_mean':lambda z: z['mard'].mean(),
                    'Kendall_tau_b_mean':lambda z: z['tau'].mean(),
                }
                for mname,fn in metric_extract.items():
                    vals=[]
                    for r in rows:
                        cfg=r['configuration_or_branch']; val=float(fn(cfg_results[cfg]['metrics'])); vals.append(val)
                        np05_rows.append({'delta':f'{delta:.2f}','row_type':'CONFIGURATION','configuration':cfg,'metric':mname,
                                          'value':f'{val:.12f}','lineage_min':'','lineage_median':'','lineage_max':'',
                                          'paired_factor_sha256':fh,'note':'co-primary configuration; do not interpret as independent draw pool'})
                    np05_rows.append({'delta':f'{delta:.2f}','row_type':'LINEAGE_DESCRIPTIVE_RANGE_MEDIAN','configuration':'ALL_SIX_CO_PRIMARY',
                                      'metric':mname,'value':'','lineage_min':f'{min(vals):.12f}','lineage_median':f'{np.median(vals):.12f}',
                                      'lineage_max':f'{max(vals):.12f}','paired_factor_sha256':fh,
                                      'note':'descriptive across six co-primary configurations only; no pooled-draw inference and no most-stable selection'})

    # Exact expected draw count: 13 configurations/branches x 5 deltas x 10,000.
    if len(draw_rows) != 13*5*EXPECTED_DRAWS:
        raise ValueError(f'draw-level row count {len(draw_rows)} != 650000')

    summary_fields=['NP_ID','configuration_or_branch','delta','draws','baseline_complete_weak_order','baseline_winner_or_recommendation_set',
        'winner_retention_frequency','baseline_recommendation_set_retention_frequency','baseline_A2_in_recommendation_set_frequency',
        'baseline_top2_both_retained_frequency','mean_baseline_top2_overlap_share','MARD_mean','MARD_median','MARD_max','MARD_p95',
        'Kendall_tau_b_mean','Kendall_tau_b_median','Kendall_tau_b_min','Kendall_tau_b_p05','TRIVIAL_BY_ALTERNATIVE_COUNT','interpretation']
    dist_fields=['NP_ID','configuration_or_branch','delta','distribution_type','label','count','frequency','note']
    draw_fields=['NP_ID','configuration_or_branch','delta','draw_index','winner_or_recommendation_set','baseline_winner_retained',
        'baseline_recommendation_set_retained','baseline_A2_in_recommendation_set','top_Q_leader_set_secondary',
        'baseline_top2_both_retained','baseline_top2_overlap_share','MARD','Kendall_tau_b']
    np03_fields=['delta','paired_draws','paired_factor_sha256','primary_winner_retention_frequency','ERP04_cost_winner_retention_frequency',
        'identical_exact_winner_set_frequency','identical_complete_weak_order_frequency','primary_MARD_mean','ERP04_cost_MARD_mean',
        'primary_Kendall_tau_b_mean','ERP04_cost_Kendall_tau_b_mean','rule']
    np05_fields=['delta','row_type','configuration','metric','value','lineage_min','lineage_median','lineage_max','paired_factor_sha256','note']
    write_csv(output_dir/'R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv',summary_rows,summary_fields)
    write_csv(output_dir/'R2B_WINNER_OR_RECOMMENDATION_DISTRIBUTIONS.csv',dist_rows,dist_fields)
    deterministic_gzip_csv(output_dir/'R2B_DRAW_LEVEL_METRICS.csv.gz',draw_rows,draw_fields)
    write_csv(output_dir/'R2B_NP03_PARALLEL_BRANCH_COMPARISON.csv',np03_rows,np03_fields)
    write_csv(output_dir/'R2B_NP05_SIX_CONFIGURATION_SUMMARY.csv',np05_rows,np05_fields)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['baseline-validation','execute'],required=True)
    ap.add_argument('--spec',type=Path,required=True)
    ap.add_argument('--r1a',type=Path,required=True); ap.add_argument('--r1b',type=Path,required=True)
    ap.add_argument('--r1c',type=Path,required=True); ap.add_argument('--r1d',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path)
    args=ap.parse_args()
    spec=read_csv(args.spec)
    if len(spec)!=13: raise ValueError(f'execution spec must contain exactly 13 applicable configuration/branch rows; got {len(spec)}')
    inp=Inputs(args.r1a,args.r1b,args.r1c,args.r1d)
    notes=baseline_validation(spec,inp)
    if args.mode=='baseline-validation':
        print('\n'.join(notes)); print('NO RNG INSTANTIATED; NO PERTURBATION DRAW GENERATED.')
        return
    if args.output_dir is None: raise ValueError('--output-dir is required in execute mode')
    # RNGs are instantiated only inside execute(), after all baseline/spec checks above have passed.
    execute(spec,inp,args.output_dir)

if __name__=='__main__':
    main()
