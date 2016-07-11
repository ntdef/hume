import pandas as pd
import numpy as np
from io import BytesIO
from hume.hume import Hume


class SciKitHume:
    "Implements the sklearn interface for hume"
    def __init__(self, image, params=None, target_label='target', verbose=False):
        self._hume = Hume(image, params=params)
        self._verbose = verbose
        self.target_label = target_label

    def fit(self, X, y):
        X = pd.DataFrame(X)
        X[self.target_label] = y
        data = pd.melt(X.reset_index(), id_vars="id")
        self._hume = self._hume.fit(BytesIO(data.to_csv(header=None, index=None)),
                                    target=self.target_label,
                                    verbose=self._verbose)

    def predict(self, X):
        data = pd.DataFrame(X)
        res = self._hume.predict(data.to_csv(header=None, index=None))
        return np.loadtxt(BytesIO(res))

    def get_params(self, deep=True):
        return self._hume.params()

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            self.setattr(parameter, value)
        return self
