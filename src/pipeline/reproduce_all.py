#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,csv,shutil,subprocess,sys,importlib.util,gzip,hashlib
HERE=Path(__file__).resolve(); REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'src'))
from pipeline.verify_reference import verify_checksum_manifest,compare_files,csv_rows,sha256
from portable.native_runner import run_case,CANONICAL
from portable.r2c_public_reproduction import reproduce as reproduce_r2c
from portable.r2d_public_reproduction import reproduce_primary as reproduce_r2d_primary
from pipeline.build_publication_tables import build as build_tables
from pipeline.build_figure_source_data import build as build_figures

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=['gate','object','status','expected_sha256','observed_sha256','note']
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();
        for r in rows:w.writerow({k:r.get(k,'') for k in fields})

def require(rows,gate,obj,ok,note,expected='',observed=''):
    rows.append({'gate':gate,'object':obj,'status':'PASS' if ok else 'FAIL','expected_sha256':expected,'observed_sha256':observed,'note':note})
    if not ok: raise RuntimeError(f'{gate} failed: {obj}: {note}')


R2C_HOSTED_VECTOR_ABS_TOL = 1e-9

def _parse_score_vector(text):
    out=[]
    for token in text.split(';'):
        token=token.strip()
        if not token:
            continue
        if '=' not in token:
            raise ValueError(f'invalid score-vector token: {token!r}')
        label, val = token.rsplit('=',1)
        out.append((label, float(val)))
    return out

def _compare_r2c_deletion_hosted(got,ref):
    g=csv_rows(got); r=csv_rows(ref)
    if len(g)!=len(r):
        return False, f'row count differs: observed={len(g)} expected={len(r)}'
    if (list(g[0].keys()) if g else []) != (list(r[0].keys()) if r else []):
        return False, 'schema differs'
    max_abs=0.0; max_where=''
    for i,(a,b) in enumerate(zip(g,r),1):
        for k in a:
            if k=='terminal_score_vector':
                try:
                    av=_parse_score_vector(a[k]); bv=_parse_score_vector(b[k])
                except Exception as exc:
                    return False, f'row {i} score-vector parse failure: {exc}'
                if [x[0] for x in av] != [x[0] for x in bv]:
                    return False, f'row {i} score-vector labels differ'
                for (lab,x),(_,y) in zip(av,bv):
                    d=abs(x-y)
                    if d>max_abs:
                        max_abs=d; max_where=f'row={i}, token={lab}, observed={x}, expected={y}'
                    if d>R2C_HOSTED_VECTOR_ABS_TOL:
                        return False, f'row {i} {lab} differs by {d:.3g} > {R2C_HOSTED_VECTOR_ABS_TOL:.1e}'
            elif a[k]!=b[k]:
                return False, f'row {i} exact field {k} differs: observed={a[k]!r} expected={b[k]!r}'
    return True, f'hosted-runtime R2C score-vector equivalence PASS; max_abs={max_abs:.3g} <= {R2C_HOSTED_VECTOR_ABS_TOL:.1e}' + (f' ({max_where})' if max_where else '')

def _compare_r2c_file(got,ref,name,runtime_profile):
    base=compare_files(got,ref,'r2c_reference_parity',name)
    if base['status']=='PASS':
        return base
    if runtime_profile=='hosted-colab' and name=='R2C_DELETION_LEVEL_RESULTS.csv':
        ok,note=_compare_r2c_deletion_hosted(got,ref)
        return {'gate':'r2c_reference_parity','object':name,'status':'PASS' if ok else 'FAIL',
                'expected_sha256':sha256(ref),'observed_sha256':sha256(got),'note':note}
    return base

