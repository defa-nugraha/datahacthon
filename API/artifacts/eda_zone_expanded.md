# EDA Zone Expanded Summary

## Dataset Snapshot

- Dataset: `data/processed/zone_dataset_expanded_id.csv`
- Total zona: 77
- Total kelas: 13
- Fitur aktif skenario terpilih (`zone_mean_plus_variability`): 57
- Distribusi sumber: {'crop_recommendation_kaggle_mirror': 44, 'mendeley_8v757rr4st_crop_recommendation_soil_weather': 33}
- Rasio imbalance support terbesar/terkecil: 4.00

## Distribusi Kelas

zone_target
Jagung          17
Teff            12
Padi             6
Pisang           6
Kelapa           5
Mangga           5
Gandum           4
Jelai            4
Jeruk            4
Semangka         4
Kopi             4
Kacang Hijau     3
Pepaya           3

## Kualitas Fitur

- Missing rate rata-rata fitur aktif: 0.0000
- Missing rate maksimum fitur aktif: 0.0000
- 10 fitur dengan missing tertinggi:

sample_count             0.0
context_sample_count     0.0
context_cluster_count    0.0
ph_mean                  0.0
ph_std                   0.0
ph_min                   0.0
ph_max                   0.0
ph_median                0.0
ph_count                 0.0
ph_range                 0.0

## Risiko Data

- Pseudo-zone aktif tetap bercampur antara anchor data Ethiopia dan pseudo-zone benchmark eksternal.
- `base_context_id` sudah dipakai sebagai group split sehingga kebocoran antarkonteks ditekan.
- Beberapa kelas masih low-support (`3-6` zona) sehingga macro F1 lebih relevan dibanding accuracy tunggal.

## Implikasi Metodologis

- Problem framing multiclass classification pada level zona masih layak.
- Hasil evaluasi perlu dibaca sebagai baseline yang valid, bukan validasi lapangan Indonesia final.
- Strategi merge saat ini kuat pada overlap fitur inti (`pH`, `N`, `P`, `K`, `temperature`, `rainfall`) namun belum mencakup atribut tanah Indonesia yang lebih kaya seperti CEC, tekstur, atau bahan organik.
