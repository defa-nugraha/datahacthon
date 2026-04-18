# Best Model Summary (Indonesia Labels)

## Final Selection

- Best scenario: `zone_mean_only`
- Best model: `catboost`
- Selection metric: macro F1 on group-aware CV
- Best CV macro F1: 0.5517

## Holdout Test Metrics

- Accuracy: 0.7143
- Macro precision: 0.6667
- Macro recall: 0.6667
- Macro F1: 0.6667
- Weighted F1: 0.7143

## Comparison vs Previous Active Baseline

- Previous active model: `random_forest` on `zone_mean_only`
- Previous test accuracy: 0.7143
- Previous test macro F1: 0.4643
- Accuracy delta: 0.0000
- Macro F1 delta: 0.2024

## Final Class Distribution

{'Jagung': 13, 'Teff': 12, 'Gandum': 4, 'Jelai': 4}

## Deployment Note

Artifact baru disimpan terpisah agar tidak mengganti model API aktif secara diam-diam. Model baru siap dipakai oleh API jika path artifact diarahkan ke file `*_id.joblib` dan environment runtime memuat dependency yang relevan.