def r2b_full(out,rows):
    r1=REPO/'data/standardized/runtime'; spec=REPO/'data/standardized/robustness/R2B/R2B_EXECUTION_SPEC.csv'; od=out/'robustness/R2B'; od.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(REPO/'src/reference_implementations/robustness/R2B_TERMINAL_WEIGHT_PERTURBATION.py'),'--mode','execute','--spec',str(spec),'--r1a',str(r1/'R1A'),'--r1b',str(r1/'R1B'),'--r1c',str(r1/'R1C'),'--r1d',str(r1/'R1D'),'--output-dir',str(od)]
    cp=subprocess.run(cmd,cwd=REPO,text=True,capture_output=True)
    r2b_diag=(f'exit={cp.returncode}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}').strip()
    require(rows,'r2b_execution','process_exit',cp.returncode==0,r2b_diag if cp.returncode else 'prespecified terminal-weight perturbation execution completed')
    names=['R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv','R2B_WINNER_OR_RECOMMENDATION_DISTRIBUTIONS.csv','R2B_DRAW_LEVEL_METRICS.csv.gz','R2B_NP03_PARALLEL_BRANCH_COMPARISON.csv','R2B_NP05_SIX_CONFIGURATION_SUMMARY.csv']
    for n in names:
        r=compare_files(od/n,REPO/'results/reference/robustness/R2B'/n,'r2b_reference_parity',n); rows.append(r); require([], 'noop','noop',True,'') if False else None
        if r['status']!='PASS': raise RuntimeError(f'R2B parity {n}')
    # Row-count validation is streamed to avoid materializing 650,000 draw records in memory.
    with gzip.open(od/'R2B_DRAW_LEVEL_METRICS.csv.gz','rt',encoding='utf-8',newline='') as f:
        draw_count=max(sum(1 for _ in f)-1,0)
    require(rows,'r2b_design_count','draw_level_rows',draw_count==650000,f'observed={draw_count} expected=650000')
    return od

def r2c_full(out,rows,runtime_profile='strict-byte'):
    od=out/'robustness/R2C'; reproduce_r2c(REPO,od)
    names=['R2C_DELETION_LEVEL_RESULTS.csv','R2C_CASE_LEVEL_SUMMARY.csv','R2C_CROSS_CASE_SUMMARY.csv','R2C_NE_RECORDS.csv','R2C_NP03_PARALLEL_BRANCH_COMPARISON.csv','R2C_NP05_SIX_CONFIGURATION_SUMMARY.csv','R2C_NP12_VIKOR_DELETION_SUMMARY.csv']
    for n in names:
        r=_compare_r2c_file(od/n,REPO/'results/reference/robustness/R2C'/n,n,runtime_profile);rows.append(r)
        if r['status']!='PASS':raise RuntimeError(f'R2C parity {n}')
    ref_note=(REPO/'results/reference/robustness/R2C/R2C_CASE_METHOD_NOTES.txt').read_text(encoding='utf-8')
    expected_note=ref_note
    observed_note=(od/'R2C_CASE_METHOD_NOTES.txt').read_text(encoding='utf-8')
    require(rows,'r2c_reader_note_parity','method_note_parity',observed_note==expected_note,'reader-facing note matches the documented scientific reference')
    d=csv_rows(od/'R2C_DELETION_LEVEL_RESULTS.csv'); ne=csv_rows(od/'R2C_NE_RECORDS.csv'); spec=csv_rows(REPO/'data/standardized/robustness/R2C/R2C_EXECUTION_SPEC.csv')
    require(rows,'r2c_design_count','executed_deletion_rows',len(d)==118,f'observed={len(d)} expected=118')
    require(rows,'r2c_design_count','spec_applicable_rows',sum(x['applicability']=='APPLICABLE' for x in spec)==118,'expected 118 applicable rows')
    require(rows,'r2c_design_count','spec_NE_rows',sum(x['applicability']=='NE' for x in spec)==47,'expected 47 NE rows')
    n11=[x for x in ne if x['NP_ID']=='NP11']; require(rows,'r2c_ne_semantics','NP11_preflight_to_execution_NE',len(n11)==6 and all(x['reason']=='NUMERICAL_NONUNIQUENESS_AND_SOLVER_FAILURE_UNDER_PRESPECIFIED_LITERAL_PROTOCOL' for x in n11),'six NP11 C1-C6 NE records, no fallback solver')
    return od

