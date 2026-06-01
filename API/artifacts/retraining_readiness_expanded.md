# Retraining Readiness (Expanded)

## Dataset Size

- Total zones: 77
- Total classes: 13
- Class distribution: {'Jagung': 17, 'Teff': 12, 'Padi': 6, 'Pisang': 6, 'Kelapa': 5, 'Mangga': 5, 'Gandum': 4, 'Jelai': 4, 'Jeruk': 4, 'Semangka': 4, 'Kopi': 4, 'Kacang Hijau': 3, 'Pepaya': 3}

## Readiness Assessment

- Supervised learning framing: **layak**, sebagai multiclass classification pada level zona.
- Main metric recommendation: **macro F1**, karena distribusi kelas masih tidak seimbang dan jumlah zona per kelas kecil.
- Split recommendation: **group-aware holdout + group CV** memakai `base_context_id`.

## Data Quality Notes

- Fitur final dibatasi pada overlap antar sumber, sehingga completeness tinggi pada fitur yang dipakai untuk training.
- Kelas tambahan dari Kaggle bukan zona geospasial nyata; mereka adalah pseudo-zones berbasis climate-context + soil clustering.
- Kelas baru dari dataset CTGAN Tamil Nadu tidak dimasukkan ke merge utama karena risiko domain dan semantic mismatch masih terlalu besar.

## Recommendation

Retraining **boleh dilakukan** untuk baseline ekspansi tahap 2, tetapi hasilnya harus diposisikan sebagai:

1. baseline eksploratif untuk ekspansi kelas Indonesia-relevant
2. belum setara dengan model produksi yang telah divalidasi pada zona lapangan Indonesia

## Main Risks

- The active anchor data is still Ethiopian and pseudo-zone based, not Indonesia field data.
- The Kaggle source is a benchmark dataset and not a geospatially explicit zone dataset.
- The merged dataset now mixes native pseudo-zones and externally constructed pseudo-zones.
- Several added classes still have only 3-6 zones, so per-class robustness remains limited.
- Requested crops such as Kedelai, Kacang Tanah, Tebu, Cabai, and Bawang Merah were found in a CTGAN-augmented source, but were intentionally excluded from the main merge because the semantic risk was too high.
