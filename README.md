# ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark

This repository accompanies the study *Computational Reconstruction, Auditability, and Decision Stability in Published Multicriteria Models for Enterprise Resource Planning Selection: A Cross-Case Benchmark*.

It contains the data and Python code used to reconstruct published ERP multi-criteria decision-analysis (MCDA) results and examine how stable the reported decisions are when criterion weights or individual criteria are changed.

## What is included

The benchmark covers twelve published ERP-MCDA cases (NP01-NP12). Nine can be reconstructed at the terminal ranking stage from the available source material. The repository also includes:

- terminal-weight perturbation analysis
- single-criterion deletion analysis
- the source-defined sensitivity analyses for NP04 and NP12
- the machine-readable files used for Tables 1-3 and Figures 1, 2, S1 and S2
- provenance records for the source material used in each case

`NE` means that a calculation is not evaluable or not applicable under the stated source and method conditions. Details are given in `docs/KNOWN_NE_AND_LIMITATIONS.md`.

## Run the code

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

For a quick check:

```bash
python src/pipeline/reproduce_all.py --mode quick --output-dir reproduced_quick
```

For the full reproduction:

```bash
python src/pipeline/reproduce_all.py --mode full --output-dir reproduced
```

The full run reconstructs the evaluable cases, regenerates the robustness analyses and rebuilds the publication data files. The main run reports are written to `PARITY_REPORT.csv` and `PUBLICATION_PARITY.csv` in the output directory.

## Google Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/myresearchbvp/ERP-MCDA-Benchmark/blob/main/notebooks/full_reproduction_colab.ipynb)

For a browser-based run, open the notebook above and run its cells in order.

## Repository structure

- `data/` - extracted, standardised and provenance data
- `src/` - reconstruction and robustness code
- `results/reference/` - reference results used by the reproduction pipeline
- `results/publication/` - data used for the paper's tables and figures
- `docs/` - method notes, provenance information and benchmark documentation
- `notebooks/` - Google Colab entry point
- `tests/` - automated checks

## Environment

The reference environment is recorded in `environment-lock.yml` and uses:

- Python 3.13.5
- NumPy 2.3.5
- SciPy 1.17.0
- pytest 9.0.2

`requirements-lock.txt` pins the direct Python dependencies. `checksums.sha256` covers the computational files checked by the reproduction pipeline.

## Source material

The repository does not redistribute article PDFs, publisher supplementary workbooks or other third-party source files.

`data/provenance/CASE_SOURCE_MAP.csv` records the sources and DOI or stable locators used for each case. `data/provenance/SOURCE_MANIFEST_SHA256.csv` records source-file hashes. Further details are in `docs/SOURCE_PROVENANCE.md` and `THIRD_PARTY_DATA_AND_LICENSES.md`.


## Citation

> *If you use this repository, please cite the accompanying article once it is published. Full citation details will be added here after publication.*

## License

The original code in this repository is licensed under the MIT License.

Original documentation and project-generated outputs or data are licensed under CC BY 4.0 only where the authors have the right to grant that licence. Third-party publications, publisher supplements and other third-party material are not relicensed by this repository.

See `LICENSE`, `LICENSES/CC-BY-4.0.txt`, `LICENSES/CONTENT_LICENSE_SCOPE.md` and `THIRD_PARTY_DATA_AND_LICENSES.md` for details.
