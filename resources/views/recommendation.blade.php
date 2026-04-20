@extends('layouts.app')
@section('title', 'Hasil Analisis ML - Agro Smart')

@section('content')
<div class="max-w-6xl mx-auto">
    
    <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-gray-800">Hasil Analisis Model ML</h1>
        <p class="text-gray-600 mt-2">Berdasarkan data hara yang diinput, berikut 3 rekomendasi terbaik beserta risikonya.</p>
    </div>

    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8 flex justify-center gap-6 text-sm">
        <span class="text-blue-800 font-semibold">Data Dianalisis:</span>
        <span class="text-blue-700">Nitrogen: {{ $inputData['nitrogen'] ?? 0 }}</span>
        <span class="text-blue-700">Fosfor: {{ $inputData['phosphorus'] ?? 0 }}</span>
        <span class="text-blue-700">Kalium: {{ $inputData['potassium'] ?? 0 }}</span>
        <span class="text-blue-700">pH: {{ $inputData['ph'] ?? 0 }}</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        @foreach($recommendations as $crop)
        <div class="group relative bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-green-500 overflow-hidden flex flex-col">
            
            <div class="absolute top-4 right-4 z-10">
                <span class="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full border border-green-200">
                    {{ $crop['match_rate'] }}% Match
                </span>
            </div>

            <div class="h-40 bg-gray-50 flex items-center justify-center text-6xl">
                {{ $crop['icon'] }}
            </div>

            <div class="p-6 flex-grow">
                <h3 class="text-xl font-bold text-gray-800 mb-2">{{ $crop['name'] }}</h3>
                
                <div class="mb-4 bg-red-50 p-3 rounded-lg border border-red-100">
                    <span class="text-[10px] font-black text-red-400 uppercase tracking-widest">Risiko Terdeteksi</span>
                    <p class="text-sm text-red-700 font-medium mt-1 leading-relaxed">
                        ⚠ {{ $crop['risk_note'] }}
                    </p>
                </div>

                <div class="space-y-2 mb-6 border-t pt-4">
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Estimasi Panen</span>
                        <span class="font-semibold text-gray-700">{{ $crop['harvest_time'] }} Hari</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">Kebutuhan Air</span>
                        <span class="font-semibold text-gray-700">{{ $crop['water_need'] }}</span>
                    </div>
                </div>
            </div>

            <div class="p-6 pt-0">
                <form action="{{ route('plant.start') }}" method="POST">
                    @csrf
                    <input type="hidden" name="crop_id" value="{{ $crop['id'] }}">
                    <button type="submit" class="w-full bg-gray-900 group-hover:bg-green-600 text-white font-bold py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
                        Mulai Tanam Sekarang
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    </button>
                </form>
            </div>
        </div>
        @endforeach
    </div>

    <div class="text-center mt-8">
        <a href="{{ route('dashboard') }}" class="text-gray-500 hover:text-gray-800 underline">Batalkan & Kembali ke Dashboard</a>
    </div>

</div>
@endsection