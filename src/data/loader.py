from pathlib import Path
import hashlib
import json
import csv
import gzip
import numpy as np
import pandas as pd

FEATURE_PREFIXES = ('Cells_', 'Cytoplasm_', 'Nuclei_')
METADATA = ('Metadata_broad_sample', 'Metadata_mmoles_per_liter',
            'Metadata_Plate', 'Metadata_Well', 'Metadata_Plate_Map_Name',
            'Metadata_Batch_Number', 'Metadata_Batch_Date')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_mapping(path):
    m = pd.read_csv(path, sep='\t', usecols=['broad_sample', 'broad_id', 'plate_map_name'])
    m = m.dropna(subset=['broad_sample', 'broad_id']).drop_duplicates()
    if m.duplicated(['plate_map_name', 'broad_sample']).any():
        raise ValueError('Ambiguous experimental compound mapping')
    return m


def load_profile(path, mapping, expected_sha256, *, allowed_wells=None, include_controls=True):
    if digest(path) != expected_sha256:
        raise ValueError('Source checksum mismatch')
    if allowed_wells is None:
        df = pd.read_csv(path, usecols=lambda c: c in METADATA or c.startswith(FEATURE_PREFIXES))
    else:
        # Filter by experimental identity before converting or summarizing phenotype values.
        # Transport may contain other rows; they never enter the analytical dataframe.
        rows = []
        with gzip.open(path, 'rt', newline='') as handle:
            reader = csv.DictReader(handle)
            cols = [c for c in reader.fieldnames if c in METADATA or c.startswith(FEATURE_PREFIXES)]
            for row in reader:
                if row['Metadata_Well'] in allowed_wells or (include_controls and row['Metadata_broad_sample']=='DMSO'):
                    rows.append({c:row[c] for c in cols})
        df = pd.DataFrame(rows, columns=cols)
        df['Metadata_mmoles_per_liter'] = pd.to_numeric(df.Metadata_mmoles_per_liter, errors='raise')
        feature_cols = [c for c in df if c.startswith(FEATURE_PREFIXES)]
        df[feature_cols] = df[feature_cols].replace('', np.nan)
    if not set(METADATA).issubset(df.columns):
        raise ValueError('Required experimental metadata missing')
    if df.duplicated(['Metadata_Plate', 'Metadata_Well']).any():
        raise ValueError('Duplicate physical observation')
    df = df.merge(mapping, left_on=['Metadata_Plate_Map_Name', 'Metadata_broad_sample'],
                  right_on=['plate_map_name', 'broad_sample'], how='left', validate='many_to_one')
    df['control'] = df.Metadata_broad_sample.eq('DMSO')
    if df.loc[~df.control, 'broad_id'].isna().any():
        raise ValueError('Unmapped treatment')
    features = [c for c in df if c.startswith(FEATURE_PREFIXES)]
    if not features:
        raise ValueError('No phenotype columns')
    df[features] = df[features].apply(pd.to_numeric, errors='raise').replace([np.inf, -np.inf], np.nan)
    return df


def local_manifest(directory):
    return {x['file']: x for x in json.loads((Path(directory) / 'manifest.json').read_text(encoding='utf-8'))}
