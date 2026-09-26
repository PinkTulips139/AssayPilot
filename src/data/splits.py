import hashlib
import numpy as np
import pandas as pd

SALT = 'AssayPilot-v1-split-2026-09-18'
ROLES = ('screening', 'confirmation', 'H1', 'H2')


def build_conditions(platemaps, mapping):
    frames = []
    for layout, pm in sorted(platemaps.items()):
        t = pm.dropna(subset=['broad_sample']).copy()
        t = t.merge(mapping, on=['plate_map_name', 'broad_sample'], validate='many_to_one')
        if len(t) != pm.broad_sample.notna().sum() or t.broad_id.isna().any():
            raise ValueError('Incomplete metadata join')
        t['dose'] = pd.to_numeric(t.mmoles_per_liter, errors='raise')
        if not np.isfinite(t.dose).all() or (t.dose <= 0).any():
            raise ValueError('Invalid treatment dose')
        frames.append(t[['plate_map_name', 'well_position', 'broad_id', 'dose']])
    out = pd.concat(frames, ignore_index=True)
    out['dose_key'] = ''
    # Complete-link 1e-6 relative tolerance: sorted group endpoints bound all pairs.
    for compound, indices in out.groupby('broad_id').groups.items():
        values = sorted(out.loc[indices, 'dose'].unique())
        anchor = None
        keys = {}
        for value in values:
            if anchor is None or abs(value-anchor) / max(abs(value), abs(anchor)) > 1e-6:
                anchor = value
            keys[value] = format(anchor, '.17g')
        out.loc[indices, 'dose_key'] = out.loc[indices, 'dose'].map(keys)
    out['condition'] = out.broad_id + '|' + out.dose_key
    # A condition appears once in the universe; choose layout/well before looking at values.
    return out.sort_values(['plate_map_name', 'well_position']).drop_duplicates('condition').reset_index(drop=True)


def plate_roles(barcodes, layouts):
    rows = []
    for layout in sorted(layouts):
        b = barcodes.loc[barcodes.Plate_Map_Name.eq(layout)].drop_duplicates('Assay_Plate_Barcode')
        choices = []
        for batch, g in b.groupby('Batch_Number'):
            if len(g) >= 4:
                choices.append((str(g.Batch_Date.min()), str(batch), g))
        if not choices:
            raise ValueError('No four-plate batch for ' + layout)
        _, batch, g = sorted(choices, key=lambda x: x[:2])[0]
        for role, plate in zip(ROLES, sorted(g.Assay_Plate_Barcode)[:4]):
            rows.append(dict(layout=layout, batch=batch, plate=plate, role=role))
    return pd.DataFrame(rows)


def make_split(conditions, exposed):
    counts = conditions.groupby('broad_id').size().to_dict()
    ordered = sorted(counts, key=lambda c: (hashlib.sha256((SALT+'|'+c).encode()).hexdigest(), c))
    seen = [c for c in ordered if c in exposed]
    unseen = [c for c in ordered if c not in exposed]
    allocation = {}; stats = {}
    def take(pool, label, min_compounds, min_conditions):
        selected = []; n = 0
        while pool and (len(selected) < min_compounds or n < min_conditions):
            c = pool.pop(0); selected.append(c); n += counts[c]
        if len(selected) < min_compounds or n < min_conditions:
            raise ValueError('Metadata universe insufficient for '+label)
        allocation.update({c: label for c in selected})
        stats[label] = dict(compounds=len(selected), conditions=n)
    training_pool = seen + unseen
    take(training_pool, 'development', 40, 160)
    unseen = [c for c in unseen if c not in allocation]
    for name, nc, nr in [('validation', 10, 40), ('T1', 50, 200), ('T2', 50, 200)]:
        take(unseen, name, nc, nr)
    allocation.update({c: 'quarantine' if c in exposed else 'reserve' for c in ordered if c not in allocation})
    result = conditions.copy(); result['split'] = result.broad_id.map(allocation)
    if not result.loc[result.broad_id.isin(exposed), 'split'].isin(['development', 'quarantine']).all():
        raise AssertionError('Exposed compound leaked')
    return result, stats
