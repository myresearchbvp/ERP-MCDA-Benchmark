#!/usr/bin/env python3
"""Google Colab runtime adapter for the ERP-MCDA benchmark repository.

This module changes only runtime provisioning, hosted-runtime parity plumbing, and diagnostics.
Scientific computation is still performed by the reference scientific implementations. The Colab route uses
narrowly scoped numerical-equivalence gates for hardware-sensitive printed floating outputs only;
all scientific structure/ranks/winners and all other reference gates remain strict.
"""
from __future__ import annotations

from pathlib import Path
import csv
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request

CANONICAL_PYTHON = (3, 13, 5)
CANONICAL_PYTHON_TEXT = "3.13.5"
MICROMAMBA_URL = "https://micro.mamba.pm/api/micromamba/linux-64/latest"


def _print(msg: str) -> None:
    print(msg, flush=True)


def _run_streaming(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None,
                   label: str = "command") -> tuple[int, list[str]]:
    """Run a subprocess while streaming combined stdout/stderr and retaining a diagnostic tail."""
    _print(f"[{label}] $ {' '.join(str(x) for x in cmd)}")
    proc = subprocess.Popen(
        [str(x) for x in cmd], cwd=str(cwd) if cwd else None, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        lines.append(line.rstrip("\n"))
        if len(lines) > 400:
            lines = lines[-400:]
    return proc.wait(), lines


def _venv_python(prefix: Path) -> Path:
    return prefix / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _install_lock(python: Path, repo: Path, label: str) -> None:
    lock = repo / "requirements-lock.txt"
    if not lock.exists():
        raise RuntimeError("Exact audited requirements-lock.txt is required")
    rc, tail = _run_streaming(
        [str(python), "-m", "pip", "install", "-r", str(lock)], label=label
    )
    if rc != 0:
        raise RuntimeError(f"{label} failed with exit code {rc}. Tail:\n" + "\n".join(tail[-60:]))


def _verify_runtime(python: Path) -> str:
    code = (
        "import sys,numpy,scipy; "
        "print(sys.version.split()[0]); print(numpy.__version__); print(scipy.__version__)"
    )
    cp = subprocess.run([str(python), "-c", code], text=True, capture_output=True)
    if cp.returncode != 0:
        raise RuntimeError("Runtime verification failed:\n" + cp.stdout + cp.stderr)
    vals = cp.stdout.strip().splitlines()
    if len(vals) < 3:
        raise RuntimeError("Runtime verification returned incomplete version data")
    py, npv, spv = vals[:3]
    if npv != "2.3.5" or spv != "1.17.0":
        raise RuntimeError(f"Dependency lock mismatch: Python={py}, NumPy={npv}, SciPy={spv}")
    return f"Python={py}; NumPy={npv}; SciPy={spv}"


def _bootstrap_micromamba(work_root: Path) -> Path:
    bin_path = work_root / "micromamba" / "bin" / "micromamba"
    if bin_path.exists():
        return bin_path
    archive = work_root / "micromamba.tar.bz2"
    extract_root = work_root / "micromamba"
    extract_root.mkdir(parents=True, exist_ok=True)
    _print("[runtime] Downloading micromamba from the official distribution endpoint...")
    try:
        urllib.request.urlretrieve(MICROMAMBA_URL, archive)
        with tarfile.open(archive, "r:bz2") as tf:
            member = next((m for m in tf.getmembers() if m.name.endswith("bin/micromamba")), None)
            if member is None:
                raise RuntimeError("micromamba archive did not contain bin/micromamba")
            tf.extract(member, extract_root)
    finally:
        if archive.exists():
            archive.unlink()
    if not bin_path.exists():
        # Some archives preserve a leading directory. Locate once and normalize.
        found = list(extract_root.rglob("micromamba"))
        found = [p for p in found if p.is_file()]
        if len(found) != 1:
            raise RuntimeError("Could not locate micromamba executable after extraction")
        bin_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found[0], bin_path)
    bin_path.chmod(0o755)
    return bin_path


def _create_canonical_runtime(repo: Path, work_root: Path) -> tuple[Path, str]:
    """Provision canonical Python 3.13.5 even when Colab's host interpreter is different."""
    prefix = work_root / "erp_mcda_py3135"
    if prefix.exists():
        shutil.rmtree(prefix)
    mm = _bootstrap_micromamba(work_root)
    rc, tail = _run_streaming(
        [str(mm), "create", "-y", "-p", str(prefix), "-c", "conda-forge",
         "--strict-channel-priority", f"python={CANONICAL_PYTHON_TEXT}", "pip"],
        label="canonical-python-provision",
    )
    if rc != 0:
        raise RuntimeError("Canonical Python provisioning failed. Tail:\n" + "\n".join(tail[-80:]))
    py = _venv_python(prefix)
    _install_lock(py, repo, "canonical-dependency-install")
    info = _verify_runtime(py)
    if not info.startswith(f"Python={CANONICAL_PYTHON_TEXT};"):
        raise RuntimeError("Canonical runtime provisioning did not produce Python 3.13.5")
    return py, "CANONICAL_PYTHON_3_13_5"


