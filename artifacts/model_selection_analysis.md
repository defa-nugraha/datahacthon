# Model Selection Analysis (Indonesia Labels)

## Dataset Audit

- Dataset aktif: `data/processed/zone_dataset_extended_id.csv`
- Jumlah zona: 33
- Jumlah fitur extended: 148
- Target column: `zone_target`
- Distribusi kelas: {'Jagung': 13, 'Teff': 12, 'Gandum': 4, 'Jelai': 4}
- Jumlah group konteks (`base_context_id`): 11

## Split Strategy

- Split utama: group-aware holdout berdasarkan `base_context_id`
- Dev contexts: [1, 2, 6, 7, 10, 11, 12]
- Test contexts: [8, 9, 14, 16]
- Seleksi model: group-aware CV pada dev split
- Metrik seleksi utama: macro F1

## Candidate Models

```
             scenario_name          model_name fit_status     selection_strategy  cv_splits  cv_accuracy_mean  cv_precision_macro_mean  cv_recall_macro_mean  cv_f1_macro_mean  cv_f1_weighted_mean  cv_accuracy_std  cv_f1_macro_std  selected_for_tuning  is_scenario_winner  is_final_selected  tuned_cv_f1_macro  test_accuracy  test_precision_macro  test_recall_macro  test_f1_macro  test_f1_weighted                                                                                                                                                          best_params_json error_message
            zone_mean_only            catboost    success stratified_group_kfold          3          0.648718                 0.483333              0.530864          0.497222             0.635256         0.145455         0.271342                 True                True               True           0.551692       0.714286              0.666667           0.666667       0.666667          0.714286                           {"model__estimator__learning_rate": 0.03, "model__estimator__l2_leaf_reg": 3, "model__estimator__iterations": 60, "model__estimator__depth": 4}              
            zone_mean_only         extra_trees    success stratified_group_kfold          3          0.674359                 0.429167              0.518519          0.453836             0.609997         0.180546         0.264381                 True               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
            zone_mean_only            lightgbm    success stratified_group_kfold          3          0.514103                 0.381481              0.464506          0.383532             0.506181         0.190513         0.204076                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
            zone_mean_only       random_forest    success stratified_group_kfold          3          0.623077                 0.361111              0.419753          0.376852             0.603205         0.111118         0.107973                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
            zone_mean_only logistic_regression    success stratified_group_kfold          3          0.581410                 0.333333              0.310185          0.310652             0.579680         0.161480         0.071162                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
            zone_mean_only             xgboost    success stratified_group_kfold          3          0.446795                 0.227315              0.283951          0.240410             0.407807         0.227630         0.157019                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
zone_mean_plus_variability            lightgbm    success stratified_group_kfold          3          0.597436                 0.492593              0.520062          0.440476             0.595070         0.078530         0.166099                 True                True              False           0.440476       0.714286              0.416667           0.500000       0.450000          0.657143 {"model__subsample": 0.8, "model__num_leaves": 7, "model__n_estimators": 40, "model__min_child_samples": 3, "model__learning_rate": 0.03, "model__colsample_bytree": 1.0}              
zone_mean_plus_variability             xgboost    success stratified_group_kfold          3          0.597436                 0.416667              0.506173          0.419180             0.574878         0.078530         0.188724                 True               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
zone_mean_plus_variability         extra_trees    success stratified_group_kfold          3          0.648718                 0.329167              0.432099          0.367670             0.575482         0.145455         0.145814                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
zone_mean_plus_variability            catboost    success stratified_group_kfold          3          0.581410                 0.333333              0.391975          0.343519             0.558761         0.161480         0.120662                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
zone_mean_plus_variability logistic_regression    success stratified_group_kfold          3          0.597436                 0.314583              0.342593          0.313866             0.581620         0.078530         0.045224                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
zone_mean_plus_variability       random_forest    success stratified_group_kfold          3          0.504487                 0.300926              0.354938          0.282265             0.472140         0.094945         0.064125                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                                                                        
```

## Selection Decision

1. Model dipilih berdasarkan macro F1 pada group-aware CV, bukan accuracy test.
2. Scenario final: `zone_mean_only`
3. Model final: `catboost`
4. Holdout test accuracy: 0.7143
5. Holdout test macro F1: 0.6667
6. Baseline model aktif sebelumnya memiliki accuracy 0.7143 dan macro F1 0.4643.

## Interpretation

- Karena dataset sangat kecil dan tidak seimbang, macro F1 lebih representatif daripada accuracy semata.
- Pergantian label ke Bahasa Indonesia tidak menambah informasi baru pada fitur; perubahan performa, jika ada, berasal dari pemilihan model dan tuning, bukan dari translasi label itu sendiri.
