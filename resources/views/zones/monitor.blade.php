@extends('layouts.app')

@section('title', 'Pemantauan Real-time - ' . $zone->name)

@section('content')
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Real-time Monitoring</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Pemantauan {{ $zone->name }}</h1>
                <p class="mt-2 text-base text-slate-600">{{ $zone->area_label }} · Terakhir diperbarui {{ optional($zone->soilData()->latest('sampled_at')->first()?->sampled_at)?->diffForHumans() ?? 'belum ada data' }}</p>
            </div>
            <div class="flex gap-3">
                <a href="{{ route('zones.show', $zone) }}" class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">Kembali ke Detail</a>
                <form action="{{ route('zones.care.refresh', $zone) }}" method="POST">
                    @csrf
                    <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                        Perbarui Advice
                    </button>
                </form>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[1fr,1.55fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Status Kesehatan Tanaman</div>
                <div class="mt-4 flex items-end gap-3">
                    <div class="text-6xl font-extrabold tracking-tight text-primary">{{ $monitoring['health_score'] }}%</div>
                    <div class="mb-2 text-xl font-semibold text-slate-700">{{ $monitoring['health_score'] >= 85 ? 'Sehat' : 'Perlu perhatian' }}</div>
                </div>
                <div class="mt-5 h-2 rounded-full bg-slate-200">
                    <div class="h-2 rounded-full bg-primary" style="width: {{ $monitoring['health_score'] }}%"></div>
                </div>
                <div class="mt-2 flex justify-between text-xs font-semibold text-slate-400">
                    <span>0%</span>
                    <span>Optimal range: 85-100%</span>
                    <span>100%</span>
                </div>
            </section>

            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-start gap-4">
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-accent">
                        <span class="material-symbols-outlined">tips_and_updates</span>
                    </div>
                    <div class="flex-1">
                        <div class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">AI Adaptive Advice</div>
                        @if ($monitoring['latest_advice'])
                            @php
                                $adviceProvider = $monitoring['latest_advice']->raw_response['provider'] ?? 'local';
                                $thresholdReason = $monitoring['latest_advice']->raw_response['threshold_context']['trigger_reason'] ?? null;
                            @endphp
                            <p class="mt-3 text-lg font-semibold leading-8 text-slate-900">{{ $monitoring['latest_advice']->advice_summary }}</p>
                            <div class="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-500">
                                <span class="rounded-full bg-surface-soft px-3 py-1">Provider: {{ $adviceProvider }}</span>
                                <span class="rounded-full bg-surface-soft px-3 py-1">Update: {{ optional($monitoring['latest_advice']->generated_at)->diffForHumans() }}</span>
                                @if ($thresholdReason)
                                    <span class="rounded-full bg-primary-soft px-3 py-1 text-primary">Trigger: {{ str_replace('_', ' ', $thresholdReason) }}</span>
                                @endif
                            </div>
                            <div class="mt-4 flex flex-wrap gap-3">
                                @foreach (($monitoring['latest_advice']->recommendations ?? []) as $recommendation)
                                    <div class="rounded-2xl border border-outline bg-surface-soft px-4 py-3 text-sm">
                                        <div class="font-semibold text-slate-900">{{ $recommendation['title'] ?? 'Rekomendasi' }}</div>
                                        <div class="mt-1 text-slate-500">{{ $recommendation['detail'] ?? '' }}</div>
                                    </div>
                                @endforeach
                            </div>
                        @else
                            <p class="mt-3 text-sm text-slate-500">Belum ada adaptive advice. Pastikan zona sudah memiliki tanaman aktif dan history sampling dalam 1 jam terakhir.</p>
                        @endif
                    </div>
                </div>
            </section>
        </div>

        <section class="space-y-4">
            <div class="flex items-center gap-2 text-3xl font-bold tracking-tight text-slate-900">
                <span class="material-symbols-outlined text-primary">monitoring</span>
                <span>Metrik Tanah Live</span>
            </div>
            <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                @php
                    $metricCards = [
                        ['label' => 'pH Tanah', 'value' => number_format($monitoring['aggregate']['ph']['mean'] ?? 0, 1), 'note' => 'Optimal 6.0 - 7.0', 'icon' => 'water_drop'],
                        ['label' => 'Nitrogen (N)', 'value' => number_format($monitoring['aggregate']['nitrogen']['mean'] ?? 0, 0) . ' mg/kg', 'note' => 'Target 100 mg/kg', 'icon' => 'grass'],
                        ['label' => 'Fosfor (P)', 'value' => number_format($monitoring['aggregate']['phosphorus']['mean'] ?? 0, 0) . ' mg/kg', 'note' => 'Target 40-50 mg/kg', 'icon' => 'grain'],
                        ['label' => 'Kalium (K)', 'value' => number_format($monitoring['aggregate']['potassium']['mean'] ?? 0, 0) . ' mg/kg', 'note' => 'Target 90 mg/kg', 'icon' => 'science'],
                        ['label' => 'Kelembapan', 'value' => number_format($monitoring['aggregate']['soil_moisture']['mean'] ?? 0, 0) . '%', 'note' => 'History 1 jam terakhir', 'icon' => 'humidity_percentage'],
                    ];
                @endphp
                @foreach ($metricCards as $metric)
                    <div class="rounded-3xl border border-outline bg-surface p-5 shadow-panel">
                        <div class="flex items-start justify-between gap-3">
                            <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ $metric['label'] }}</div>
                            <span class="material-symbols-outlined text-slate-400">{{ $metric['icon'] }}</span>
                        </div>
                        <div class="mt-5 text-4xl font-extrabold tracking-tight text-slate-900">{{ $metric['value'] }}</div>
                        <div class="mt-3 text-sm text-slate-500">{{ $metric['note'] }}</div>
                    </div>
                @endforeach
            </div>
        </section>

        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-center justify-between gap-3">
                    <div>
                        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Grafik 1 Jam Terakhir</h2>
                        <p class="text-sm text-slate-500">Ringkasan NPK gabungan dan kelembapan untuk history 1 jam.</p>
                    </div>
                    <div class="text-sm font-semibold text-slate-500">{{ $monitoring['history_count'] }} titik data</div>
                </div>
                <div class="mt-6 h-80">
                    <canvas id="monitoringChart"></canvas>
                </div>
            </section>

            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-center justify-between">
                    <h2 class="text-3xl font-bold tracking-tight text-slate-900">Peringatan Sistem</h2>
                    <span class="rounded-full bg-surface-soft px-3 py-1 text-xs font-semibold text-slate-500">{{ $monitoring['alerts']->count() }} baru</span>
                </div>
                <div class="mt-5 space-y-4">
                    @forelse ($monitoring['alerts'] as $alert)
                        <div class="rounded-2xl border px-4 py-4 {{ $alert['tone'] === 'red' ? 'border-rose-200 bg-rose-50' : ($alert['tone'] === 'amber' ? 'border-amber-200 bg-amber-50' : 'border-sky-200 bg-sky-50') }}">
                            <div class="font-semibold text-slate-900">{{ $alert['title'] }}</div>
                            <div class="mt-1 text-sm text-slate-600">{{ $alert['description'] }}</div>
                        </div>
                    @empty
                        <div class="rounded-2xl border border-outline bg-surface-soft px-4 py-6 text-sm text-slate-500">
                            Belum ada alert aktif. Sistem akan menampilkan peringatan saat kondisi nutrisi atau kelembapan mulai menyimpang.
                        </div>
                    @endforelse
                </div>
            </section>
        </div>
    </div>
@endsection

@push('scripts')
    <script>
        const monitoringChartPayload = @json($monitoring['history_chart']);
        const monitoringCtx = document.getElementById('monitoringChart');

        if (monitoringCtx) {
            new Chart(monitoringCtx, {
                type: 'line',
                data: {
                    labels: monitoringChartPayload.labels,
                    datasets: [
                        {
                            label: 'NPK',
                            data: monitoringChartPayload.npk,
                            borderColor: '#154212',
                            backgroundColor: '#154212',
                            tension: 0.4
                        },
                        {
                            label: 'Kelembapan',
                            data: monitoringChartPayload.moisture,
                            borderColor: '#0b4f7d',
                            backgroundColor: '#0b4f7d',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { grid: { color: '#ecece4' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
    </script>
@endpush
