# Modeling Strategy

## Problem Framing

- Selected framing: multiclass classification for crop recommendation.
- Reason: the final dataset contains one target label per observation and does not include user-item interaction data or graded relevance judgments required by a classical recommender system.
- Deployment stance: use the classifier as the main predictive engine, then optionally apply rule-based post-filtering from EcoCrop or GAEZ later.

## Dataset Decision

- Training dataset: `data/processed/final_dataset.csv`
- Source: single-source cleaned version of `mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- Cross-source row-level merging was rejected because candidate datasets lack reliable shared keys, aligned units, or consistent label semantics.

## Validation Protocol

- Split strategy: stratified train/validation/test.
- Random seed: 42
- Model selection: 4-fold stratified cross-validation on the training split with `macro_f1` as the primary ranking metric.
- Hyperparameter tuning: `RandomizedSearchCV` on the best cross-validation candidate only.
- Final evaluation: hold-out test split after refitting the tuned model on train + validation.

## Models Compared

- Logistic Regression with class balancing for an interpretable linear baseline.
- Random Forest for nonlinear tabular robustness.
- Extra Trees for a stronger high-variance ensemble baseline on mixed numeric/categorical features.

## Risks And Mitigations

- Class imbalance: handled with stratification, macro metrics, and class-weighted models.
- Data leakage: preprocessing is fully contained inside scikit-learn pipelines and fit only on training data within each split/CV fold.
- Label noise: `soil_color` and crop labels were normalized, and the non-crop class `Fallow` was removed from the target space.
- Merge noise: avoided by not forcing weak cross-source joins.
- External validity: the model is trained on an Ethiopia-based dataset, so transfer to Indonesia must be treated as a domain adaptation problem, not assumed.

## Best Model Summary

- Best model: `random_forest`
- Validation macro F1: 0.2794
- Test macro F1: 0.2815
- Test accuracy: 0.4575
