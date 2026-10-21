from pathlib import Path
import csv,copy,json,sys
import pytest

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from portable.np11_certified_deletion import certified_rank,reproduce

def read(path):return list(csv.DictReader(path.open()))

def test_all_six_certified_rankings_and_distinct_provenance():
    cert=json.loads((R/'results/reference/robustness/R2C/NP11/face_certificates.json').read_text())
    actual=['>'.join(certified_rank(cert['DELETE_C'+str(i)])) for i in range(1,7)]
    assert actual==['S4>S3>S1>S2','S4>S1>S3>S2','S4>S3>S1>S2','S4>S3>S2>S1','S4>S3>S1>S2','S3>S1>S2>S4']
    rows=read(R/'results/reference/robustness/R2C/R2C_DELETION_LEVEL_RESULTS.csv')
    original=read(R/'results/reference/robustness/R2C/historical/R2C_DELETION_LEVEL_RESULTS.csv')
    assert len(rows)==124 and len(original)==118
    for old,new in zip(original,rows[:118]):
        assert all(new[k]==v for k,v in old.items())
        assert new['analysis_origin']=='ORIGINAL_BENCHMARK'
    n11=[r for r in rows if r['NP_ID']=='NP11']
    assert len(n11)==6 and all(r['analysis_origin']=='POST_HOC_NP11_EXTENSION' for r in n11)
    assert sum(r['baseline_winner_retained']=='YES' for r in n11)==5
    assert sum(r['baseline_complete_ranking_retained']=='True' for r in n11)==3
    assert not any(r['NP_ID']=='NP11' for r in read(R/'results/reference/robustness/R2C/R2C_NE_RECORDS.csv'))
    assert len([r for r in read(R/'results/reference/robustness/R2C/historical/R2C_NE_RECORDS.csv') if r['NP_ID']=='NP11'])==6

def test_unidentified_contrast_is_rejected():
    cert=json.loads((R/'results/reference/robustness/R2C/NP11/face_certificates.json').read_text())
    meta=copy.deepcopy(cert['DELETE_C6'])
    for pair,bound in meta['bounds']['frozen'].items():
        if pair=='score_ranges':continue
        bound['lower_certificate']['certificate_t_exact']='0'
        bound['negative_upper_certificate']['certificate_t_exact']='0'
    with pytest.raises(AssertionError,match='ranking not identified'):certified_rank(meta)

def test_changed_scientific_input_is_rejected_before_certificate_replay(tmp_path):
    fake=tmp_path/'repo';identity=fake/'data/standardized/robustness/R2C/NP11_INPUT_IDENTITIES.json';identity.parent.mkdir(parents=True)
    (fake/'src/reference_implementations/robustness').mkdir(parents=True)
    import shutil
    shutil.copy2(R/'src/reference_implementations/robustness/NP11_LFPP_CERTIFICATION.py',fake/'src/reference_implementations/robustness/NP11_LFPP_CERTIFICATION.py')
    p=fake/'data/input.csv';p.write_text('tampered input')
    identity.write_text(json.dumps({'data/input.csv':'0'*64}))
    with pytest.raises(AssertionError,match='data/input.csv'):reproduce(fake,tmp_path/'out')
