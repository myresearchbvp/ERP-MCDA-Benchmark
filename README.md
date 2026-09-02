# ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark

This repository contains the computational material for a twelve-case benchmark of published ERP multi-criteria decision-analysis (MCDA) studies. It reconstructs published rankings when the public source material allows this, examines decision stability under terminal-weight changes and single-criterion deletion, reproduces the source-defined sensitivity analyses for NP04 and NP12 and rebuilds the data used in the study's tables and figures.

## Benchmark

The benchmark covers twelve ERP-MCDA cases, NP01-NP12. Nine can be evaluated at the terminal stage from the documented public source chain.

`NE` means not evaluable or not applicable under the stated source and method conditions. It does not mean that a robustness test produced a negative result.

The case structure is summarised in:

- `docs/BENCHMARK_AND_LINEAGE_MAP.csv`
- `docs/KNOWN_NE_AND_LIMITATIONS.md`
- `docs/METHOD_MAP.md`

## Quick check

Install the dependencies and run:

```bash
python -m pip install -r requirements.txt
python src/pipeline/reproduce_all.py --mode quick --output-dir reproduced_quick
```

Quick mode checks repository integrity and a compact computational route. It is not the full reproduction.

## Full reproduction

```bash
python src/pipeline/reproduce_all.py --mode full --output-dir reproduced
```

Full mode verifies the scientific checksums, reruns the nine evaluable native baselines, regenerates 650,000 terminal-weight perturbation rows, executes the 118 applicable single-criterion deletion operations, retains the stated `NE` records, recomputes the NP04 and NP12 sensitivity analyses and rebuilds the publication-source CSV files.

The main diagnostics are written to:

- `reproduced/PARITY_REPORT.csv`
- `reproduced/PUBLICATION_PARITY.csv`

`checksums.sha256` covers only the computational scientific assets used by the reproduction pipeline. The README, citation file, licence files, documentation, tests and Colab notebook are outside this scientific checksum.

## Tested environment

The reference environment is recorded in `environment-lock.yml`:

- Python 3.13.5
- NumPy 2.3.5
- SciPy 1.17.0
- pytest 9.0.2

`requirements-lock.txt` pins the direct Python dependencies.

With Conda:

```bash
conda env create -f environment-lock.yml
conda activate erp-mcda-repro
```

Or from an existing Python 3.13.5 environment:

```bash
python -m pip install -r requirements-lock.txt
```

## Publication data

`results/publication/` contains the seven machine-readable files used for Tables 1-3 and Figures 1, 2, S1 and S2. The full pipeline regenerates these files and checks their values against the reference results in the repository.

## Google Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/myresearchbvp/ERP-MCDA-Benchmark/blob/main/notebooks/full_reproduction_colab.ipynb)

The notebook provides the hosted full-reproduction route. It is pinned to the public commit that passed the repository's reproducibility workflow.

Runtime notes are available in `docs/COLAB_RUNTIME_COMPATIBILITY.md`.

## Provenance and third-party material

The repository does not redistribute article PDFs, publisher supplementary workbooks or other third-party source binaries.

`data/provenance/CASE_SOURCE_MAP.csv` records source identities and DOI or stable locators. `data/provenance/SOURCE_MANIFEST_SHA256.csv` records source-file hashes. Extracted factual records required for the benchmark are stored under `data/`. Reference results used for computational verification are stored under `results/reference/`.

See `docs/SOURCE_PROVENANCE.md` and `THIRD_PARTY_DATA_AND_LICENSES.md` for details.

## Citation

Please cite this repository using `CITATION.cff` and cite the accompanying study when using the benchmark in scholarly work:

*Computational Reconstruction, Auditability, and Decision Stability in Published Multicriteria Models for Enterprise Resource Planning Selection: A Cross-Case Benchmark*

Vasile Paul Bresfelean, Zsolt Csaba Johanyák, Silviu Claudiu Popa and George Sebastian Chis

Correspondence: `paul.bresfelean@econ.ubbcluj.ro`

## Licence

Original repository code is licensed under the MIT License in `LICENSE`.

Original repository documentation and original project-generated outputs or data are licensed under CC BY 4.0 only where the authors have the right to grant that licence. See `LICENSES/CC-BY-4.0.txt` and `LICENSES/CONTENT_LICENSE_SCOPE.md`.

Third-party publications, publisher supplements and other third-party material are not relicensed by this repository.

## Further documentation

- `docs/REPRODUCIBILITY_SCOPE.md`
- `docs/REFERENCE_IMPLEMENTATION_SCOPE.md`
- `docs/SOURCE_PROVENANCE.md`
