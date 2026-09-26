import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from .loader import FEATURE_PREFIXES


class PhenotypePreprocessor:
    """Fit once on declared development screening; transform never updates state."""
    def fit(self, frame, controls, *, split, n_components=10):
        if split != 'development':
            raise ValueError('Fit requires development partition')
        if hasattr(self, 'columns_'):
            raise ValueError('Create a new versioned instance instead of refitting')
        columns = [c for c in frame if c.startswith(FEATURE_PREFIXES)]
        x = frame[columns].replace([np.inf, -np.inf], np.nan)
        keep = (x.isna().mean() <= .05) & (x.var(ddof=0) > 0)
        columns = list(keep.index[keep])
        c = controls[columns].replace([np.inf, -np.inf], np.nan)
        center = c.median(); mad = (c-center).abs().median()
        columns = list(mad.index[(mad > 0) & np.isfinite(mad)])
        if not columns or len(frame) < 2:
            raise ValueError('No usable development features')
        self.columns_ = columns
        self.impute_ = x[columns].median().to_numpy()
        self.center_ = center[columns].to_numpy(); self.scale_ = mad[columns].to_numpy()
        a, valid = self._scaled(frame)
        if valid.sum() < 2:
            raise ValueError('Insufficient valid development observations')
        self.pca_ = PCA(n_components=min(n_components, len(columns), int(valid.sum())-1), svd_solver='full')
        self.pca_.fit(a[valid])
        z, good = self._scaled(controls)
        if good.sum() < 2:
            raise ValueError('Insufficient reference controls')
        self.reference_center_ = np.median(self.pca_.transform(z[good]), axis=0)
        ctrl = self.pca_.transform(z[good])-self.reference_center_
        self.threshold_ = float(np.quantile(np.sqrt(np.mean(ctrl**2, axis=1)), .95))
        return self

    def _scaled(self, frame):
        x = frame[self.columns_].to_numpy(float).copy()
        x[~np.isfinite(x)] = np.nan
        valid = np.isnan(x).mean(axis=1) <= .05
        x = np.where(np.isnan(x), self.impute_, x)
        return np.clip((x-self.center_)/self.scale_, -10, 10), valid

    def transform(self, frame):
        x, valid = self._scaled(frame)
        z = self.pca_.transform(x)-self.reference_center_
        z[~valid] = np.nan
        return z, valid

    def metadata(self):
        return dict(features=self.columns_, threshold=self.threshold_,
                    impute=self.impute_.tolist(), center=self.center_.tolist(), scale=self.scale_.tolist(),
                    components=self.pca_.components_.tolist(), pca_mean=self.pca_.mean_.tolist(),
                    reference_center=self.reference_center_.tolist())
