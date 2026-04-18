# Audit Label Indonesia

## Dataset Aktif

- File sumber zona aktif: `data/processed/zone_dataset_extended.csv`
- File output label Indonesia: `data/processed/zone_dataset_extended_id.csv`
- Target column aktif: `zone_target`
- Unique labels aktif: ['Gandum', 'Jagung', 'Jelai', 'Teff']
- Distribusi label aktif: {'Jagung': 13, 'Teff': 12, 'Gandum': 4, 'Jelai': 4}

## Mapping Label ke Bahasa Indonesia

- Barley -> Jelai
- Maize -> Jagung
- Teff -> Teff
- Wheat -> Gandum

## Audit Source Data

- Source dataset: `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- Label titik setelah normalisasi: {'Teff': 1260, 'Maize': 732, 'Wheat': 715, 'Barley': 503, 'Bean': 253, 'Pea': 94, 'Sorghum': 72, 'Dagussa': 71, 'Niger Seed': 64, 'Potato': 48, 'Red Pepper': 29}
- Kandidat label di level zona sebelum filter kualitas: {'Teff': 52, 'Maize': 45, 'Wheat': 24, 'Barley': 19, 'Bean': 6, 'Sorghum': 3, 'Potato': 2, 'Pea': 1, 'Red Pepper': 1}
- Label final yang lolos filter kualitas dan support kelas: {'Maize': 13, 'Teff': 12, 'Wheat': 4, 'Barley': 4}

## Temuan Penting

1. Source data titik memang mengandung label tambahan seperti `Bean`, `Pea`, `Sorghum`, `Dagussa`, `Niger Seed`, `Potato`, dan `Red Pepper`.
2. Tidak ada label tambahan tersebut yang lolos sampai dataset zona final aktif. Setelah filter kualitas zona dan minimum support kelas, hanya empat label yang tersisa.
3. Beberapa label tambahan tidak bisa dipetakan langsung ke tanaman umum Indonesia secara sah. Contoh: `Bean` terlalu ambigu untuk dipaksa menjadi `Kedelai` atau `Kacang Tanah`.
4. Label yang masih tersisa dapat diterjemahkan ke Bahasa Indonesia tanpa mengubah makna agronominya.

## Hidden / Non-Retained Candidates

{'Bean': 253, 'Pea': 94, 'Sorghum': 72, 'Dagussa': 71, 'Niger Seed': 64, 'Potato': 48, 'Red Pepper': 29}
