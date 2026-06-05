# Final Round Readiness

Dokumen ini merangkum area penyempurnaan Vera AI dari prototype menuju demo final yang lebih siap dinilai.

## Status Saat Ini

- Arsitektur sudah dipisah menjadi `API` dan `INTERFACE`.
- Model aktif sudah menggunakan sistem zona, bukan satu titik sensor.
- API sudah memiliki endpoint prediksi zona dan endpoint saran penanganan.
- Laravel sudah memiliki dashboard petani/admin, workflow zona, sampling, rekomendasi, dan care advice.
- Docker Compose root sudah tersedia untuk menjalankan stack lokal.
- Artifact model expanded tersedia dan menggunakan label Bahasa Indonesia.

## Prioritas Penyempurnaan Paling Berdampak

1. Validasi end-to-end demo: login, tambah zona, input sampling, rekomendasi tanaman, pilih tanaman, generate saran penanganan, dan refresh berkala.
2. Dokumentasi deployment Azure: pastikan perintah build/push/revision update jelas dan tidak bergantung pada asumsi lokal.
3. Observability dasar: health check API, status koneksi Laravel ke API, dan error message yang jelas ketika Azure OpenAI tidak aktif.
4. Kebersihan repository: jangan track `.env`, virtualenv, cache, log, SQLite runtime, `vendor`, dan `node_modules`.
5. Transparansi model: tampilkan bahwa rekomendasi berbasis dataset terbatas, metrik validasi, dan confidence/top-k agar tidak terlihat sebagai klaim absolut.
6. UX demo: alur petani harus pendek, jelas, dan tidak membuat juri mencari tombol utama.

## Risiko Yang Perlu Dijelaskan Saat Presentasi

- Dataset expanded menggabungkan dataset zona aktif dan dataset crop recommendation tambahan, sehingga ada risiko domain shift.
- Beberapa kelas memiliki jumlah zona kecil; macro F1 lebih relevan daripada accuracy saja.
- Rekomendasi AI penanganan adalah advisory, bukan pengganti rekomendasi agronom profesional.
- SQLite cukup untuk demo dan deployment ringan, tetapi production multi-user idealnya memakai managed database.

## Checklist Sebelum Demo

- Jalankan `docker compose config --quiet`.
- Jalankan test API dengan `pytest` di folder `API`.
- Jalankan test Laravel dengan `php artisan test` di folder `INTERFACE`.
- Pastikan `/health` API berstatus `ok`.
- Pastikan `/model/info` mengarah ke `best_zone_model_expanded.joblib`.
- Pastikan login demo berhasil untuk admin dan petani.
- Pastikan minimal satu workflow demo bisa selesai tanpa seed ulang manual.
- Pastikan environment Azure tidak memakai `APP_DEBUG=true`.

## Narasi Teknis Singkat

Vera AI tidak menganggap satu titik sensor mewakili seluruh lahan. Beberapa titik sampling dikumpulkan dalam satu zona, lalu sistem menghitung agregasi statistik untuk menangkap kondisi rata-rata dan variasi internal zona. Representasi zona tersebut masuk ke model klasifikasi tabular untuk menghasilkan rekomendasi tanaman. Setelah petani memilih tanaman, sistem dapat mengirim ringkasan kondisi tanah terbaru ke endpoint advisory untuk menghasilkan saran penanganan berbasis Azure OpenAI atau fallback lokal.
