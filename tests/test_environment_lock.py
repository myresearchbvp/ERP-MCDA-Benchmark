from pathlib import Path
R=Path(__file__).resolve().parents[1]

def test_exact_requirements_lock():
    lines={x.strip() for x in (R/'requirements-lock.txt').read_text().splitlines() if x.strip()}
    assert {'numpy==2.3.5','scipy==1.17.0','pytest==9.0.2'} <= lines

def test_exact_environment_lock():
    text=(R/'environment-lock.yml').read_text()
    for token in ['python=3.13.5','numpy=2.3.5','scipy=1.17.0','pytest=9.0.2']:
        assert token in text
