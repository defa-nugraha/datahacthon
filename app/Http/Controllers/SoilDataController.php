<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class SoilDataController extends Controller
{
    public function index()
    {
        // 1. Data dummy buat grafik (yang kemaren)
        $chartData = [
            'labels' => ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Hari Ini'],
            'nitrogen' => [30, 32, 35, 40, 42, 45, 42],
            'phosphorus' => [10, 12, 11, 14, 15, 14, 15],
            'potassium' => [110, 115, 112, 118, 120, 122, 120],
            'ph' => [5.8, 5.9, 6.0, 6.1, 6.1, 6.2, 6.2]
        ];

        // 2. Simulasi Status Tanaman Aktif
        // Kalo lu mau ngetes tampilan biasa (belum nanam), ganti jadi: $activePlant = null;
        $activePlant = [
            'nama' => 'Tomat Sayur',
            'tanggal_tanam' => '12 April 2026',
            'hari_ke' => 7,
            'estimasi_panen' => 83,
            'progress' => 15 // dalam persen
        ];

        return view('welcome', compact('chartData', 'activePlant'));
    }

    public function analyzeManual(Request $request)
    {
        // Tembak API Python lu
        $response = Http::post('http://127.0.0.1:5000/predict', [
            'nitrogen' => $request->nitrogen,
            'phosphorus' => $request->phosphorus,
            'potassium' => $request->potassium,
            'ph' => $request->ph
        ]);

        // Tangkep format JSON dari Python lu
        $aiRecommendations = $response->json();

        // Lempar ke halaman rekomendasi
        return view('recommendation', compact('aiRecommendations'));
    }
}
