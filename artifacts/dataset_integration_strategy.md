# Dataset Integration Strategy

## Integration Outcome

Pendekatan yang dipakai adalah **harmonisasi schema + concat zone datasets**, bukan merge row-level antar sumber.

## Why Direct Merge Was Rejected

- Dataset zona aktif sudah berada pada level zona, sedangkan source tambahan utama berada pada level titik.
- Tidak ada primary key, field boundary, atau koordinat yang bisa dipakai untuk merge baris-ke-baris dengan dataset aktif.
- Karena itu, source tambahan diubah dulu menjadi pseudo-zone yang konsisten secara metodologis.

## Main Pipeline

1. Ambil dataset zona aktif sebagai anchor.
2. Ambil dataset crop recommendation bergaya Kaggle pada level titik.
3. Bentuk `base_context_id` dari bin kuantil `temperature`, `rainfall`, dan `humidity`.
4. Di dalam setiap konteks, cluster titik berdasarkan `ph`, `nitrogen`, `phosphorus`, dan `potassium`.
5. Bentuk `zone_id`, lalu hitung agregat zona.
6. Pertahankan hanya zona dengan:
   - minimal 8 titik
   - dominant label ratio minimal 0.60
   - minimal 3 zona per kelas
7. Harmonisasi ke schema zona bersama.
8. Concat dengan dataset zona aktif.

## Unified Schema

Fitur inti yang dipertahankan pada dataset final:

- zone_id
- base_context_id
- source_dataset
- source_region
- integration_strategy
- sample_count
- context_sample_count
- context_cluster_count
- sample_count_risk_flag
- label_nunique
- zone_label_dominance_ratio
- ph_mean
- ph_std
- ph_min
- ph_max
- ph_median
- ph_count
- ph_range
- ph_cv
- ph_missing_ratio
- nitrogen_mean
- nitrogen_std
- nitrogen_min
- nitrogen_max
- nitrogen_median
- nitrogen_count
- nitrogen_range
- nitrogen_cv
- nitrogen_missing_ratio
- phosphorus_mean
- phosphorus_std
- phosphorus_min
- phosphorus_max
- phosphorus_median
- phosphorus_count
- phosphorus_range
- phosphorus_cv
- phosphorus_missing_ratio
- potassium_mean
- potassium_std
- potassium_min
- potassium_max
- potassium_median
- potassium_count
- potassium_range
- potassium_cv
- potassium_missing_ratio
- temperature_mean_mean
- temperature_mean_std
- temperature_mean_min
- temperature_mean_max
- temperature_mean_median
- temperature_mean_count
- temperature_mean_range
- temperature_mean_cv
- temperature_mean_missing_ratio
- rainfall_mean_mean
- rainfall_mean_std
- rainfall_mean_min
- rainfall_mean_max
- rainfall_mean_median
- rainfall_mean_count
- rainfall_mean_range
- rainfall_mean_cv
- rainfall_mean_missing_ratio

## Feature Compatibility Decisions

- `humidity` dari Kaggle **tidak** dibawa ke schema final karena fitur aktif yang serupa adalah `specific_humidity_mean`, dan semantik keduanya tidak aman untuk disamakan langsung.
- `rainfall` dipertahankan karena tersedia pada dataset aktif dan Kaggle.
- `zinc`, `sulfur`, `soil_color`, `soil_moisture_surface`, dan fitur lain yang tidak overlap antar sumber tidak dipakai pada schema final utama.

## Source Composition

{'crop_recommendation_kaggle_mirror': 44, 'mendeley_8v757rr4st_crop_recommendation_soil_weather': 33}

## Consequence

Dataset final lebih sempit pada sisi fitur dibanding dataset zona aktif asli, tetapi lebih kuat untuk ekspansi label karena hanya mempertahankan fitur yang benar-benar kompatibel secara lintas sumber.
