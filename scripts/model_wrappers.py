from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.preprocessing import LabelEncoder


def flatten_predictions(y_pred: Any) -> np.ndarray:
    return np.asarray(y_pred, dtype=object).reshape(-1)


class StringLabelXGBClassifier(BaseEstimator, ClassifierMixin):
    """Wrap XGBoost so it can train on string labels and emit string predictions."""

    def __init__(self, estimator: Any):
        self.estimator = estimator

    def fit(self, X: Any, y: pd.Series | np.ndarray) -> "StringLabelXGBClassifier":
        self.label_encoder_ = LabelEncoder()
        y_encoded = self.label_encoder_.fit_transform(np.asarray(y))
        self.classes_ = self.label_encoder_.classes_
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y_encoded)
        return self

    def predict(self, X: Any) -> np.ndarray:
        encoded_predictions = np.asarray(self.estimator_.predict(X)).reshape(-1).astype(int)
        return self.label_encoder_.inverse_transform(encoded_predictions)

    def predict_proba(self, X: Any) -> np.ndarray:
        return self.estimator_.predict_proba(X)


class FlattenPredictionClassifier(BaseEstimator, ClassifierMixin):
    """Wrap estimators whose predict output may come back as a column vector."""

    def __init__(self, estimator: Any):
        self.estimator = estimator

    def fit(self, X: Any, y: pd.Series | np.ndarray) -> "FlattenPredictionClassifier":
        self.estimator_ = clone(self.estimator)
        self.estimator_.fit(X, y)
        self.classes_ = getattr(self.estimator_, "classes_", np.unique(np.asarray(y)))
        return self

    def predict(self, X: Any) -> np.ndarray:
        return flatten_predictions(self.estimator_.predict(X))

    def predict_proba(self, X: Any) -> np.ndarray:
        return self.estimator_.predict_proba(X)
