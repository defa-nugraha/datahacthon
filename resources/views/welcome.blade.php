<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agro Smart - AI Crop Predictor</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans p-8">

    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold text-green-700 mb-8">Dashboard Precision Agriculture</h1>

        @if(session('success'))
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                {{ session('success') }}
            </div>
        @endif

        <div class="w-full bg-white p-6 rounded-lg shadow-md border-t-4 border-green-500 mb-8">
    
        <div class="flex flex-col md:flex-row justify-between items-center mb-6 border-b pb-4">
            <div>
                <h2 class="text-2xl font-bold text-gray-800">Monitoring Lahan (Real-time IoT)</h2>
                <p class="text-sm text-gray-500 mt-1">Update terakhir: Barusan</p>
            </div>
            <div class="mt-4 md:mt-0 flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full border border-green-200">
                <span class="relative flex h-3 w-3">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span class="text-sm font-semibold text-green-700">Sensor Terhubung</span>
            </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 text-center hover:shadow-md transition">
                <p class="text-sm text-gray-500 font-semibold mb-1">Nitrogen (N)</p>
                <p class="text-3xl font-bold text-blue-600">42 <span class="text-sm font-normal text-gray-400">mg/kg</span></p>
                <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full mt-2 inline-block">Normal</span>
            </div>

            <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 text-center hover:shadow-md transition">
                <p class="text-sm text-gray-500 font-semibold mb-1">Fosfor (P)</p>
                <p class="text-3xl font-bold text-blue-600">15 <span class="text-sm font-normal text-gray-400">mg/kg</span></p>
                <span class="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full mt-2 inline-block">Rendah</span>
            </div>

            <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 text-center hover:shadow-md transition">
                <p class="text-sm text-gray-500 font-semibold mb-1">Kalium (K)</p>
                <p class="text-3xl font-bold text-blue-600">120 <span class="text-sm font-normal text-gray-400">mg/kg</span></p>
                <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full mt-2 inline-block">Normal</span>
            </div>

            <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 text-center hover:shadow-md transition">
                <p class="text-sm text-gray-500 font-semibold mb-1">pH Tanah</p>
                <p class="text-3xl font-bold text-blue-600">6.2</p>
                <span class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full mt-2 inline-block">Sedikit Asam</span>
            </div>

        </div>

        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
            <div class="flex items-start">
                <div class="text-2xl mr-3">🤖</div>
                <div>
                    <h3 class="font-bold text-blue-900 mb-1">Insight AI (Berdasarkan Data IoT Saat Ini)</h3>
                    <p class="text-sm text-blue-800">
                        Berdasarkan parameter yang terbaca, tanah ini paling cocok untuk ditanam <span class="font-bold">Jagung</span>. 
                        Namun, terdeteksi kadar <span class="font-bold text-red-600">Fosfor (P) terlalu rendah</span>. 
                        Rekomendasi: Tambahkan pupuk SP-36 (Super Fosfat) sebanyak 100kg/ha sebelum masa tanam untuk mengoptimalkan pertumbuhan akar.
                    </p>
                </div>
            </div>
        </div>
        
    </div>

        <div class="flex flex-col md:flex-row gap-6">
            
            <div class="w-full md:w-1/3 bg-white p-6 rounded-lg shadow-md">
                <h2 class="text-xl font-semibold mb-4 border-b pb-2">Input Manual Unsur Hara</h2>
                <form action="{}" method="POST">
                    @csrf
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Nitrogen (N)</label>
                        <input type="number" name="nitrogen" class="w-full border rounded py-2 px-3 focus:outline-none focus:border-green-500" required>
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Fosfor (P)</label>
                        <input type="number" name="phosphorus" class="w-full border rounded py-2 px-3 focus:outline-none focus:border-green-500" required>
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Kalium (K)</label>
                        <input type="number" name="potassium" class="w-full border rounded py-2 px-3 focus:outline-none focus:border-green-500" required>
                    </div>
                    <div class="mb-6">
                        <label class="block text-gray-700 text-sm font-bold mb-2">pH Tanah</label>
                        <input type="number" step="0.1" name="ph" class="w-full border rounded py-2 px-3 focus:outline-none focus:border-green-500" required>
                    </div>
                    <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition duration-200">
                        Cek Rekomendasi AI
                    </button>
                </form>
            </div>

            <div class="w-full md:w-2/3 bg-white p-6 rounded-lg shadow-md">
                <h2 class="text-xl font-semibold mb-4 border-b pb-2">Hasil Analisis AI</h2>
                
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
                    <p class="text-sm text-blue-700">Rekomendasi Tanaman Terbaik:</p>
                    <p class="text-2xl font-bold text-blue-900">Tomat 🍅</p>
                </div>

                <h3 class="font-bold text-gray-700 mt-6 mb-2">Tindakan Perawatan (Gap Analysis)</h3>
                <p class="text-gray-600 mb-6">Tanah saat ini memiliki pH 5.5 (terlalu asam untuk tomat). Rekomendasi: Taburkan kapur dolomit 2 minggu sebelum tanam untuk menetralkan pH ke angka 6.5.</p>

                <h3 class="font-bold text-gray-700 mb-2">Jadwal Reminder</h3>
                <ul class="list-disc list-inside text-gray-600">
                    <li><span class="font-semibold text-gray-800">Hari ini:</span> Pengapuran lahan.</li>
                    <li><span class="font-semibold text-gray-800">H+14:</span> Penanaman bibit tomat.</li>
                </ul>
            </div>

        </div>
    </div>

</body>
</html>