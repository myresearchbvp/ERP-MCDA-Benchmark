from pathlib import Path
import csv, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from pipeline.build_publication_tables import build as build_tables
from pipeline.build_figure_source_data import build as build_figures

FILES=[
 'table_1_benchmark_depth.csv','table_2_native_reconstruction.csv','table_3_integrated_robustness.csv',
 'figure_1_evidence_matrix.csv','figure_2_terminal_weight_trajectories.csv',
 'figure_s1_single_criterion_deletion_summary.csv','figure_s2_np04_source_audit.csv'
]

def test_publication_objects_regenerate_non_circular(tmp_path):
    out=tmp_path/'publication'; out.mkdir()
    build_tables(R,out); build_figures(R,out)
    for name in FILES:
        assert (out/name).read_bytes()==(R/'results/publication'/name).read_bytes(), name

def test_figure_s2_source_classification_regeneration(tmp_path):
    out=tmp_path/'publication'; out.mkdir()
    build_figures(R,out)
    p=out/'figure_s2_np04_source_audit.csv'
    rows=list(csv.DictReader(p.open(encoding='utf-8-sig')))
    assert len(rows)==20
    assert 'inconsistency_class' not in rows[0]
    assert all(r['source_artifact_class']=='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY' for r in rows)
    assert all(r['publication_label']=='SOURCE_WORKBOOK_IMPLEMENTATION_INCONSISTENCY' for r in rows)