def _create_host_compat_runtime(repo: Path, work_root: Path) -> tuple[Path, str]:
    """Fallback route: hosted Python + exact dependencies + strict scientific parity gates."""
    prefix = work_root / "erp_mcda_host_compat"
    if prefix.exists():
        shutil.rmtree(prefix)
    rc, tail = _run_streaming([sys.executable, "-m", "venv", str(prefix)], label="host-compat-venv")
    if rc != 0:
        raise RuntimeError("Hosted compatibility venv creation failed. Tail:\n" + "\n".join(tail[-60:]))
    py = _venv_python(prefix)
    _install_lock(py, repo, "host-compat-dependency-install")
    _verify_runtime(py)
    return py, "HOSTED_PYTHON_VERIFIED_COMPATIBILITY"


def prepare_runtime(repo: Path, work_root: Path) -> tuple[Path, str, str]:
    """Return an interpreter, route label, and version summary for a Colab run.

    The canonical interpreter is always preferred. If network/runtime policy prevents that,
    a hosted-Python compatibility environment is allowed only because the downstream full
    reproduction performs strict scientific equivalence/reference gates. The sole non-byte gate
    is limited to the documented NP11 solver-output and R2C score-vector tolerances for hosted BLAS variation.
    """
    repo = repo.resolve(); work_root = work_root.resolve(); work_root.mkdir(parents=True, exist_ok=True)
    host = sys.version.split()[0]
    _print(f"[runtime] Hosted interpreter: {sys.executable} (Python {host})")
    _print("[runtime] Canonical audited reference: Python 3.13.5 + requirements-lock.txt")
    if sys.version_info[:3] == CANONICAL_PYTHON:
        prefix = work_root / "erp_mcda_canonical_venv"
        if prefix.exists(): shutil.rmtree(prefix)
        rc, tail = _run_streaming([sys.executable, "-m", "venv", str(prefix)], label="canonical-venv")
        if rc != 0:
            raise RuntimeError("Canonical venv creation failed. Tail:\n" + "\n".join(tail[-60:]))
        py = _venv_python(prefix)
        _install_lock(py, repo, "canonical-dependency-install")
        return py, "CANONICAL_HOST_PYTHON_3_13_5", _verify_runtime(py)
    try:
        py, route = _create_canonical_runtime(repo, work_root)
        return py, route, _verify_runtime(py)
    except Exception as canonical_error:
        _print("[runtime] Canonical Python provisioning was unavailable; entering strict-parity hosted compatibility route.")
        _print(f"[runtime] Canonical provisioning diagnostic: {canonical_error}")
        py, route = _create_host_compat_runtime(repo, work_root)
        return py, route, _verify_runtime(py)


def _print_failed_parity(parity: Path) -> None:
    if not parity.exists():
        _print(f"[diagnostic] PARITY_REPORT.csv not found at {parity}")
        return
    try:
        with parity.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        fails = [r for r in rows if r.get("status") != "PASS"]
        _print(f"[diagnostic] Parity rows: {len(rows)}; non-PASS rows: {len(fails)}")
        for r in fails[:50]:
            _print("[diagnostic] FAIL " + " | ".join(
                f"{k}={r.get(k,'')}" for k in ("gate","object","status","note","expected_sha256","observed_sha256")
            ))
    except Exception as exc:
        _print(f"[diagnostic] Could not parse parity report: {exc}")


def run_full_reproduction(python: Path, repo: Path, output_dir: Path) -> None:
    """Execute FULL reproduction using the fail-closed hosted-runtime compatibility profile."""
    cmd = [str(python), str(repo / "src/pipeline/reproduce_all.py"),
           "--mode", "full", "--output-dir", str(output_dir),
           "--runtime-profile", "hosted-colab"]
    rc, tail = _run_streaming(cmd, cwd=repo, label="full-reproduction")
    parity = output_dir if output_dir.is_absolute() else repo / output_dir
    parity = parity / "PARITY_REPORT.csv"
    if rc != 0:
        _print_failed_parity(parity)
        _print("[diagnostic] Last captured pipeline lines:")
        for line in tail[-80:]:
            _print("[diagnostic] " + line)
        raise RuntimeError(
            f"FULL reproduction failed with exit code {rc}. See the streamed output and parity diagnostics above."
        )
    _print_failed_parity(parity)
    marker = parity.parent / "FULL_REPRODUCTION_PASS.txt"
    if not marker.exists():
        raise RuntimeError("Pipeline returned zero but FULL_REPRODUCTION_PASS.txt is missing")
    pub = parity.parent / "PUBLICATION_PARITY.csv"
    if not pub.exists():
        raise RuntimeError("Publication parity output is missing")
    with pub.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = [r for r in rows if r.get("status") != "PASS"]
    if bad:
        raise RuntimeError(f"Publication parity contains {len(bad)} non-PASS rows")
    _print(f"[publication-parity] PASS ({len(rows)}/{len(rows)})")


def write_runtime_record(path: Path, *, route: str, info: str) -> None:
    path.write_text(
        "ERP-MCDA COLAB RUNTIME RECORD\n"
        f"route={route}\n"
        f"runtime={info}\n"
        "canonical_reference=Python 3.13.5; NumPy 2.3.5; SciPy 1.17.0\n"
        "acceptance_rule=hosted-runtime scientific-equivalence profile; NP11 numeric CSV abs_tol=1e-6 and R2C terminal score-vector abs_tol=1e-9 only; decision fields/ranks/winner/schema exact; all other gates strict\n",
        encoding="utf-8",
    )
