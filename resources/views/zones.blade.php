@extends('layouts.app')
@section('title', 'Manajemen Perangkat - Agro Smart')

@section('content')
<div class="max-w-6xl mx-auto">

    <div class="flex flex-col md:flex-row justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-bold text-gray-800">Manajemen Perangkat IoT</h1>
            <p class="text-gray-500 mt-1">Pantau status koneksi sensor di setiap zona lahan Anda.</p>
        </div>
        <button class="mt-4 md:mt-0 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-lg shadow transition flex items-center gap-2">
            <span>➕</span> Tambah Alat Baru
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        @foreach($iotDevices as $device)
        <div class="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
            
            <div class="p-4 border-b flex justify-between items-center bg-gray-50">
                <h2 class="text-lg font-bold text-gray-800">{{ $device['zona'] }}</h2>
                
                @if($device['status'] == 'Online')
                    <span class="flex items-center gap-1 text-xs font-bold text-green-700 bg-green-100 px-2 py-1 rounded-full">
                        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Online
                    </span>
                @elseif($device['status'] == 'Offline')
                    <span class="flex items-center gap-1 text-xs font-bold text-red-700 bg-red-100 px-2 py-1 rounded-full">
                        <span class="w-2 h-2 rounded-full bg-red-500"></span> Offline
                    </span>
                @else
                    <span class="flex items-center gap-1 text-xs font-bold text-gray-600 bg-gray-200 px-2 py-1 rounded-full">
                        Setup
                    </span>
                @endif
            </div>

            <div class="p-5 space-y-3">
                <div>
                    <p class="text-xs text-gray-500 font-semibold uppercase">ID Perangkat / MAC</p>
                    <p class="text-sm font-mono bg-gray-100 p-1 rounded mt-1 text-gray-700">{{ $device['mac_address'] }}</p>
                </div>
                
                <div class="flex justify-between border-t pt-3">
                    <div>
                        <p class="text-xs text-gray-500 font-semibold uppercase">Status Lahan</p>
                        <p class="text-sm font-bold text-gray-800">{{ $device['tanaman'] }}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-xs text-gray-500 font-semibold uppercase">Update Terakhir</p>
                        <p class="text-sm text-gray-600">{{ $device['last_ping'] }}</p>
                    </div>
                </div>
            </div>

            <div class="p-4 bg-gray-50 border-t flex gap-2">
                <button class="flex-1 bg-white border border-gray-300 text-gray-700 text-sm font-bold py-2 rounded hover:bg-gray-100 transition">Pengaturan</button>
                <button class="flex-1 bg-white border border-red-300 text-red-600 text-sm font-bold py-2 rounded hover:bg-red-50 transition">Restart</button>
            </div>

        </div>
        @endforeach
    </div>

</div>
@endsection