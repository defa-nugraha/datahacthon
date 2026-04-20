@extends('layouts.app')

@section('title', 'Dashboard - Agro Smart')

@section('content')

    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold text-green-700 mb-8">Dashboard Precision Agriculture</h1>

        @if(session('success'))
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4 shadow-sm">
                {{ session('success') }}
            </div>
        @endif

        @if(isset($activePlant) && $activePlant != null)
            
            <div class="w-full bg-gradient-to-r from-green-600 to-green-800 rounded-2xl shadow-lg p-6 mb-8 text-white relative overflow-hidden">
                <div class="relative z-10 flex flex-col md:flex-row justify-between items-center gap-6">
                    <div class="flex items-center gap-6 w-full md:w-1/2">
                        <div class="bg-white/20 p-4 rounded-xl text-4xl">🍅</div>
                        <div>
                            <span class="text-green-200 text-sm font-bold tracking-wider uppercase">Fase Vegetatif</span>
                            <h2 class="text-3xl font-black mt-1">{{ $activePlant['nama'] }} (Zona A)</h2>
                            <p class="text-green-100 mt-1">Ditanam pada: {{ $activePlant['tanggal_tanam'] }}</p>
                        </div>
                    </div>
                    <div class="w-full md:w-1/2 bg-black/20 rounded-xl p-4">
                        <div class="flex justify-between text-sm font-bold mb-2">
                            <span>Hari ke-{{ $activePlant['hari_ke'] }}</span>
                            <span class="text-green-300">Estimasi Panen: {{ $activePlant['estimasi_panen'] }} Hari Lagi</span>
                        </div>
                        <div class="w-full bg-black/30 rounded-full h-3 mb-2">
                            <div class="bg-green-400 h-3 rounded-full" style="width: {{ $activePlant['progress'] }}%"></div>
                        </div>
                    </div>
                </div>
            </div>

            <form action="{{ route('plant.reset') }}" method="POST" class="mb-8">
                @csrf
                <button type="submit" class="text-red-500 hover:text-red-700 text-sm font-bold underline">
                    Akhiri Masa Tanam (Reset Lahan)
                </button>
            </form>

        @else
            
            <div class="w-full bg-white p-6 rounded-lg shadow-md border-t-4 border-green-500 mb-8">
                <div class="flex justify-between items-center mb-6 border-b pb-4">
                    <h2 class="text-xl font-bold text-gray-800">Monitoring Lahan (Real-time IoT)</h2>
                    <span class="text-sm font-semibold text-green-700 bg-green-50 px-3 py-1 rounded-full">● Sensor Aktif</span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div class="bg-gray-50 rounded-lg p-4 text-center border border-gray-100"><p class="text-sm text-gray-500">Nitrogen</p><p class="text-2xl font-bold text-blue-600">42</p></div>
                    <div class="bg-gray-50 rounded-lg p-4 text-center border border-gray-100"><p class="text-sm text-gray-500">Fosfor</p><p class="text-2xl font-bold text-blue-600">15</p></div>
                    <div class="bg-gray-50 rounded-lg p-4 text-center border border-gray-100"><p class="text-sm text-gray-500">Kalium</p><p class="text-2xl font-bold text-blue-600">120</p></div>
                    <div class="bg-gray-50 rounded-lg p-4 text-center border border-gray-100"><p class="text-sm text-gray-500">pH</p><p class="text-2xl font-bold text-blue-600">6.2</p></div>
                </div>
            </div>

            <div class="w-full bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-xl font-semibold mb-4 border-b pb-2">Input Manual Unsur Hara</h2>
                <form action="{{ route('analyze.manual') }}" method="POST" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    @csrf
                    <div><label class="text-sm font-bold">Nitrogen (N)</label><input type="number" name="nitrogen" class="w-full border rounded p-2" required></div>
                    <div><label class="text-sm font-bold">Fosfor (P)</label><input type="number" name="phosphorus" class="w-full border rounded p-2" required></div>
                    <div><label class="text-sm font-bold">Kalium (K)</label><input type="number" name="potassium" class="w-full border rounded p-2" required></div>
                    <div><label class="text-sm font-bold">pH Tanah</label><input type="number" step="0.1" name="ph" class="w-full border rounded p-2" required></div>
                    <div class="md:col-span-4 mt-2">
                        <button type="submit" class="bg-green-600 text-white font-bold py-2 px-4 rounded w-full md:w-auto">Cek Rekomendasi AI</button>
                    </div>
                </form>
            </div>

        @endif

        <div class="w-full bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4 border-b pb-2">Tren Kualitas Tanah (7 Hari)</h2>
            <div class="relative h-80 w-full">
                <canvas id="soilChart"></canvas>
            </div>
        </div>

    </div>

    <script>
        window.soilData = @json($chartData ?? []);
    </script>
    <script src="{{ asset('js/dashboard-chart.js') }}"></script>

@endsection