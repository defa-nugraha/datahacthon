@extends('layouts.app')
@section('title', 'Riwayat Data - Agro Smart')

@section('content')
<div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center mb-8">
            <div>
                <h1 class="text-3xl font-bold text-gray-800">Riwayat Sensor & Analisis</h1>
                <p class="text-gray-500 mt-1">Pantau tren kualitas tanah secara mendetail.</p>
            </div>
            
            <div class="mt-4 md:mt-0 flex gap-4">
                <a href="{{ route('welcome') }}" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded transition">
                    Kembali ke Dashboard
                </a>
                <button class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded shadow transition flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Export CSV
                </button>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-md overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-green-700 text-white text-sm uppercase tracking-wider">
                            <th class="p-4 font-semibold">Tanggal / Waktu</th>
                            <th class="p-4 font-semibold text-center">Zona</th>
                            <th class="p-4 font-semibold text-center">N (mg/kg)</th>
                            <th class="p-4 font-semibold text-center">P (mg/kg)</th>
                            <th class="p-4 font-semibold text-center">K (mg/kg)</th>
                            <th class="p-4 font-semibold text-center">pH</th>
                            <th class="p-4 font-semibold">Status AI</th>
                        </tr>
                    </thead>
                    <tbody class="text-gray-700 text-sm">
                        @forelse($historicalData as $data)
                        <tr class="border-b hover:bg-gray-50 transition">
                            <td class="p-4">{{ $data->created_at->format('d M Y, H:i') }}</td>
                            <td class="p-4 text-center font-medium">{{ $data->zone_name ?? 'N/A' }}</td>
                            <td class="p-4 text-center">{{ $data->nitrogen }}</td>
                            
                            <td class="p-4 text-center {{ $data->phosphorus < 20 ? 'text-red-600 font-bold' : '' }}">
                                {{ $data->phosphorus }}
                            </td>
                            
                            <td class="p-4 text-center">{{ $data->potassium }}</td>
                            
                            <td class="p-4 text-center font-bold {{ $data->ph < 6 ? 'text-orange-500' : 'text-green-600' }}">
                                {{ $data->ph }}
                            </td>
                            
                            <td class="p-4">
                                @if($data->ph < 6)
                                    <span class="bg-orange-100 text-orange-700 py-1 px-2 rounded-full text-xs font-bold">⚠️ Perlu Pengapuran</span>
                                @elseif($data->phosphorus < 20)
                                    <span class="bg-red-100 text-red-700 py-1 px-2 rounded-full text-xs font-bold">❗ P Kritis</span>
                                @else
                                    <span class="bg-green-100 text-green-700 py-1 px-2 rounded-full text-xs font-bold">✅ Optimal</span>
                                @endif
                            </td>
                        </tr>
                        @empty
                        <tr>
                            <td colspan="7" class="p-8 text-center text-gray-500">
                                Belum ada data sensor yang masuk.
                            </td>
                        </tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
            
            <div class="p-4 border-t bg-gray-50">
                {{ $historicalData->links() }}
            </div>
        </div>

    </div>
@endsection