# Keputusan Ekspansi Label Indonesia

## Keputusan

Pendekatan yang dipilih adalah **B**:

- tidak menambahkan kelas baru khas Indonesia ke dataset training aktif
- hanya menerjemahkan label final yang sudah valid ke Bahasa Indonesia
- melatih ulang model pada label terjemahan tersebut

## Alasan

1. Dataset zona aktif yang valid saat ini hanya berisi empat kelas final: {'Maize': 13, 'Teff': 12, 'Wheat': 4, 'Barley': 4}.
2. Label tambahan pada source point data ({'Teff': 1260, 'Maize': 732, 'Wheat': 715, 'Barley': 503, 'Bean': 253, 'Pea': 94, 'Sorghum': 72, 'Dagussa': 71, 'Niger Seed': 64, 'Potato': 48, 'Red Pepper': 29}) tidak bertahan pada level zona dengan kualitas yang memadai.
3. Setelah filter kualitas zona (`min_samples_per_zone >= 8` dan dominant label ratio `>= 0.6`), label yang tersisa tetap hanya {'Maize': 13, 'Teff': 12, 'Wheat': 4, 'Barley': 4}.
4. Tidak ada dasar yang sah untuk mengganti label seperti `Wheat` menjadi `Padi` atau `Barley` menjadi `Singkong`.
5. Label seperti `Bean` terlalu umum dan tidak dapat dipetakan secara aman ke `Kedelai` atau `Kacang Tanah`.

## Implikasi

- Model hasil pembaruan tetap terbatas pada empat tanaman: `Jelai`, `Jagung`, `Teff`, `Gandum`.
- Model belum dapat mengeluarkan rekomendasi untuk `Padi`, `Kedelai`, `Singkong`, `Ubi Jalar`, `Tebu`, `Kacang Tanah`, `Cabai`, atau `Bawang Merah`.

## Data Tambahan yang Dibutuhkan

Untuk mendukung tanaman yang umum di Indonesia secara valid, dibutuhkan salah satu dari:

1. dataset zona dengan label tanaman Indonesia yang eksplisit
2. raw point data dengan label yang jelas dan cukup support untuk membentuk zona berkualitas
3. field/grid geospasial Indonesia yang bisa di-join dengan crop presence atau suitability label yang tervalidasi
