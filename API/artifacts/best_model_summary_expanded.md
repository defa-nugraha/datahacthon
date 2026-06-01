# Best Expanded Zone Model Summary

## Final Selection

- Best scenario: `zone_mean_plus_variability`
- Best model: `extra_trees`
- Selection metric: macro F1 on group-aware CV
- Best CV macro F1: 0.8057

## Holdout Test Metrics

- Accuracy: 0.8750
- Macro precision: 0.8205
- Macro recall: 0.8462
- Macro F1: 0.8308
- Weighted F1: 0.8417

## Final Class Distribution

{'Jagung': 17, 'Teff': 12, 'Padi': 6, 'Pisang': 6, 'Kelapa': 5, 'Mangga': 5, 'Gandum': 4, 'Jelai': 4, 'Jeruk': 4, 'Semangka': 4, 'Kopi': 4, 'Kacang Hijau': 3, 'Pepaya': 3}

## Interpretation

- Angka ini tidak bisa dibandingkan langsung dengan baseline 4-kelas lama karena jumlah kelas bertambah dan task menjadi lebih sulit.
- Macro F1 tetap dijadikan acuan utama karena class imbalance dan beberapa kelas baru hanya memiliki 3-6 zona.
- Artifact baru disimpan terpisah agar tidak mengganti model API aktif secara diam-diam.
