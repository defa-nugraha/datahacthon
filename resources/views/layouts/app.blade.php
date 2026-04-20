<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Agro Smart')</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
</head>
<body class="bg-gray-50 font-sans flex h-screen overflow-hidden">

    <aside class="w-64 bg-green-800 text-white flex flex-col hidden md:flex">
        <div class="p-6 text-center border-b border-green-700">
            <h1 class="text-2xl font-black tracking-wider">🌱 AgroSmart</h1>
            <p class="text-green-300 text-xs mt-1">Precision Agriculture</p>
        </div>
        <nav class="flex-1 p-4 space-y-2">
            <a href="{{ route('welcome') }}" class="flex items-center gap-3 p-3 rounded-lg hover:bg-green-700 transition {{ request()->routeIs('dashboard') ? 'bg-green-700 font-bold' : '' }}">
                <span>📊</span> Dashboard
            </a>
            <a href="{{ route('history') }}" class="flex items-center gap-3 p-3 rounded-lg hover:bg-green-700 transition {{ request()->routeIs('history') ? 'bg-green-700 font-bold' : '' }}">
                <span>📝</span> Riwayat Data
            </a>
            <a href="#" class="flex items-center gap-3 p-3 rounded-lg hover:bg-green-700 transition opacity-50 cursor-not-allowed" title="Diakses dari hasil analisis">
                <span>🤖</span> Rekomendasi AI
            </a>
            <a href="{{ route('zones') }}" class="flex items-center gap-3 p-3 rounded-lg hover:bg-green-700 transition {{ request()->routeIs('zones') ? 'bg-green-700 font-bold' : '' }}">
                <span>📡</span> Manajemen Alat IoT
            </a>
        </nav>
        <div class="p-4 border-t border-green-700 text-sm text-center text-green-200">
            Hackathon Build v1.0
        </div>
    </aside>

    <main class="flex-1 flex flex-col h-screen overflow-y-auto">
        
        <header class="bg-white shadow-sm p-4 flex justify-between items-center md:justify-end">
            <div class="md:hidden font-bold text-green-800">🌱 AgroSmart</div>
            <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 font-semibold">Petani Modern (Zona A)</span>
                <div class="w-8 h-8 bg-green-200 rounded-full flex items-center justify-center">👨‍🌾</div>
            </div>
        </header>

        <div class="p-8">
            @yield('content')
        </div>

    </main>

</body>
</html>