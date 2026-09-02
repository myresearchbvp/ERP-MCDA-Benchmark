from pathlib import Path
R=Path(__file__).resolve().parents[1]

def test_single_criterion_method_note_semantics():
    text=(R/'results/reference/robustness/R2C/R2C_CASE_METHOD_NOTES.txt').read_text(encoding='utf-8')
    assert 'Total executed deletion-outcome rows=118' in text
    assert 'deterministic single-criterion deletion' in text
    assert 'prespecified execution rule' in text