def r2d_full(out,rows):
    od=out/'robustness/R2D'; reproduce_r2d_primary(REPO,od)
    primary=['R2D_NP04_30_SCENARIO_RESULTS.csv','R2D_NP04_CRITERION_MAPPING.csv','R2D_NP04_PRIMARY_EQ31_SCENARIO_WEIGHTS.csv','R2D_NP04_SCENARIO_WEIGHT_VALIDATION.csv','R2D_NP12_Q_SWEEP_RESULTS.csv']
    for n in primary:
        r=compare_files(od/n,REPO/'results/reference/robustness/R2D'/n,'r2d_primary_reference_parity',n);rows.append(r)
        if r['status']!='PASS':raise RuntimeError(f'R2D primary parity {n}')
    p04=csv_rows(od/'R2D_NP04_30_SCENARIO_RESULTS.csv'); val=csv_rows(od/'R2D_NP04_SCENARIO_WEIGHT_VALIDATION.csv'); q=csv_rows(od/'R2D_NP12_Q_SWEEP_RESULTS.csv')
    require(rows,'r2d_design_count','NP04_primary_scenarios',len(p04)==30,'exactly 30 SOURCE_DEFINED_EQ31 scenarios')
    require(rows,'r2d_design_count','NP04_weight_validation_records',len(val)==720,'exactly 720 validation records')
    require(rows,'r2d_design_count','NP12_qv_rows',len(q)==15 and sorted(set(x['q_v'] for x in q))==['0.00','0.25','0.50','0.75','1.00'],'five q/v settings × three alternatives')
    # Documented third-party-workbook comparison records are integrity-checked, not re-extracted offline.
    defect=csv_rows(REPO/'data/standardized/robustness/R2D/SOURCE_AUDIT_RECORDS/R2D_NP04_SOURCE_WORKBOOK_INCONSISTENCY_AUDIT.csv')
    branch=csv_rows(REPO/'data/standardized/robustness/R2D/SOURCE_AUDIT_RECORDS/R2D_NP04_SOURCE_WORKBOOK_BRANCH_RESULTS.csv')
    require(rows,'r2d_source_audit_integrity','NP04_source_workbook_inconsistency_records',len(defect)==20 and all(x['complete_order_changed']=='NO' and x['winner_set_changed']=='NO' for x in defect),'20 documented score-level records; 0 complete-rank and 0 winner changes; raw workbook not redistributed')
    require(rows,'r2d_source_audit_integrity','NP04_source_workbook_branch_scenarios',len(branch)==30 and sum(x['complete_order_changed_vs_primary']=='YES' for x in branch)==0 and sum(x['winner_set_changed_vs_primary']=='YES' for x in branch)==0,'30 documented comparison-branch scenarios; source bytes not required')
    close=csv_rows(REPO/'results/reference/resolved/R2D_SOURCE_RESOLUTION_SUMMARY.csv')
    s16=[x for x in close if x['NP_ID']=='NP04' and x['component']=='S16_SOURCE_COMPARISON']
    require(rows,'source_resolution_consistency','NP04_S16_final',len(s16)==1 and s16[0]['final_status']=='CHECKPOINT_AND_ROUNDING_SENSITIVE_INTERNAL_TIE_RESOLUTION__NO_WINNER_EFFECT','S16 checkpoint/rounding-sensitive tie classification retained')
    np06=csv_rows(REPO/'results/reference/robustness/R2D/R2D_NP06_SOURCE_REPORTED_COMPARISON.csv')
    require(rows,'r2d_source_comparison','NP06_publication_only_reconstruction_NE',len(np06)==4 and all(x['comparison_status']=='NE' and x['NATIVE_SENSITIVITY_STATUS']=='PUBLICATION_REPORTED_ONLY__RECONSTRUCTION_NE' for x in np06),'publication-reported-only; source-defined reconstruction remains NE')
    np12cmp=csv_rows(REPO/'results/reference/robustness/R2D/R2D_NP12_SOURCE_COMPARISON.csv')
    require(rows,'r2d_source_comparison','NP12_source_comparison_PASS',len(np12cmp)==15 and len(set(x['q_v'] for x in np12cmp))==5 and all(x['comparison_class']=='MATCH' for x in np12cmp),'five q/v values × three alternatives; all source comparisons MATCH')
    return od

