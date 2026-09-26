# Data and release boundary
The official LINCS Cell Painting README states data, results and figures are CC0 1.0; upstream code is BSD-3-Clause. This does not license restricted CLUE annotations. Official source: https://github.com/broadinstitute/lincs-cell-painting ; see DATA_CC0_REFERENCE.md and [Third-Party Notices](../THIRD_PARTY_NOTICES.md) for retained attribution. Source and license evidence is retained in this snapshot.

Included experimental fields are registered broad_id/compound and broad_sample identifiers, dose, well, plate, plate-map/layout, batch, condition/role/split and frozen phenotype-derived summaries/parameters. Their lineage is the public experimental platemaps and augmented profiles, not the restricted CLUE annotation directory. These are assay identifiers, not human-participant identities or evidence of chemical/scaffold independence. The loader uses selected experimental fields; it does not join molecular structure, fingerprints, MOA or targets.

Excluded: raw profiles/images, restricted structure/fingerprint/MOA/target/CLUE annotation values, credentials, caches, private absolute paths, and new batch3/4/5 evidence. No data was downloaded or newly analyzed for this package. Reproduction inputs must be acquired independently from pinned official URLs and match the recorded hashes. Full experiment reproduction has not been executed during packaging.


This public competition snapshot follows [RIGHTS_NOTICE.md](../RIGHTS_NOTICE.md); third-party materials retain their upstream terms.
