# Third-Party Notices

This file records known third-party dependencies and data sources in the AssayPilot competition snapshot. It does not replace the complete upstream license texts or grant a license for user-original project code.

## LINCS Cell Painting

Dataset: Natoli, T.; Way, G.; Lu, X.; Logan, D.; Alimova, M.; Hartland, K.; Golub, T.; Carpenter, A.; Singh, S.; Subramanian, A. (2021), *broadinstitute/lincs-cell-painting: Full release of LINCS Cell Painting dataset*, Version v1. Zenodo: https://doi.org/10.5281/zenodo.5008187 . Official repository: https://github.com/broadinstitute/lincs-cell-painting .

The upstream README states that its source code is BSD 3-Clause and its data, results and figures are CC0 1.0. This snapshot does not redistribute raw Cell Painting profiles or images. It uses documented phenotype-derived summaries, experimental metadata and provenance. Restricted molecular structure, fingerprint, MOA and target annotations are excluded. See `docs/DATA_CC0_REFERENCE.md` and `docs/DATA_AND_LICENSE.md`.

## Python dependencies

Dependencies are installed separately and are not vendored in this repository:

- NumPy 2.3.5 — upstream BSD notices and bundled-component terms: https://numpy.org/
- pandas 2.3.3 — BSD 3-Clause: https://pandas.pydata.org/
- scikit-learn 1.7.2 — BSD 3-Clause: https://scikit-learn.org/
- SciPy 1.16.3 — upstream BSD notices and bundled-component terms: https://scipy.org/
- Matplotlib 3.10.6 — Matplotlib license: https://matplotlib.org/
- Python-Markdown 3.8 — BSD 3-Clause: https://python-markdown.github.io/

These names and versions were verified from the recorded packaging environment. Users remain responsible for reviewing the complete license distributed by each dependency.

## Fonts and demo assets

Generated figures use DejaVu Sans glyphs supplied with Matplotlib. The retained notice is in `docs/FONT_LICENSE_DEJAVU.txt`; no font binary is redistributed. The demo contains no external logo, music, stock photograph or raw Cell Painting image.

## AI-assisted development disclosure

AI-assisted development tools, including ChatGPT and Codex, were used for code drafting, debugging, documentation, consistency checks, and workflow support. The research question, experimental design, evaluation protocol, scientific decisions, interpretation of results, release decisions, and final verification were directed and reviewed by the author, Lekang Sun. No AI service is required at demo or reproduction runtime.
