# Zone Modeling Strategy

## Dataset Audit

- Raw training source: `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- Initial data structure: point-based sampling records.
- Explicit `zone_id` in raw data: no
- Explicit `field_id` in raw data: no
- Latitude/longitude: no
- X/Y coordinates: no
- Sample ID: no
- Sampling time: no
- Depth: no
- Target label present: yes (`target_crop`)

Available high-signal columns include soil chemistry (`Ph`, `N`, `P`, `K`, `Zn`, `S`), soil color, and repeated weather signatures.

## Decision

1. Zona belum tersedia secara eksplisit di dataset mentah.
2. Zona perlu dibentuk agar pipeline tidak lagi memperlakukan satu titik sebagai representasi seluruh lahan.
3. Karena koordinat dan field boundary tidak tersedia, zona dibentuk dengan strategi fallback yang masih defensible:
   - langkah 1: bentuk `base_context_id` dari kombinasi signature cuaca yang identik
   - langkah 2: di dalam setiap `base_context_id`, cluster titik berdasarkan fitur tanah `ph`, `nitrogen`, `phosphorus`, `potassium`, `zinc`, `sulfur`
   - langkah 3: setiap cluster menjadi satu `zone_id`
4. Target zona cocok untuk framing klasifikasi multiclass setelah disaring berdasarkan dominasi label titik.

## Zone Construction Rules

- Jumlah base context terdeteksi: 16
- Jumlah kandidat zona hasil clustering: 153
- Jumlah zona final yang lolos filtering: 33
- Target zone size: 25 titik
- Minimum titik per zona: 8
- Minimum dominant label ratio: 0.60
- Minimum jumlah zona per kelas target: 3

## Zone Label Rule

- Label zona = label titik dominan di dalam zona.
- Zona ambigu tidak dipakai untuk training bila dominant label ratio < 0.60.
- Kelas yang hanya muncul pada sangat sedikit zona juga dibuang agar evaluasi supervised tetap defensible.

## Why This Is A Fallback

- Zona yang dibentuk bukan zona geospasial resmi karena dataset mentah tidak punya koordinat atau batas lahan.
- Namun, pembentukan zona ini tetap lebih realistis daripada memakai satu titik sebagai satu unit rekomendasi, karena beberapa titik dengan konteks agroklimat yang sama digabung dan variasi internal tanah dipertahankan.

## Risks

- The source dataset does not contain latitude/longitude, field_id, sampling time, or explicit zone_id.
- Constructed zones are pseudo-zones in feature/context space, not verified cadastral or geospatial zones.
- Weather variability inside a constructed zone is almost zero because base contexts were defined from repeated weather signatures.
- Zone labels are derived from dominant point labels and therefore inherit label noise from mixed zones.
- The final zone dataset is concentrated in the retained classes: Maize, Teff, Wheat, Barley.

## Source Columns

- soil_color
- ph
- potassium
- phosphorus
- nitrogen
- zinc
- sulfur
- QV2M-W
- QV2M-Sp
- QV2M-Su
- QV2M-Au
- T2M_MAX-W
- T2M_MAX-Sp
- T2M_MAX-Su
- T2M_MAX-Au
- T2M_MIN-W
- T2M_MIN-Sp
- T2M_MIN-Su
- T2M_MIN-Au
- PRECTOTCORR-W
- PRECTOTCORR-Sp
- PRECTOTCORR-Su
- PRECTOTCORR-Au
- wind_speed_10m
- soil_moisture_surface
- cloud_amount
- wind_speed_range_2m
- surface_pressure
- target_crop
- base_context_id
- source_dataset
- point_id
- specific_humidity_mean
- temperature_mean
- temperature_seasonal_range
- rainfall_mean
- rainfall_total_proxy
- zone_id
- context_sample_count
- context_cluster_count
## Modeling Results

- Point-based or zone-based raw data: point-based
- Final zone model framing: multiclass classification on zone labels
- Compared scenarios:
  - point-to-zone baseline
  - zone mean-only
  - zone mean + variability
- Best point baseline test macro F1: 0.6667
- Best zone mean-only test macro F1: 0.4643
- Best zone variability test macro F1: 0.3810
- Selected production zone scenario: `zone_mean_only`
- Variability features improved test macro F1: False
- Zone model outperformed point-to-zone baseline on test macro F1: False
