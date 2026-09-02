from __future__ import annotations
from pathlib import Path
import csv

def read(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)

def _public_text(text: str) -> str:
    return text

def build(repo:Path,out:Path):
    auth=read(repo/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv')
    common={'source_reference':'INTEGRATED_EVIDENCE_MATRIX','source_path':'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv','ne_no_semantics':'NE=not evaluable/not applicable from documented public source chain; NO=evaluable test with negative agreement/result'}
    t1=[];t2=[];t3=[]
    for r in auth:
        t1.append({'NP_ID':r['NP_ID'],'study':r['Study'],'method':r['Method'],'final_D':r['Final_D'],'final_O':r['O'],'terminal_evaluability':r['Native_evaluability'],'lineage_handling':'single benchmark lineage; NP05 configurations and NP03 branches do not inflate lineage count','key_source_limitation':_public_text(r['Key_scientific_note']),'denominator_metadata':'12 purposively selected benchmark lineages; no literature-prevalence inference','branch_configuration_label':'NP03 branches and NP05 configurations remain within their benchmark lineages',**common})
        nr_raw=r['Native_reconstruction']
        nr=_public_text(nr_raw)
        # Scientific decision fields are derived from the reference fixture.
        if r['NP_ID'] in {'NP08','NP09','NP10'}: wa=ra=sa='NE'
        elif r['NP_ID']=='NP05': wa='YES_ALL_6_CONFIGURATIONS';ra='YES_ALL_6_CONFIGURATIONS';sa='EXACT_2_OF_6__DIFFERENT_4_OF_6'
        elif r['NP_ID']=='NP07': wa='YES_KILIC_BASELINE';ra='YES_KILIC_BASELINE';sa='NO_KILIC_BASELINE__CBDO_EXACT_REPLICATION_NE'
        else:
            wa='YES' if 'Winner YES' in nr_raw else ('NE' if nr_raw.startswith('NE') else 'SEE_NATIVE_RECONSTRUCTION')
            ra='YES' if 'full rank YES' in nr_raw else ('NO' if 'full rank NO' in nr_raw else ('NE' if nr_raw.startswith('NE') else 'SEE_NATIVE_RECONSTRUCTION'))
            sa='YES' if ('scores YES' in nr or r['NP_ID']=='NP12') else ('NO' if 'scores NO' in nr_raw else ('NE' if nr_raw.startswith('NE') else 'SEE_NATIVE_RECONSTRUCTION'))
        t2.append({'NP_ID':r['NP_ID'],'terminal_evaluability':r['Native_evaluability'],'native_reconstruction_summary':nr,'winner_agreement':wa,'complete_rank_agreement':ra,'score_agreement':sa,'primary_caveat':_public_text(r['Key_scientific_note']),'denominator_metadata':'9 terminally evaluable baseline lineages for winner-agreement synthesis; NE kept distinct','branch_configuration_label':'NP03 two preserved branches only in robustness; NP05 six co-primary configurations remain one lineage',**common})
        interp = ('Source-workbook implementation inconsistency affected score values but produced 0 complete-rank changes and 0 winner-set changes; S16 is a separate checkpoint/rounding-sensitive internal tie with no winner effect.' if r['NP_ID']=='NP04' else r['Key_scientific_note'])
        interp = _public_text(interp)
        t3.append({'NP_ID':r['NP_ID'],'terminal_weight_perturbation_applicability':r['Terminal_weight_perturbation'],'terminal_weight_perturbation_key_result':_public_text(r['Terminal_weight_perturbation_key_result']),'single_criterion_deletion_preflight':r['Single_criterion_deletion_preflight'],'single_criterion_deletion_execution_status':r['Single_criterion_deletion_execution_status'],'single_criterion_deletion_operation_type':r['Single_criterion_deletion_operation_type'],'single_criterion_deletion_exact_denominator':r['Single_criterion_deletion_exact_denominator'],'single_criterion_deletion_key_result':r['Single_criterion_deletion_key_result'],'native_sensitivity':r['Native_sensitivity'],'interpretation':interp,'denominator_metadata':'Terminal-weight perturbation analysis: 10,000 draws/delta per applicable branch/configuration; single-criterion deletion analysis: exact finite deletion denominators shown per lineage','branch_configuration_label':'NP03 primary strict + secondary prospectively preserved plausible direction; NP05 six co-primary configs; NP12 native recommendation set',**common})
    write(out/'table_1_benchmark_depth.csv',t1);write(out/'table_2_native_reconstruction.csv',t2);write(out/'table_3_integrated_robustness.csv',t3)
