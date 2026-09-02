from pathlib import Path
import csv,gzip
R=Path(__file__).resolve().parents[1]

def read(rel):
    with (R/rel).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def evidence_matrix(): return {r['NP_ID']:r for r in read('results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv')}

def test_benchmark_native_denominators_and_terminal_ne():
    a=evidence_matrix(); assert len(a)==12 and set(a)=={f'NP{i:02d}' for i in range(1,13)}
    non_eval={'NP08','NP09','NP10'}; evaluable=[n for n in a if n not in non_eval]
    assert len(evaluable)==9
    def winner_yes(n):
        t=a[n]['Native_reconstruction']; return ('Winner YES' in t) or t.startswith('All 6 configurations: winner/rank YES') or t.startswith('Kılıç: winner/rank YES')
    def rank_yes(n):
        t=a[n]['Native_reconstruction']; return ('full rank YES' in t) or t.startswith('All 6 configurations: winner/rank YES') or t.startswith('Kılıç: winner/rank YES')
    assert sum(winner_yes(n) for n in evaluable)==9
    assert sum(rank_yes(n) for n in evaluable)==8
    assert a['NP08']['Native_reconstruction']=='NE under documented source resolution'
    assert a['NP09']['Native_reconstruction']=='NE under documented source resolution'
    assert (a['NP10']['Final_D'],a['NP10']['O'])==('D0','O3')
    d10=read('results/reference/resolved/NP10_D_O_SOURCE_RESOLUTION.csv')
    assert len(d10)==1 and d10[0]['unique_terminal_chain']=='NO'

def test_terminal_weight_perturbation_reference_and_lineage_semantics():
    with gzip.open(R/'results/reference/robustness/R2B/R2B_DRAW_LEVEL_METRICS.csv.gz','rt',encoding='utf-8',newline='') as f:
        assert sum(1 for _ in f)-1==650000
    a=evidence_matrix(); applicable={n for n,r in a.items() if r['Terminal_weight_perturbation'].startswith('APPLICABLE')}
    assert applicable=={'NP01','NP02','NP03','NP05','NP07','NP11','NP12'}
    summary=read('results/reference/robustness/R2B/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv')
    labels={r['configuration_or_branch'] for r in summary if r['NP_ID']=='NP03'}
    assert labels=={'A_STRICT_EXPLICIT_DIRECTION','ERP04_COST_PARALLEL'}
    paired=read('results/reference/robustness/R2B/R2B_NP03_PARALLEL_BRANCH_COMPARISON.csv')
    assert paired and all(r['paired_draws']=='10000' and r['paired_factor_sha256'] for r in paired)
    np05=read('results/reference/robustness/R2B/R2B_NP05_SIX_CONFIGURATION_SUMMARY.csv')
    configs={r['configuration'] for r in np05 if r['row_type']=='CONFIGURATION'}
    assert len(configs)==6
    assert sum(1 for n in applicable if n=='NP05')==1

def test_single_criterion_deletion_exact_denominators_and_ne_semantics():
    a=evidence_matrix(); pre={n for n,r in a.items() if r['Single_criterion_deletion_preflight'].startswith('APPLICABLE')}
    result={n for n,r in a.items() if r['Single_criterion_deletion_execution_status'].startswith('RESULT-PRODUCING')}
    assert len(pre)==8 and len(result)==7 and 'NP11' in pre and 'NP11' not in result
    spec=read('data/standardized/robustness/R2C/R2C_EXECUTION_SPEC.csv')
    assert sum(r['applicability']=='APPLICABLE' for r in spec)==118
    assert sum(r['applicability']=='NE' for r in spec)==47
    assert a['NP11']['Single_criterion_deletion_preflight']=='APPLICABLE AT PREFLIGHT'
    assert a['NP11']['Single_criterion_deletion_execution_status'].startswith('NE UNDER')
    np05=[r for r in spec if r['NP_ID']=='NP05' and r.get('deleted_criterion')=='C6']
    assert len(np05)==6 and all(r['applicability']=='NE' for r in np05)

def test_r2d_np04_exact_scenarios_audit_and_s16():
    p04=read('results/reference/robustness/R2D/R2D_NP04_30_SCENARIO_RESULTS.csv')
    assert len({r['scenario_id'] for r in p04})==30
    assert {r['implementation_branch'] for r in p04}=={'SOURCE_DEFINED_EQ31'}
    audit=read('results/reference/robustness/R2D/R2D_NP04_SOURCE_WORKBOOK_INCONSISTENCY_AUDIT.csv')
    assert len(audit)==20
    assert sum(r['complete_order_changed']=='YES' for r in audit)==0
    assert sum(r['winner_set_changed']=='YES' for r in audit)==0
    close=read('results/reference/resolved/R2D_SOURCE_RESOLUTION_SUMMARY.csv')
    s16=[r for r in close if r['NP_ID']=='NP04' and r['component']=='S16_SOURCE_COMPARISON']
    assert len(s16)==1
    assert s16[0]['final_status']=='CHECKPOINT_AND_ROUNDING_SENSITIVE_INTERNAL_TIE_RESOLUTION__NO_WINNER_EFFECT'

def test_r2d_np06_and_np12_source_comparison():
    np06=read('results/reference/robustness/R2D/R2D_NP06_SOURCE_REPORTED_COMPARISON.csv')
    assert len(np06)==4
    assert all(r['comparison_status']=='NE' and r['NATIVE_SENSITIVITY_STATUS']=='PUBLICATION_REPORTED_ONLY__RECONSTRUCTION_NE' for r in np06)
    q=read('results/reference/robustness/R2D/R2D_NP12_Q_SWEEP_RESULTS.csv')
    assert sorted({r['q_v'] for r in q})==['0.00','0.25','0.50','0.75','1.00']
    cmp=read('results/reference/robustness/R2D/R2D_NP12_SOURCE_COMPARISON.csv')
    assert len(cmp)==15 and sorted({r['q_v'] for r in cmp})==['0.00','0.25','0.50','0.75','1.00']
    assert all(r['comparison_class']=='MATCH' for r in cmp)
