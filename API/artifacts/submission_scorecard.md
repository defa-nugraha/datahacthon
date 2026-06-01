# Submission Scorecard

Dokumen ini adalah **penilaian internal heuristik** terhadap submission saat ini setelah audit model dan perubahan pendukung.

## Ringkasan Skor

- Metodologi dan Eksplorasi Data: **21/25**
- Performa Model dan Kualitas Kode: **22/25**
- Pemanfaatan AI dan Layanan Microsoft Azure: **22/30**
- Insight dan Solusi Strategis: **17/20**
- Total indikatif: **82/100**

## 1. Metodologi dan Eksplorasi Data

Nilai: **21/25**

Alasan utama:
- Sudah memakai framing zona, bukan satu titik, dan split evaluasi memakai `base_context_id`.
- Merge dataset tambahan terdokumentasi dan tidak dilakukan secara sembarangan.
- Fitur aktif model cukup bersih dan overlap antarsumber dijaga.

Gap yang masih menahan skor:
- Anchor data masih bukan zona lapangan Indonesia yang eksplisit.
- Masih ada `13` kelas dengan support sangat kecil pada holdout evaluation.
- EDA sudah lebih rapi, tetapi insight spasial dan validasi unit antar-sumber masih belum setara studi lapangan penuh.

## 2. Performa Model dan Kualitas Kode

Nilai: **22/25**

Metrik utama model terpilih:
- Accuracy: **0.8750**
- Macro precision: **0.8205**
- Macro recall: **0.8462**
- Macro F1: **0.8308**
- Weighted F1: **0.8417**
- Group-aware CV macro F1: **0.8057**

Alasan utama:
- Seleksi model memakai macro F1 dan group-aware CV, bukan accuracy saja.
- Artifact evaluasi sudah lengkap: confusion matrix, classification report, per-class metrics, feature importance.
- Kode pipeline modular dan inference tidak mengubah kontrak feature order model.

Gap yang masih menahan skor:
- CV efektif masih hanya 2 fold karena ukuran data dan constraint group.
- Performa holdout bagus, tetapi robustness antar-domain tetap dibatasi ukuran dataset.

## 3. Pemanfaatan AI dan Layanan Microsoft Azure

Nilai: **22/30**

Kekuatan:
- Service inference sekarang mendukung **Azure OpenAI** sebagai lapisan strategic advisor di atas model tabular.
- Integrasi dirancang dengan **API key** maupun **Microsoft Entra ID**.
- Structured output dipakai agar respons AI bisa tetap terparse secara deterministik.

Gap yang masih menahan skor:
- Integrasi Azure masih bersifat **optional runtime**, belum dibuktikan sebagai deployment Azure produksi.
- Belum ada konfigurasi Azure ML online endpoint, monitoring, atau observability Azure native pada repo ini.
- Belum ada bukti operasional biaya, latency, dan fallback policy di environment Azure nyata.

## 4. Insight dan Solusi Strategis

Nilai: **17/20**

Kekuatan:
- Model tidak hanya memberi label, tetapi bisa diterjemahkan menjadi rekomendasi aksi strategis berbasis zona.
- Insight kini bisa dihasilkan melalui endpoint strategis dengan fokus monitoring, risiko, dan rencana tindakan.
- Fitur paling berpengaruh saat ini: ['sample_count', 'ph_count', 'ph_min', 'nitrogen_missing_ratio', 'nitrogen_range']

Gap yang masih menahan skor:
- Insight masih sangat tergantung pada kualitas pseudo-zone dan belum tervalidasi dengan agronom lapangan Indonesia.
- Belum ada feedback loop pengguna atau dampak ekonomi/agronomi pasca rekomendasi.

## Prioritas Peningkatan Berikutnya

1. Deploy inference API ke **Azure Machine Learning Online Endpoint** atau App Service/Container Apps agar pemanfaatan Azure tidak hanya optional.
2. Tambah data zona Indonesia yang benar-benar punya batas field, geolokasi, dan histori tindakan lapangan.
3. Tambah evaluasi robustness antarsumber dan kalibrasi probabilitas model.
4. Hubungkan strategic advisor ke log observability agar bisa dievaluasi kualitas rekomendasinya dari waktu ke waktu.

## Sumber Internal yang Dipakai

- `artifacts/best_model_metrics_expanded.json`
- `artifacts/model_selection_analysis_expanded.md`
- `data/processed/zone_dataset_expanded_id_metadata.json`
- `artifacts/per_class_metrics_expanded.csv`
- `artifacts/feature_importance_best_model_expanded.csv`
