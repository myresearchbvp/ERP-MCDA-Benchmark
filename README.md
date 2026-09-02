# ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark

This repository provides a reproducible computational benchmark for twelve purposively selected ERP multi-criteria decision-analysis (MCDA) lineages. It reconstructs terminal published rankings where the public source chain is evaluable, evaluates decision stability under prespecified terminal-weight perturbations and single-criterion deletions, and reproduces source-defined native sensitivity analyses. It also rebuilds the machine-readable source data used by the accompanying study's tables and figures.

## Benchmark scope

The twelve cases (NP01–NP12) are a purposive, lineage-aware benchmark rather than a prevalence sample of ERP-MCDA research. Nine lineages are terminally evaluable under the documented public source chain. `NE` means not evaluable or not applicable under the stated source/method conditions; it does **not** mean a negative robustness result. `docs/BENCHMARK_AND_LINEAGE_MAP.csv` records lineage identities and branch/configuration semantics, while `docs/KNOWN_NE_AND_LIMITATIONS.md` summarizes the non-evaluable cases.

## Quick start

Create an environment and run the smoke check:

```bash
python -m pip install -r requirements.txt
python src/pipeline/reproduce_all.py --mode quick --output-dir reproduced_quick
```

Quick mode checks repository integrity and a compact computational route; it is not the full publication reproduction.

## Full reproduction

```bash
python src/pipeline/reproduce_all.py --mode full --output-dir reproduced
```

Full mode verifies scientific checksums, reruns the nine evaluable native baselines, regenerates 650,000 terminal-weight perturbation rows, executes the 118 applicable single-criterion deletion operations while retaining the prespecified `NE` records, recomputes the source-defined NP04 and NP12 sensitivity analyses, checks source-resolution consistency, and rebuilds all publication-source CSVs. A required validation failure returns a non-zero exit code. The principal machine-readable diagnostics are `reproduced/PARITY_REPORT.csv` and `reproduced/PUBLICATION_PARITY.csv`.

`checksums.sha256` covers the computationally locked scientific assets used by the reproduction pipeline. Reader-facing metadata and documentation such as the README, citation and licensing files are not part of this scientific checksum scope. Publication-source CSVs are regenerated separately and checked by publication parity.

## Environment

The tested deterministic reference is recorded in `environment-lock.yml`: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, and pytest 9.0.2. `requirements-lock.txt` pins the direct Python dependencies. `requirements.txt` and `environment.yml` provide broader convenience ranges.

With a Conda-compatible tool:

```bash
conda env create -f environment-lock.yml
conda activate erp-mcda-repro
```

Or from an existing Python 3.13.5 environment:

```bash
python -m pip install -r requirements-lock.txt
```

## Publication source data

`results/publication/` contains the seven canonical machine-readable source files used for Tables 1–3 and Figures 1, 2, S1, and S2. The full pipeline regenerates these objects and verifies their values against the repository's scientific reference fixtures.

## Google Colab

`notebooks/full_reproduction_colab.ipynb` is the single hosted-runtime entry point. After this repository is publicly available, enter the real repository URL and an exact commit hash in the notebook. It checks out that commit, verifies `HEAD`, provisions the tested Python/dependency route where possible, and runs the full reproduction fail-closed. No repository URL or commit is prefilled here. Hosted-runtime equivalence rules for the small hardware-sensitive numeric fields are documented in `docs/COLAB_RUNTIME_COMPATIBILITY.md`.

## Provenance and third-party boundary

The repository does **not** redistribute article PDFs, publisher supplementary workbooks, or other third-party source binaries. `data/provenance/CASE_SOURCE_MAP.csv` provides source identities and DOI/stable locators; `data/provenance/SOURCE_MANIFEST_SHA256.csv` provides source-file hashes. Extracted and standardized factual records required for the computational benchmark are stored under `data/`, and scientific verification fixtures are under `results/reference/`. See `docs/SOURCE_PROVENANCE.md` and `THIRD_PARTY_DATA_AND_LICENSES.md` for the precise boundary.

## Citation

Please cite the repository using `CITATION.cff` and cite the accompanying study when using the benchmark in scholarly work:

*Computational Reconstruction, Auditability, and Decision Stability in Published Multicriteria Models for Enterprise Resource Planning Selection: A Cross-Case Benchmark* — Vasile Paul Bresfelean, Zsolt Csaba Johanyák, Silviu Claudiu Popa, and George Sebastian Chis.

Correspondence: `paul.bresfelean@econ.ubbcluj.ro`.

## Licensing

Original repository code is licensed under the MIT License in `LICENSE`. Original repository documentation and original project-generated outputs/data are licensed under CC BY 4.0 **only where the authors have the rights to grant that license**; see `LICENSES/CC-BY-4.0.txt` and `LICENSES/CONTENT_LICENSE_SCOPE.md`. The CC BY 4.0 grant does not blanket-relicense third-party publications, publisher supplements, source-derived expressive content, or source-derived records whose underlying rights remain with their respective rights holders.

## Reproducibility expectations

The public execution route preserves the benchmark definitions, denominators, branch/configuration semantics, `NE` statuses, and final decision rules used by the accompanying study. Reference implementations and verification fixtures provide the documented computational route used to reproduce and verify the benchmark results. For method details see `docs/METHOD_MAP.md`, `docs/REPRODUCIBILITY_SCOPE.md`, and `docs/REFERENCE_IMPLEMENTATION_SCOPE.md`.
