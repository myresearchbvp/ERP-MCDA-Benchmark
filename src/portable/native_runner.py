#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, shutil, subprocess, sys, hashlib, math

CANONICAL = ["NP01","NP02","NP03","NP04","NP05","NP06","NP07","NP11","NP12"]
OUTPUTS = {
"NP01":["NP01_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP01_RECONSTRUCTION_VALIDATION.txt"],
"NP02":["NP02_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP02_RECONSTRUCTION_VALIDATION.txt"],
"NP03":["NP03_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP03_RECONSTRUCTION_VALIDATION.txt"],
"NP04":["NP04_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP04_INTERMEDIATES.csv"],
"NP05":["NP05_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP05_INTERMEDIATES.csv"],
"NP06":["NP06_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP06_INTERMEDIATES.csv"],
"NP07":["NP07_COMPUTED_OUTPUTS_PRECOMPARISON.csv"],
"NP11":["NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP11_CALCULATED_INTERMEDIATES.csv","NP11_RECONSTRUCTION_VALIDATION.txt"],
"NP12":["NP12_COMPUTED_OUTPUTS_PRECOMPARISON.csv","NP12_CALCULATED_INTERMEDIATES.csv","NP12_RECONSTRUCTION_VALIDATION.txt"],
}

# NP11 uses the reference LFPP/SLSQP solver. Its documented ranking is stable, but the final
# sub-micro numerical digits can vary with the hosted CPU/OpenBLAS execution backend.
# This tolerance is used ONLY by the explicit hosted-runtime profile. The reference
# route remains byte-for-byte strict for every output.
NP11_HOSTED_ABS_TOL = 1e-6


