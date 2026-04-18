# Model Selection Analysis (Expanded)

## Dataset Audit

- Dataset aktif untuk retraining tahap 2: `data/processed/zone_dataset_expanded_id.csv`
- Jumlah zona: 77
- Jumlah fitur extended: 65
- Target column: `zone_target`
- Distribusi kelas: {'Jagung': 17, 'Teff': 12, 'Padi': 6, 'Pisang': 6, 'Kelapa': 5, 'Mangga': 5, 'Gandum': 4, 'Jelai': 4, 'Jeruk': 4, 'Semangka': 4, 'Kopi': 4, 'Kacang Hijau': 3, 'Pepaya': 3}
- Jumlah group konteks (`base_context_id`): 53

## Split Strategy

- Split utama: group-aware holdout berdasarkan `base_context_id`
- Dev contexts: ['active::1', 'active::10', 'active::11', 'active::14', 'active::6', 'active::8', 'active::9', 'kaggle::ctx_003', 'kaggle::ctx_009', 'kaggle::ctx_010', 'kaggle::ctx_015', 'kaggle::ctx_016', 'kaggle::ctx_020', 'kaggle::ctx_023', 'kaggle::ctx_037', 'kaggle::ctx_042', 'kaggle::ctx_047', 'kaggle::ctx_048', 'kaggle::ctx_060', 'kaggle::ctx_061', 'kaggle::ctx_063', 'kaggle::ctx_072', 'kaggle::ctx_075', 'kaggle::ctx_082', 'kaggle::ctx_083', 'kaggle::ctx_090', 'kaggle::ctx_093', 'kaggle::ctx_100', 'kaggle::ctx_107', 'kaggle::ctx_112', 'kaggle::ctx_118', 'kaggle::ctx_123', 'kaggle::ctx_131', 'kaggle::ctx_134', 'kaggle::ctx_135']
- Test contexts: ['active::12', 'active::16', 'active::2', 'active::7', 'kaggle::ctx_001', 'kaggle::ctx_002', 'kaggle::ctx_021', 'kaggle::ctx_036', 'kaggle::ctx_043', 'kaggle::ctx_067', 'kaggle::ctx_070', 'kaggle::ctx_101', 'kaggle::ctx_108', 'kaggle::ctx_111', 'kaggle::ctx_116', 'kaggle::ctx_126', 'kaggle::ctx_130', 'kaggle::ctx_133']
- Seleksi model: group-aware CV pada dev split
- Metrik seleksi utama: macro F1

## Candidate Models

```
             scenario_name          model_name fit_status     selection_strategy  cv_splits  cv_accuracy_mean  cv_precision_macro_mean  cv_recall_macro_mean  cv_f1_macro_mean  cv_f1_weighted_mean  cv_accuracy_std  cv_f1_macro_std  selected_for_tuning  is_scenario_winner  is_final_selected  tuned_cv_f1_macro  test_accuracy  test_precision_macro  test_recall_macro  test_f1_macro  test_f1_weighted                                                                                                    best_params_json error_message
            zone_mean_only         extra_trees    success stratified_group_kfold          2          0.716524                 0.744017              0.780983          0.732338             0.695187         0.024217         0.023791                 True                True              False           0.732338       0.916667              0.884615           0.884615       0.884615          0.916667 {"model__n_estimators": 360, "model__min_samples_leaf": 2, "model__max_features": "sqrt", "model__max_depth": null}              
            zone_mean_only logistic_regression    success stratified_group_kfold          2          0.623932                 0.747436              0.733974          0.724176             0.632112         0.068376         0.001099                 True               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
            zone_mean_only            catboost    success stratified_group_kfold          2          0.510684                 0.610989              0.673077          0.607942             0.469133         0.066239         0.031252                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
            zone_mean_only            lightgbm    success stratified_group_kfold          2          0.605413                 0.624237              0.632479          0.602875             0.596357         0.086895         0.053535                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
            zone_mean_only       random_forest    success stratified_group_kfold          2          0.564103                 0.499359              0.569444          0.492054             0.509862         0.102564         0.081664                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
            zone_mean_only             xgboost    success stratified_group_kfold          2          0.525641                 0.383089              0.477564          0.399263             0.456647         0.141026         0.166803                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
zone_mean_plus_variability         extra_trees    success stratified_group_kfold          2          0.772792                 0.816667              0.829060          0.805739             0.758866         0.042023         0.066056                 True                True               True           0.805739       0.875000              0.820513           0.846154       0.830769          0.841667 {"model__n_estimators": 360, "model__min_samples_leaf": 2, "model__max_features": "sqrt", "model__max_depth": null}              
zone_mean_plus_variability logistic_regression    success stratified_group_kfold          2          0.735755                 0.775000              0.785256          0.768602             0.731607         0.004986         0.016466                 True               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
zone_mean_plus_variability            catboost    success stratified_group_kfold          2          0.622507                 0.729167              0.733974          0.687821             0.617901         0.007123         0.030128                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
zone_mean_plus_variability       random_forest    success stratified_group_kfold          2          0.640313                 0.657234              0.679487          0.635780             0.599008         0.063390         0.084132                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
zone_mean_plus_variability            lightgbm    success stratified_group_kfold          2          0.544872                 0.581502              0.613248          0.566550             0.524743         0.121795         0.174476                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
zone_mean_plus_variability             xgboost    success stratified_group_kfold          2          0.470085                 0.326465              0.434829          0.363381             0.386466         0.085470         0.126629                False               False              False                NaN            NaN                   NaN                NaN            NaN               NaN                                                                                                                                  
```

## Selection Decision

1. Model dipilih berdasarkan macro F1 pada group-aware CV, bukan accuracy saja.
2. Scenario final: `zone_mean_plus_variability`
3. Model final: `extra_trees`
4. Holdout test accuracy: 0.8750
5. Holdout test macro F1: 0.8308

## Interpretation

- Task expanded ini lebih sulit daripada baseline 4-kelas lama, jadi penurunan atau kestabilan accuracy harus dibaca bersama macro F1.
- Macro F1 lebih penting karena beberapa kelas tambahan tetap low-support.
