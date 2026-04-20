<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class SoilDataController extends Controller
{
    public function index()
    {
        $chartData = [ /* ... data chart lu kemaren ... */ ];

        // Ambil data tanaman aktif dari session (kalo ga ada, isinya bakal null)
        $activePlant = session('activePlant');

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

    public function history()
    {
        // Mengambil semua data, diurutkan dari yang terbaru, dan tambahkan pagination
        $historicalData = \App\Models\SoilData::orderBy('created_at', 'desc')->paginate(10);
        
        return view('history', compact('historicalData'));
    }

    public function startPlanting(Request $request)
    {
        // Tangkep ID/Nama tanaman dari tombol yang diklik
        $cropId = $request->input('crop_id'); // Misal: 1 buat Tomat, 2 Jagung

        // Simulasi data tanaman berdasarkan pilihan
        $plantData = [];
        if ($cropId == 1) {
            $plantData = ['nama' => 'Tomat Sayur', 'estimasi_panen' => 83];
        } elseif ($cropId == 2) {
            $plantData = ['nama' => 'Jagung Manis', 'estimasi_panen' => 60];
        } else {
            $plantData = ['nama' => 'Cabai Merah', 'estimasi_panen' => 90];
        }

        // Siapin data lengkap buat disimpen di Session
        $activePlant = [
            'nama' => $plantData['nama'],
            'tanggal_tanam' => now()->format('d M Y'),
            'hari_ke' => 1,
            'estimasi_panen' => $plantData['estimasi_panen'],
            'progress' => 1 // Baru hari pertama
        ];

        // Simpan ke Session Laravel
        session(['activePlant' => $activePlant]);

        // Balikin ke Dashboard dengan pesan sukses
        return redirect()->route('dashboard')->with('success', 'Berhasil memulai penanaman ' . $plantData['nama'] . '!');
    }

    public function resetPlanting()
    {
        // Hapus data tanaman dari session (Buat simulasi "Selesai Panen")
        session()->forget('activePlant');
        return redirect()->route('dashboard')->with('success', 'Lahan berhasil di-reset. Siap untuk penanaman baru.');
    }

    public function zones()
    {
        // Simulasi data perangkat IoT di berbagai zona
        $iotDevices = [
            [
                'zona' => 'Zona A (Utara)',
                'mac_address' => 'ESP32-A8:4F:23',
                'status' => 'Online',
                'last_ping' => 'Barusan',
                'tanaman' => 'Tomat Sayur'
            ],
            [
                'zona' => 'Zona B (Selatan)',
                'mac_address' => 'ESP32-B2:11:9C',
                'status' => 'Offline',
                'last_ping' => '2 Jam yang lalu',
                'tanaman' => 'Belum ditanam'
            ],
            [
                'zona' => 'Zona C (Timur)',
                'mac_address' => 'Belum ada alat',
                'status' => 'Menunggu Setup',
                'last_ping' => '-',
                'tanaman' => 'Belum ditanam'
            ]
        ];

        return view('zones', compact('iotDevices'));
    }
}
