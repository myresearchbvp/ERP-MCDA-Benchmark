# ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark

Data and Python code for *Computational Reconstruction, Auditability and Decision Stability in Published Multicriteria Models for Enterprise Resource Planning Selection: A Cross-Case Benchmark*.

The benchmark covers 12 ERP-MCDA decision-problem lineages from 13 publications. Nine lineages can be reconstructed through the terminal ranking stage. The code evaluates terminal-weight perturbation, single-criterion deletion and source-defined sensitivity analyses for NP04 and NP12.

## Google Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/myresearchbvp/ERP-MCDA-Benchmark/blob/main/notebooks/full_reproduction_colab.ipynb)

Run the notebook's code cell. It installs the dependencies, reproduces the analyses and downloads the results.

## Run locally

Install the dependencies and run the full analysis from the repository root:

```bash
python -m pip install -r requirements-lock.txt
python src/pipeline/reproduce_all.py --mode full --output-dir reproduced --runtime-profile hosted-colab
```

For a quick check of selected baselines, NP11 certificates and publication data:

```bash
python src/pipeline/reproduce_all.py --mode quick --output-dir reproduced_quick --runtime-profile hosted-colab
```

Run the tests with:

```bash
python -m pytest -q -p no:cacheprovider
```

The full run reconstructs the evaluable cases, reruns the robustness analyses, checks NP11 with three solvers and verifies its rational/interval certificates. It also rebuilds the table and figure data. Results and verification reports are saved in the selected output directory; `PARITY_REPORT.csv` and `PUBLICATION_PARITY.csv` report agreement with the reference files.

## Files and methods

- `data/`: extracted inputs, standardized data and source provenance
- `src/`: reconstruction and robustness code
- `results/reference/`: benchmark results and verification data
- `results/publication/`: data for Tables 1-3, Figures 1-2 and additional diagnostics
- `docs/`: [methods](docs/METHOD_MAP.md), [reproducibility scope](docs/REPRODUCIBILITY_SCOPE.md), [limitations](docs/KNOWN_NE_AND_LIMITATIONS.md) and [NP11 criterion deletion](docs/NP11_CRITERION_DELETION.md)
- `notebooks/`: Google Colab notebook
- `tests/`: automated checks

`NE` denotes a calculation that is not evaluable or not applicable under the stated source and method conditions.

## Environment

The reference environment uses Python 3.13.5, NumPy 2.3.5 and SciPy 1.17.0. `environment-lock.yml` records the environment and `requirements-lock.txt` pins the direct dependencies, including the NP11 certification tools. The analyses have also been run on Python 3.12.14. The [runtime notes](docs/COLAB_RUNTIME_COMPATIBILITY.md) explain the numerical tolerances used by the `hosted-colab` profile.

## Sources and citation

Source locators and file hashes are listed in `data/provenance/`. Article PDFs and publisher workbooks are not redistributed. See [source provenance](docs/SOURCE_PROVENANCE.md).

Please cite the accompanying article when using this benchmark. Publication details will be added when available.

## License

Original code is licensed under MIT. Original documentation and project-generated outputs are licensed under CC BY 4.0 where the authors hold the necessary rights. See [LICENSE](LICENSE), [content license scope](LICENSES/CONTENT_LICENSE_SCOPE.md) and [third-party sources](THIRD_PARTY_DATA_AND_LICENSES.md).