def sha256(p: Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def _np11_numeric_equivalent(got: Path, ref: Path) -> tuple[bool, str]:
    """Strict-structure + tight-numeric equivalence for hosted NP11 solver outputs.

    No rank, identifier, row-order, metric-label, or schema difference is tolerated.
    Only the printed floating values may differ, and only within NP11_HOSTED_ABS_TOL.
    """
    gf, gr = _read_csv(got)
    rf, rr = _read_csv(ref)
    if gf != rf:
        return False, f'schema differs: observed={gf} expected={rf}'
    if len(gr) != len(rr):
        return False, f'row count differs: observed={len(gr)} expected={len(rr)}'

    if got.name == 'NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv':
        exact = {'system', 'rank'}
        numeric = {'total_global_weight'}
    elif got.name == 'NP11_CALCULATED_INTERMEDIATES.csv':
        exact = {'stage', 'basis', 'item', 'metric'}
        numeric = {'value'}
    else:
        return False, 'hosted numerical-equivalence rule is not defined for this file'

    max_abs = 0.0
    max_where = ''
    for i, (a, b) in enumerate(zip(gr, rr), 1):
        for k in exact:
            if a.get(k) != b.get(k):
                return False, f'row {i} exact field {k} differs: observed={a.get(k)!r} expected={b.get(k)!r}'
        for k in numeric:
            try:
                av, bv = float(a[k]), float(b[k])
            except Exception:
                return False, f'row {i} numeric field {k} is not parseable'
            if not (math.isfinite(av) and math.isfinite(bv)):
                return False, f'row {i} numeric field {k} is non-finite'
            d = abs(av-bv)
            if d > max_abs:
                max_abs = d
                max_where = f'row={i}, field={k}, observed={a[k]}, expected={b[k]}'
            if d > NP11_HOSTED_ABS_TOL:
                return False, (
                    f'row {i} numeric field {k} differs by {d:.3g}, '
                    f'exceeding hosted tolerance {NP11_HOSTED_ABS_TOL:.1e}; '
                    f'observed={a[k]} expected={b[k]}'
                )

    # Explicit scientific invariants for the terminal output. These are redundant with
    # exact rank matching but make the acceptance rule auditable and fail-closed.
    if got.name == 'NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv':
        if [r['system'] for r in gr] != ['S1','S2','S3','S4']:
            return False, 'terminal system order changed'
        observed_ranks = {r['system']: int(r['rank']) for r in gr}
        expected_ranks = {r['system']: int(r['rank']) for r in rr}
        if observed_ranks != expected_ranks:
            return False, f'terminal ranks changed: observed={observed_ranks} expected={expected_ranks}'
        observed_winner = min(observed_ranks, key=observed_ranks.get)
        expected_winner = min(expected_ranks, key=expected_ranks.get)
        if observed_winner != expected_winner:
            return False, f'winner changed: observed={observed_winner} expected={expected_winner}'

    return True, (
        f'hosted-runtime NP11 numerical equivalence PASS; max_abs={max_abs:.3g} '
        f'<= {NP11_HOSTED_ABS_TOL:.1e}' + (f' ({max_where})' if max_where else '')
    )


def _parity_row(npid: str, name: str, got: Path, ref: Path, parity_profile: str) -> dict:
    expected, observed = sha256(ref), sha256(got)
    if expected == observed:
        return {
            'gate':'native_reference_parity','object':f'{npid}/{name}','status':'PASS',
            'expected_sha256':expected,'observed_sha256':observed,
            'note':'byte-identical reference native rerun'
        }
    if parity_profile == 'hosted-colab' and npid == 'NP11' and name in {
        'NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv','NP11_CALCULATED_INTERMEDIATES.csv'
    }:
        ok, note = _np11_numeric_equivalent(got, ref)
        return {
            'gate':'native_reference_parity','object':f'{npid}/{name}','status':'PASS' if ok else 'FAIL',
            'expected_sha256':expected,'observed_sha256':observed,'note':note
        }
    return {
        'gate':'native_reference_parity','object':f'{npid}/{name}','status':'FAIL',
        'expected_sha256':expected,'observed_sha256':observed,
        'note':'byte-identical reference native rerun required by this runtime profile'
    }


def run_case(repo:Path,npid:str,out_root:Path,parity_profile:str='strict-byte')->list[dict]:
    if npid not in CANONICAL:
        raise ValueError(f"{npid} is not a canonical executable terminal baseline")
    if parity_profile not in {'strict-byte','hosted-colab'}:
        raise ValueError(f'unknown parity profile: {parity_profile}')
    work=out_root/'native_work'/npid
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True)
    shutil.copy2(repo/'src/reference_implementations/native'/f'{npid}_RECONSTRUCTION.py',work/f'{npid}_RECONSTRUCTION.py')
    ext=repo/'data/extracted/native'/npid/f'{npid}_EXTRACTION.csv'
    if ext.exists(): shutil.copy2(ext,work/ext.name)
    cpdir=repo/'data/standardized/native'/npid
    if cpdir.exists():
        for p in cpdir.iterdir():
            if p.is_file(): shutil.copy2(p,work/p.name)
    cp=subprocess.run([sys.executable,str(work/f'{npid}_RECONSTRUCTION.py')],cwd=work,text=True,capture_output=True)
    if cp.returncode!=0:
        raise RuntimeError(f'{npid} failed with exit={cp.returncode}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}')
    rows=[]
    refdir=repo/'results/reference/native'/npid
    for name in OUTPUTS[npid]:
        got=work/name; ref=refdir/name
        if not got.exists() or not ref.exists():
            raise FileNotFoundError(f'{npid} missing output/reference {name}')
        row=_parity_row(npid,name,got,ref,parity_profile)
        rows.append(row)
        if row['status']!='PASS':
            raise RuntimeError(
                f'{npid} parity failed for {name}; profile={parity_profile}; '
                f'expected_sha256={row["expected_sha256"]}; observed_sha256={row["observed_sha256"]}; '
                f'diagnostic={row["note"]}'
            )
    finaldir=out_root/'native'/npid; finaldir.mkdir(parents=True,exist_ok=True)
    for name in OUTPUTS[npid]: shutil.copy2(work/name,finaldir/name)
    shutil.rmtree(work)
    work_parent=out_root/'native_work'
    if work_parent.exists() and not any(work_parent.iterdir()):
        work_parent.rmdir()
    return rows
