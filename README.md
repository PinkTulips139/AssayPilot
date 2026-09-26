# AssayPilot: Auditable Policy Evaluation for Phenotype Discovery

**Frozen confirmation changed the policy-selection conclusion.** AssayPilot evaluates budget-constrained phenotype-discovery policies with frozen protocols, auditable selection traces, identity-aware confirmation and explicit claim boundaries.

| Coverage-only | Development | T1 confirmation | T2 confirmation |
| --- | ---: | ---: | ---: |
| Mean Coverage-AUC | 0.91806 | 0.69018 | 0.88917 |
| Rank among the same five policies | 1 | 4 | 4 |

![Development-to-confirmation ranking reversal](figures/figure_3.png)

[Technical report](REPORT/ASSAYPILOT_TECHNICAL_REPORT.html) · [Evidence replay](demo/index.html) · [Confirmation results](tables/table_2.md) · [Reproduction](reproducibility/README.md)

## What this project contributes

AssayPilot provides a budgeted sequential simulator, a leakage and identity-aware confirmation protocol, systematic policy comparison, and an evidence chain that retains negative results. Five frozen policies were evaluated with the same campaigns, seed protocol, budget, preprocessing, reference and evaluator. All 200 planned confirmation runs completed with zero failures.

Coverage-only led Development at 0.91806 but ranked fourth in both fixed confirmation campaigns. Diversity-only led T1 (0.85625); Uncertainty-only led T2 (0.92750). The formal result is **C — COVERAGE_ONLY_NOT_CONFIRMED**. Multi-objective QACS was also not supported in development. These findings motivate the evaluation framework; they do not establish a universally optimal policy.

## Claim scope

The supported scope is one study, a previously seen batch environment, registered entities held out from development and physical plates not used in development. T1 and T2 share eight plates and are not independent biological replications. Chemical/scaffold independence is unknown; unseen-batch and external-study generalization are not established. This is retrospective offline evaluation with no demonstrated prospective wet-lab, drug-efficacy or clinical benefit.

## Repository map

- `src/`: archived scientific implementation used by the frozen evaluation.
- `configs/`: frozen method, preprocessing, reference and split manifests.
- `results/`: minimal saved aggregates and adjudication evidence needed by the report and renderer.
- `figures/`, `tables/`: six report figures, five main tables and source records.
- `demo/`: static browser replay of saved evidence; it never executes a selector.
- `REPORT/`: Technical Report in Markdown and HTML.
- `reproducibility/`: saved-result verification and figure/table/report rendering.
- `docs/`: claim, authorship and data boundaries.

## Local evidence replay

Clone or download this repository, then open `demo/index.html` in a browser. This is a static saved-evidence replay, not a hosted web app. It does not execute a selector and requires no external API.

## Reproduce figures, tables and report

Use the recorded versions in `reproducibility/requirements_packaging.txt`, then run from the repository root:

```powershell
python reproducibility/verify_saved_artifacts.py
python reproducibility/render_saved_results.py
python reproducibility/render_report.py
```

These commands consume saved results only. They do not run policies, fit preprocessing, access raw profiles or perform a new experiment. Figure/table/report reproduction has been smoke-tested in this snapshot. A full 200-run experiment rerun is outside this minimal public package and is not claimed.

## Data and rights

Raw profiles, restricted structure/fingerprint/MOA/target annotations, registration records, private correspondence and internal research audits are excluded. Upstream data and dependencies retain their original ownership and terms. No additional open-source license is granted for user-original project code in this snapshot. See [Rights Notice](RIGHTS_NOTICE.md), [Third-Party Notices](THIRD_PARTY_NOTICES.md) and [data boundary](docs/DATA_AND_LICENSE.md).

## Author and AI disclosure

**Lekang Sun (孙乐康)** — **Beijing University of Technology (北京工业大学)**. Affiliation does not imply institutional endorsement or ownership.

AI-assisted development tools, including ChatGPT and Codex, were used for code drafting, debugging, documentation, consistency checks and workflow support. The research question, experimental design, evaluation protocol, scientific decisions, interpretation, release decisions and final verification were directed and reviewed by the author.
