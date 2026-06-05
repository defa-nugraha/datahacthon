# Analisis dan Improvement Project Brief Vera AI

## File Dianalisis

- `Salinan dari [METC] Project Brief Template - Datathon.docx`

## Temuan Utama

- Struktur template sudah diikuti: Informasi Peserta, Topik, Ringkasan Eksekutif, Deskripsi Project, Fitur dan Teknologi, Cara Penggunaan, Informasi Pendukung, dan Link Aplikasi/Project.
- Draft lama sudah cukup relevan, tetapi masih memiliki beberapa klaim yang belum selaras dengan implementasi project saat ini.
- Ada typo credential demo: `petani@veraai..test` dan `admin@ veraai. test`.
- Ada klaim penggunaan Azure Functions dan Azure SQL sebagai bagian aktif, padahal project saat ini memakai Laravel/FastAPI container, SQLite untuk demo ringan, Azure OpenAI, Azure Container Apps, ACR, dan opsi Azure IoT Hub.
- Belum memuat fitur terbaru monitoring: pilihan nilai langsung dari MQTT atau rata-rata 5/15/30/60 menit.
- Belum memuat update terbaru integrasi cuaca BMKG: cuaca saat ini, prakiraan 3 hari, dan penggunaan konteks cuaca pada AI Adaptive Advice.
- Belum memuat model forecasting ARIMA dari folder `model-forecasting` yang sudah tersedia sebagai endpoint FastAPI `/forecast/weather`.
- Metrik model perlu dibuat eksplisit agar juri melihat kualitas evaluasi: Extra Trees, accuracy 87,5%, macro F1 83,08%, group-aware evaluation.

## Improvement Yang Dilakukan

- Problem statement diperkuat dengan data Indonesia dari BPS ST2023 dan data padi 2024.
- Ringkasan eksekutif dibuat lebih fokus pada masalah nyata: satu titik sensor tidak mewakili satu zona lahan.
- Deskripsi project diselaraskan dengan pipeline aktif: zone-based recommendation, FastAPI inference, Laravel dashboard, MQTT monitoring, dan Azure OpenAI advice.
- Bagian Azure dikoreksi agar tidak overclaim:
  - Azure Container Apps
  - Azure Container Registry
  - Azure OpenAI Service
  - Azure IoT Hub sebagai opsi production telemetry
  - Azure Files untuk persistensi SQLite demo
  - Azure Monitor/Log Stream untuk observability
- Cara penggunaan diperbarui dengan role admin/petani, monitoring MQTT, dan pilihan rata-rata window.
- Bagian monitoring dan AI advisor diperbarui dengan BMKG public weather API berdasarkan kode wilayah `adm4` per zona.
- Diagram sistem diperbarui dengan komponen ARIMA Forecast API sebagai fitur pendukung terpisah dari rekomendasi utama.
- Diagram sistem diperbarui menjadi lane rekomendasi zona, monitoring MQTT/BMKG/forecasting/notifikasi, adaptive care advice berbasis Azure OpenAI, dan catatan batasan forecasting.
- Link dan credential demo diperbaiki.
- Informasi pendukung diperkuat dengan metodologi ML, insight strategis, keterbatasan, dan rencana pengembangan.

## Output

- `docs/Vera AI - Project Brief Datathon - Improved.docx`
- `docs/vera_ai_current_system_workflow.drawio`
- `docs/vera_ai_current_system_workflow.png`
- `docs/vera_ai_system_workflow.drawio`
- `docs/vera_ai_system_workflow.png`

## Diagram Cara Kerja Sistem

- Diagram dibuat dalam format XML draw.io agar bisa diedit ulang melalui diagrams.net.
- Diagram juga dikonversi menjadi PNG berwarna dan dimasukkan ke dalam file brief.
- Layout diagram terbaru dibuat dalam tiga lane utama:
  - Alur rekomendasi tanaman berbasis zona.
  - Alur monitoring MQTT, cuaca BMKG, endpoint forecasting ARIMA, dan notifikasi batas aman.
  - Alur AI Adaptive Advice yang menerima konteks tanah, tanaman aktif, dan prakiraan cuaca 3 hari.
- Diagram juga menegaskan bahwa `/forecast/weather` memakai artifact ARIMA dari `model-forecasting` untuk prediksi suhu bulanan dan saat ini belum menjadi input utama rekomendasi tanaman.
- Garis penghubung dibuat searah dan dipisahkan per lane untuk menghindari overlap dan tabrakan visual.
