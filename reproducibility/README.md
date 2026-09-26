# Reproduce saved evidence

This minimal snapshot supports figure, table and report reproduction from saved results. It does not contain raw phenotype profiles or claim a full experiment rerun.

From the repository root, using `requirements_packaging.txt`:

```powershell
python reproducibility/verify_saved_artifacts.py
python reproducibility/render_saved_results.py
python reproducibility/render_report.py
```

`verify_saved_artifacts.py` checks every public file recorded in `artifact_index.json`. `render_saved_results.py` reads the existing aggregate/per-seed CSV and JSON evidence to rebuild six figures and five main tables. It does not execute a selector or recompute bootstrap samples. `render_report.py` converts the Markdown Technical Report to HTML.

Frozen method fingerprint: `009d78b97ac2d1d47986fd13e3f5592c01c8e0b0e09ab9063d20cfe6a364bda7`.

Split manifest SHA256: `52e61d9c7136907226776cfe69895004890234916f5617492c71a4010392b45a`.

Role manifest SHA256: `c1c6f22b19d99cc58d2f62257f8843833df3f131351a7fb31252b464a3f048d7`.

Seeds 0–19; 12 initial conditions; 12 rounds of four queries; confirmation budget 60; two-dose-per-compound cap; reference cost 96; screen cost 300. Coverage-AUC is trapezoidal coverage over budgets 12 through 60 divided by 48. Saved bootstrap estimates use 10,000 paired resamples with RNG seed 1600 within each fixed campaign.

The static demo in `demo/index.html` replays existing selection data embedded in `demo/data.js`. Individual private-workspace run files are intentionally not duplicated in this minimal snapshot. T1/T2 are performance-exposed and cannot serve as independent confirmation for a later method informed by their outcomes.
