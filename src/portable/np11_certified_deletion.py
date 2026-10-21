"""Post hoc NP11 LFPP deletion with exact input checks and saved-proof replay."""
from pathlib import Path
from fractions import Fraction
from functools import cmp_to_key
import argparse,csv,hashlib,importlib.util,json,contextlib,io

def load_engine(repo):
    path=repo/'src/reference_implementations/robustness/NP11_LFPP_CERTIFICATION.py'
    spec=importlib.util.spec_from_file_location('np11_lfpp',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def certified_rank(meta):
    bounds=meta['bounds']['frozen']
    def compare(a,b):
        if a==b:return 0
        left,right=sorted((a,b));item=bounds[left+'-'+right]
        lo=Fraction(item['lower_certificate']['certificate_t_exact'])
        hi=-Fraction(item['negative_upper_certificate']['certificate_t_exact'])
        assert lo>0 or hi<0, (meta['name'],left,right,'ranking not identified')
        sign=-1 if lo>0 else 1
        return sign if a==left else -sign
    return sorted(['S1','S2','S3','S4'],key=cmp_to_key(compare))

def reproduce(repo,out,solve=False):
    repo=repo.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    assert not out.is_relative_to(repo/'data') and not out.is_relative_to(repo/'results/reference')
    m=load_engine(repo)
    identity=json.loads((repo/'data/standardized/robustness/R2C/NP11_INPUT_IDENTITIES.json').read_text())
    for rel,digest in identity.items():assert hashlib.sha256((repo/rel).read_bytes()).hexdigest()==digest,rel
    extracted=list(csv.DictReader((repo/'data/extracted/native/NP11/NP11_EXTRACTION.csv').open()))
    for kind,basis,prefix,values in [('criteria_pairwise','criteria','C',m.SOURCE['criteria_upper'])]+[('alternative_pairwise',c,'S',v) for c,v in m.SOURCE['local_upper'].items()]:
        for item in values:
            r=next(x for x in extracted if (x['kind'],x['basis'],x['row_id'],x['col_id'])==(kind,basis,prefix+str(item['i']+1),prefix+str(item['j']+1)))
            assert all(float(Fraction(v))==float(r[k]) for v,k in zip(item['exact_lmu'].split(),('l','m','u')))
    path=repo/'results/reference/robustness/R2C/NP11/face_certificates.json';cert=json.loads(path.read_text())
    counts=m.verify_saved_certificates(cert)
    assert counts=={'qp':13,'lp':696,'feasible_witnesses':33}
    ns={'__name__':'np11_interval_review','__file__':str(out/'certificate_review.py')}
    exec(compile(m.INDEPENDENT_CERTIFICATE_REVIEW_SOURCE,'np11_interval_review','exec'),ns)
    (out/'source_transcription.json').write_text(json.dumps(m.SOURCE,indent=2))
    ns['IN']=path;ns['OUT']=out
    with contextlib.redirect_stdout(io.StringIO()):ns['main']()
    review=json.loads((out/'certificate_review_results.json').read_text())
    assert review['precision']==180 and review['total_lp_certificate_checks']==1032
    locals_rows=list(csv.DictReader((repo/'results/reference/native/NP11/NP11_CALCULATED_INTERMEDIATES.csv').open()))
    local={c:[Fraction(next(r['value'] for r in locals_rows if (r['stage'],r['basis'],r['item'],r['metric'])==('local_system',c,s,'weight'))) for s in ['S1','S2','S3','S4']] for c in ['C1','C2','C3','C4','C5','C6']}
    for name,meta in cert.items():
        if name=='LOCAL_FACES':continue
        for pair,item in meta['bounds']['frozen'].items():
            if pair=='score_ranges':continue
            a,b=[int(v[1:])-1 for v in pair.split('-')]
            coeff=[local[c][a]-local[c][b] for c in meta['ids']]
            assert list(map(Fraction,item['lower_certificate']['coefficient_exact']))==coeff
            assert list(map(Fraction,item['negative_upper_certificate']['coefficient_exact']))==[-x for x in coeff]
    nonunique=m.verify_score_nonuniqueness(cert,local)
    (out/'score_nonuniqueness_results.json').write_text(json.dumps(nonunique,indent=2))
    baseline=certified_rank(cert['BASELINE']);rows=[]
    for c in ['C1','C2','C3','C4','C5','C6']:
        ranking=certified_rank(cert['DELETE_'+c])
        rows.append({'NP_ID':'NP11','criterion_removed':c,'analysis_origin':'POST_HOC_NP11_EXTENSION','certified_complete_ranking':'>'.join(ranking),'baseline_winner_retained':str(ranking[0]==baseline[0]),'baseline_complete_ranking_retained':str(ranking==baseline),'certificate_model':'DELETE_'+c})
    with (out/'NP11_POST_HOC_SIX_OUTCOMES.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    if solve:
        numerical=m.run_solver_crosschecks(m.SOURCE,repo,out)
        for r in numerical['main']:
            if r['solver'] not in {'CLARABEL','OSQP'}:continue
            assert r['solver_success'] and r['primal_violation']<1e-7 and r['bound_violation']<1e-7
            assert r['frozen_ranking']=='>'.join(certified_rank(cert[r['case']])),r['case']
    summary={'input_hashes_verified':True,'source_triplets_verified':51,'certificate_replay':counts,'independent_interval_precision':180,'independent_lp_checks':1032,'all_primary_coefficients_bound_to_local_inputs':True,'baseline_ranking':'>'.join(baseline),'post_hoc_deletions':6,'winner_retained':sum(r['baseline_winner_retained']=='True' for r in rows),'complete_ranking_retained':sum(r['baseline_complete_ranking_retained']=='True' for r in rows),'fresh_solver_crosschecks':solve,'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    assert summary['winner_retained']==5 and summary['complete_ranking_retained']==3
    (out/'NP11_VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--solve',action='store_true');a=p.parse_args()
    reproduce(Path(__file__).resolve().parents[2],a.output_dir,solve=a.solve)
