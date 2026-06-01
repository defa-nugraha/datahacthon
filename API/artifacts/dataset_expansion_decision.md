# Dataset Expansion Decision

## Selected Main Integration Sources

- Current active zone dataset
- Crop Recommendation dataset (Kaggle-origin mirror)

## Why These Were Selected

1. **Current active zone dataset** remains the anchor because it is the only dataset already aligned with the current zone-based training pipeline.
2. **Kaggle-origin crop recommendation benchmark** was selected because it overlaps on the core features `N`, `P`, `K`, `pH`, `temperature`, and `rainfall`, and it adds multiple crops that are genuinely common in Indonesia, especially `Rice`.
3. The Kaggle dataset was not merged row-to-row. It was first converted into pseudo-zones using climate-context grouping and soil clustering without using target labels during zone formation.

## Selected Additional Classes

Kelas baru yang benar-benar ditambahkan ke dataset final:

- Padi
- Pisang
- Kelapa
- Kopi
- Mangga
- Jeruk
- Pepaya
- Semangka
- Kacang Hijau

`Jagung` sudah ada sebelumnya dan mendapat tambahan support dari source baru.

## Main Rejections

- **Mendeley vynxnppr7j**: sangat kaya label Indonesia-relevant (`soyabean`, `groundnut`, `sugarcane`, `onion`, `chillies`), tetapi record-nya eksplisit memakai CTGAN dan tidak punya rainfall. Saya simpan sebagai kandidat eksperimen, bukan merge utama.
- **Zenodo rice fertility**: target-nya `fertility`, bukan crop class.
- **GitHub sugarcane yield**: target-nya yield untuk satu crop, bukan multiclass recommendation.
- **Zenodo 17-crop training samples**: sangat menarik untuk `cassava`, `soybean`, `peanut`, `sugarcane`, tetapi masih perlu join spasial soil + climate sebelum valid untuk supervised learning tabular.
- **Gist kecil**: ditolak karena toy-scale dan tidak punya fitur inti.

## Kaggle Contribution

Kaggle berhasil memberi dataset yang **relevan dan usable** untuk ekspansi kelas. Dataset itulah yang menjadi sumber tambahan utama pada tahap ini.

## Pseudo-Zone Diagnostics for Kaggle Source

- Source points retained for selected crops: 1000
- Candidate pseudo-zones: 137
- Final kept pseudo-zones: 44
- Final class distribution from Kaggle pseudo-zones: {'Rice': 6, 'Banana': 6, 'Coconut': 5, 'Mango': 5, 'Maize': 4, 'Orange': 4, 'Watermelon': 4, 'Coffee': 4, 'MungBean': 3, 'Papaya': 3}

## Final Class Distribution After Main Integration

{'Jagung': 17, 'Teff': 12, 'Padi': 6, 'Pisang': 6, 'Kelapa': 5, 'Mangga': 5, 'Gandum': 4, 'Jelai': 4, 'Jeruk': 4, 'Semangka': 4, 'Kopi': 4, 'Kacang Hijau': 3, 'Pepaya': 3}
