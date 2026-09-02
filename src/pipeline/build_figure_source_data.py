from __future__ import annotations
from pathlib import Path
import csv

def read(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)

def build(repo:Path,out:Path):
    auth=read(repo/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv')
    # Figure 1 long categorical matrix
    dims=[('terminal_evaluability','Native_evaluability'),('winner_agreement','Native_reconstruction'),('complete_rank_agreement','Native_reconstruction'),('score_agreement','Native_reconstruction'),('terminal_weight_perturbation','Terminal_weight_perturbation'),('single_criterion_deletion_preflight','Single_criterion_deletion_preflight'),('single_criterion_deletion_execution','Single_criterion_deletion_execution_status'),('native_sensitivity','Native_sensitivity')]
    f1=[]
    for r in auth:
        for dim,col in dims:
            if dim=='winner_agreement':
                val='NE' if r['NP_ID'] in {'NP08','NP09','NP10'} else ('YES' if 'Winner YES' in r['Native_reconstruction'] or r['NP_ID'] in {'NP05','NP07','NP11','NP12'} else r['Native_reconstruction'])
            elif dim=='complete_rank_agreement':
                val='NE' if r['NP_ID'] in {'NP08','NP09','NP10'} else ('YES' if 'full rank YES' in r['Native_reconstruction'] or r['NP_ID'] in {'NP05','NP07','NP11','NP12'} else ('NO' if 'full rank NO' in r['Native_reconstruction'] else r['Native_reconstruction']))
            elif dim=='score_agreement':
                if r['NP_ID'] in {'NP08','NP09','NP10'}: val='NE'
                elif r['NP_ID']=='NP05': val='MIXED_2_OF_6_EXACT'
                elif r['NP_ID']=='NP12': val='YES'
                elif 'scores NO' in r['Native_reconstruction']: val='NO'
                else: val=r['Native_reconstruction']
            else: val=r[col]
            f1.append({'NP_ID':r['NP_ID'],'dimension':dim,'categorical_value':val,'source_reference':'INTEGRATED_EVIDENCE_MATRIX','denominator_metadata':'12 lineages; categorical evidence matrix; no ordinal quality score','ne_no_semantics':'NE distinct from NO','branch_configuration_label':'NP05 configurations stay within one lineage; NP03 branches not split into lineages','provenance':'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv'})
    write(out/'figure_1_evidence_matrix.csv',f1)
    # Figure 2 terminal-weight perturbation trajectories
    s=read(repo/'results/reference/robustness/R2B/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv')
    keep={'NP01','NP02','NP03','NP07','NP11','NP12'}
    f2=[]
    for r in s:
        if r['NP_ID'] not in keep: continue
        metric='baseline_recommendation_set_retention_frequency' if r['NP_ID']=='NP12' else 'winner_retention_frequency'
        label=r['configuration_or_branch']
        if r['NP_ID']=='NP03' and label=='ERP04_COST_PARALLEL': label='PROSPECTIVELY_PRESERVED_PLAUSIBLE_DIRECTION'
        f2.append({'NP_ID':r['NP_ID'],'series':label,'delta':r['delta'],'declared_draws':r['draws'],'retention_metric':'native_recommendation_set' if r['NP_ID']=='NP12' else 'baseline_winner','retention_fraction':r[metric],'render_role':'TRAJECTORY','source_reference':'R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY','denominator_metadata':'10,000 draws per delta per listed branch/configuration','ne_no_semantics':'Only lineages applicable to the terminal-weight perturbation analysis have trajectories; absent lineages are not zeros','branch_configuration_label':label,'provenance':'results/reference/robustness/R2B/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv'})
    for d in ['0.05','0.10','0.20','0.30','0.40']:
        f2.append({'NP_ID':'NP05','series':'ALL_SIX_CO_PRIMARY_CONFIGURATIONS','delta':d,'declared_draws':'10000 per configuration','retention_metric':'baseline_winner','retention_fraction':'1.000000000000','render_role':'ANNOTATION_NOT_SIX_IDENTICAL_LINES','source_reference':'R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY','denominator_metadata':'6 co-primary configurations × 10,000 draws per delta; no pooled lineage-wide draw denominator','ne_no_semantics':'not applicable','branch_configuration_label':'six co-primary configurations remain one lineage','provenance':'results/reference/robustness/R2B/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv'})
    write(out/'figure_2_terminal_weight_trajectories.csv',f2)
    # Figure S1 single-criterion deletion descriptive source data: include all cross-case rows and explicit preflight/result denominator metadata
    cross=read(repo/'results/reference/robustness/R2C/R2C_CROSS_CASE_SUMMARY.csv')
    pre={r['NP_ID']:r for r in auth}
    f3=[]
    for r in cross:
        a=pre[r['NP_ID']]
        f3.append({'NP_ID':r['NP_ID'],'single_criterion_deletion_applicability':r['single_criterion_deletion_applicability'],'operation_type':r['operation_type'],'applicable_deletion_count':r['applicable_deletion_count'],'winner_or_recommendation_retention_share':r['winner_or_recommendation_retention_share'],'winner_or_recommendation_critical_deletions':r['winner_or_recommendation_critical_deletions'],'branch_configuration_caveat':r['branch_configuration_caveat'],'preflight_status':a['Single_criterion_deletion_preflight'],'execution_status':a['Single_criterion_deletion_execution_status'],'exact_denominator_publication':a['Single_criterion_deletion_exact_denominator'],'source_reference':'R2C_CROSS_CASE_SUMMARY + INTEGRATED_EVIDENCE_MATRIX','denominator_metadata':'8 lineages preflight-applicable; 7 result-producing; 118 executed deletion rows; 47 NE spec rows','ne_no_semantics':'NE is non-evaluable/not executed, not instability','branch_configuration_label':'NP03 two branches separate; NP05 six configs one lineage with C6 NE; NP11 preflight applicable -> execution NE','provenance':'results/reference/robustness/R2C/R2C_CROSS_CASE_SUMMARY.csv'})
    write(out/'figure_s1_single_criterion_deletion_summary.csv',f3)
    # Figure S2 NP04 source-workbook comparison records
    defect=read(repo/'results/reference/robustness/R2D/R2D_NP04_SOURCE_WORKBOOK_INCONSISTENCY_AUDIT.csv')
    f4=[]
    for r in defect:
        d={k:v for k,v in r.items() if k!='inconsistency_class'}
        d['source_artifact_class']='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY'
        d['publication_label']='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY'
        d['source_reference']='NP04 source-workbook comparison record'
        d['denominator_metadata']='20 inconsistent S21-S30 × MSC/C11 × endpoint records; 720 Eq.(31) validation records overall; 30 primary scenarios'
        d['ne_no_semantics']='not applicable'
        d['branch_configuration_label']='SOURCE_DEFINED_EQ31 primary vs source-workbook audit branch'
        d['provenance']='documented NP04 source-workbook comparison records + results/reference/resolved/R2D_SOURCE_RESOLUTION_SUMMARY.csv'
        f4.append(d)
    write(out/'figure_s2_np04_source_audit.csv',f4)