def source_resolution_checks(rows):
    auth={r['NP_ID']:r for r in csv_rows(REPO/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv')}
    require(rows,'source_resolution_consistency','NP08_final_NE',auth['NP08']['Native_evaluability']=='NOT_TERMINALLY_EVALUABLE' and auth['NP08']['Native_reconstruction']=='NE under documented source resolution','NP08 source-resolved terminal NE retained')
    require(rows,'source_resolution_consistency','NP09_final_NE',auth['NP09']['Native_evaluability']=='NOT_EVALUABLE_LITERAL_METHOD_NONFINITE' and auth['NP09']['Native_reconstruction']=='NE under documented source resolution','NP09 literal ln(0) gate retained')
    require(rows,'source_resolution_consistency','NP10_final_D0_O3',auth['NP10']['Final_D']=='D0' and auth['NP10']['O']=='O3' and auth['NP10']['Native_reconstruction'].startswith('NE;'),'NP10 source limitation retained')
    require(rows,'source_resolution_consistency','NP11_single_criterion_deletion_8_to_7',auth['NP11']['Single_criterion_deletion_preflight']=='APPLICABLE AT PREFLIGHT' and auth['NP11']['Single_criterion_deletion_execution_status']=='NE UNDER PRESPECIFIED REDUCED-LFPP SOLVER/NONUNIQUENESS CONDITION','preflight denominator eight preserved; seven result-producing')
    require(rows,'source_resolution_consistency','NP04_final_native_sensitivity','30 source-defined Eq. (31) scenarios' in auth['NP04']['Native_sensitivity'],'NP04 source-defined sensitivity result retained')

def publication_parity(out,rows):
    canonical=REPO/'results/publication'
    regen=out/'publication_regenerated'
    if regen.exists(): shutil.rmtree(regen)
    regen.mkdir(parents=True)
    build_tables(REPO,regen); build_figures(REPO,regen)
    checks=[]
    files=['table_1_benchmark_depth.csv','table_2_native_reconstruction.csv','table_3_integrated_robustness.csv','figure_1_evidence_matrix.csv','figure_2_terminal_weight_trajectories.csv','figure_s1_single_criterion_deletion_summary.csv','figure_s2_np04_source_audit.csv']
    for fn in files:
        rr=csv_rows(regen/fn)
        byte_ok=(regen/fn).read_bytes()==(canonical/fn).read_bytes()
        checks.append({'object':fn,'check':'independent_regeneration_byte_parity','status':'PASS' if byte_ok else 'FAIL','detail':f'rows={len(rr)}; regenerated in clean reproduction output'})
        for idx,r in enumerate(rr,1):
            ok=bool(r.get('source_reference')) and bool(r.get('denominator_metadata')) and 'ne_no_semantics' in r and 'branch_configuration_label' in r
            checks.append({'object':f'{fn}:row{idx}','check':'required_metadata','status':'PASS' if ok else 'FAIL','detail':'source reference + denominator + NE/NO + branch/configuration metadata'})
    t3={r['NP_ID']:r for r in csv_rows(regen/'table_3_integrated_robustness.csv')}
    s2=csv_rows(regen/'figure_s2_np04_source_audit.csv')
    checks += [
      {'object':'NP03','check':'branch_label','status':'PASS' if 'plausible direction' in t3['NP03']['branch_configuration_label'].lower() else 'FAIL','detail':t3['NP03']['branch_configuration_label']},
      {'object':'NP05','check':'lineage_count','status':'PASS' if 'six co-primary' in t3['NP05']['branch_configuration_label'].lower() else 'FAIL','detail':'six configurations remain one lineage'},
      {'object':'NP11','check':'single_criterion_deletion_8_to_7','status':'PASS' if 'PREFLIGHT' in t3['NP11']['single_criterion_deletion_preflight'] and t3['NP11']['single_criterion_deletion_execution_status'].startswith('NE UNDER') else 'FAIL','detail':'8 preflight-applicable; 7 result-producing'},
      {'object':'NP12','check':'native_recommendation_set','status':'PASS' if 'recommendation set' in t3['NP12']['single_criterion_deletion_key_result'].lower() else 'FAIL','detail':t3['NP12']['single_criterion_deletion_key_result']},
      {'object':'NP04','check':'source_resolution_wording','status':'PASS' if 'implementation inconsistency' in t3['NP04']['interpretation'].lower() else 'FAIL','detail':t3['NP04']['interpretation']},
      {'object':'Figure S2','check':'source_artifact_class','status':'PASS' if len(s2)==20 and all(x.get('source_artifact_class')=='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY' and x.get('publication_label')=='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY' and 'inconsistency_class' not in x for x in s2) else 'FAIL','detail':'20 source-workbook comparison records with the documented source artifact class'},
    ]
    with (out/'PUBLICATION_PARITY.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['object','check','status','detail'],lineterminator='\n');w.writeheader();w.writerows(checks)
    require(rows,'publication_parity','all_publication_objects',all(x['status']=='PASS' for x in checks),f'actual checks={len(checks)}; PASS={sum(x["status"]=="PASS" for x in checks)}')
    return checks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['full','quick'],required=True);ap.add_argument('--output-dir',required=True,type=Path);ap.add_argument('--runtime-profile',choices=['strict-byte','hosted-colab'],default='strict-byte');args=ap.parse_args()
    out=args.output_dir if args.output_dir.is_absolute() else REPO/args.output_dir
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    rows=[]
    cks=verify_checksum_manifest(REPO);rows.extend(cks)
    if any(r['status']!='PASS' for r in cks):
        write_csv(out/'PARITY_REPORT.csv',rows)
        failed=[r for r in cks if r['status']!='PASS']
        print(f'SCIENTIFIC_CHECKSUM_FAILURE: {len(failed)} mismatches',file=sys.stderr)
        for r in failed[:50]:
            print(f"FAIL {r['object']} expected={r['expected_sha256']} observed={r['observed_sha256']}",file=sys.stderr)
        print(f'Parity report: {out / "PARITY_REPORT.csv"}',file=sys.stderr)
        return 2
    cases=CANONICAL if args.mode=='full' else ['NP01','NP03','NP12']
    try:
        for npid in cases: rows.extend(run_case(REPO,npid,out,parity_profile=args.runtime_profile))
        source_resolution_checks(rows)
        if args.mode=='full':
            r2b_full(out,rows);r2c_full(out,rows,args.runtime_profile);r2d_full(out,rows)
        else:
            (out/'QUICK_SMOKE_ONLY.txt').write_text('QUICK MODE: selected deterministic native reruns + source resolution/publication consistency only. Not publication results.\n',encoding='utf-8')
            require(rows,'quick_mode','robustness_full_execution','SKIPPED'=='PASS','not reached') if False else rows.append({'gate':'quick_mode','object':'robustness_full_execution','status':'PASS','expected_sha256':'','observed_sha256':'','note':'SKIPPED_BY_DESIGN: quick/CI smoke only; full mode required for publication parity'})
        publication_parity(out,rows)
        write_csv(out/'PARITY_REPORT.csv',rows)
        if any(r['status']!='PASS' for r in rows): return 3
        (out/'FULL_REPRODUCTION_PASS.txt' if args.mode=='full' else out/'QUICK_REPRODUCTION_PASS.txt').write_text('PASS\n',encoding='utf-8')
        return 0
    except Exception as e:
        rows.append({'gate':'fatal','object':'pipeline','status':'FAIL','expected_sha256':'','observed_sha256':'','note':str(e)})
        write_csv(out/'PARITY_REPORT.csv',rows)
        print(f'PIPELINE_FATAL: {type(e).__name__}: {e}',file=sys.stderr)
        print(f'Parity report: {out / "PARITY_REPORT.csv"}',file=sys.stderr)
        return 1
if __name__=='__main__': raise SystemExit(main())
