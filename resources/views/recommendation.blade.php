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
            
            <div class="mb-4">
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Risiko Terdeteksi</span>
                <p class="text-sm text-red-600 font-medium mt-1 leading-relaxed">
                    ⚠ {{ $crop['risk_note'] }}
                </p>
            </div>

            <div class="space-y-2 mb-6">
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