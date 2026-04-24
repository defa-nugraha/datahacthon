@extends('layouts.app')

@section('title', 'Input Data Sampling - ' . $zone->name)

@section('content')
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Field Zone / Soil Lab</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Input Data Sampling</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">Masukkan beberapa titik sampling tanah agar zona bisa direpresentasikan dengan lebih akurat.</p>
            </div>
            <div class="inline-flex rounded-2xl border border-outline bg-surface p-1 shadow-panel">
                <button type="button" class="rounded-2xl px-4 py-2 text-sm font-semibold text-slate-500">Ambil Data IoT</button>
                <button type="button" class="rounded-2xl bg-primary-soft px-4 py-2 text-sm font-semibold text-primary">Input Manual</button>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div>
                    <h2 class="text-3xl font-bold tracking-tight text-slate-900">Progress Sampling</h2>
                    <p class="mt-1 text-sm text-slate-500">Titik representatif untuk {{ $zone->name }}.</p>
                </div>
                <div class="mt-4 h-3 rounded-full bg-slate-200">
                    @php
                        $progress = min(100, (($detail['samples']->count() ?? 0) / max($zone->sample_target_count, 1)) * 100);
                    @endphp
                    <div class="h-3 rounded-full bg-primary" style="width: {{ $progress }}%"></div>
                </div>
                <div class="mt-2 text-sm font-medium text-slate-600">{{ $detail['samples']->count() }} dari {{ $zone->sample_target_count }} titik terisi</div>

                <form action="{{ route('zones.sampling.store', $zone) }}" method="POST" class="mt-6 space-y-4">
                    @csrf
                    <div>
                        <label class="mb-2 block text-sm font-semibold text-slate-700">Waktu sampling</label>
                        <input type="datetime-local" name="sampled_at" value="{{ now()->format('Y-m-d\TH:i') }}" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
                    </div>

                    <div class="overflow-hidden rounded-3xl border border-outline">
                        <div class="hidden bg-surface-soft px-5 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 md:grid md:grid-cols-[1.3fr,repeat(5,minmax(0,1fr))] md:gap-3">
                            <div>Nama titik</div>
                            <div>pH</div>
                            <div>N (mg/kg)</div>
                            <div>P (mg/kg)</div>
                            <div>K (mg/kg)</div>
                            <div>Kelembapan (%)</div>
                        </div>
                        <div id="samplingRows" class="divide-y divide-outline">
                            @for ($i = 0; $i < 4; $i++)
                                <div class="grid gap-3 bg-white px-5 py-4 md:grid-cols-[1.3fr,repeat(5,minmax(0,1fr))]">
                                    <input type="text" name="point_label[]" value="Point {{ $zone->name }}-{{ $i + 1 }}" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="Point Alpha-1" required>
                                    <input type="number" step="0.1" min="0" max="14" name="ph[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="6.4" required>
                                    <input type="number" step="0.1" min="0" name="nitrogen[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="110" required>
                                    <input type="number" step="0.1" min="0" name="phosphorus[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="45" required>
                                    <input type="number" step="0.1" min="0" name="potassium[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="85" required>
                                    <input type="number" step="0.1" min="0" max="100" name="soil_moisture[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="42">
                                </div>
                            @endfor
                        </div>
                    </div>

                    <div class="flex flex-wrap gap-3">
                        <button id="addSamplingRow" type="button" class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                            + Tambah Titik
                        </button>
                        <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                            Simpan Zona
                        </button>
                    </div>
                </form>
            </section>

            <aside class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <h2 class="text-3xl font-bold tracking-tight text-slate-900">Estimasi Zona</h2>
                <div class="mt-5 space-y-4">
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-slate-500">Rata-rata pH</span>
                        <span class="font-bold text-slate-900">{{ number_format($detail['aggregate']['ph']['mean'] ?? 0, 2) }}</span>
                    </div>
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-slate-500">Rata-rata NPK</span>
                        <span class="font-bold text-slate-900">
                            {{ number_format($detail['aggregate']['nitrogen']['mean'] ?? 0, 0) }}/{{ number_format($detail['aggregate']['phosphorus']['mean'] ?? 0, 0) }}/{{ number_format($detail['aggregate']['potassium']['mean'] ?? 0, 0) }}
                        </span>
                    </div>
                    <div class="rounded-2xl border border-sky-200 bg-sky-50 px-4 py-4 text-sm text-sky-900">
                        Selesaikan input minimal {{ max(4, $zone->sample_target_count) }} titik agar rekomendasi AI lebih stabil dan lebih mewakili variasi zona.
                    </div>
                </div>
            </aside>
        </div>
    </div>
@endsection

@push('scripts')
    <script>
        document.getElementById('addSamplingRow')?.addEventListener('click', function () {
            const container = document.getElementById('samplingRows');
            const count = container.children.length + 1;
            const row = document.createElement('div');
            row.className = 'grid gap-3 bg-white px-5 py-4 md:grid-cols-[1.3fr,repeat(5,minmax(0,1fr))]';
            row.innerHTML = `
                <input type="text" name="point_label[]" value="Point {{ $zone->name }}-${count}" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" max="14" name="ph[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="nitrogen[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="phosphorus[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="potassium[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" max="100" name="soil_moisture[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
            `;
            container.appendChild(row);
        });
    </script>
@endpush
