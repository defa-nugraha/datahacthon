<?php $__env->startSection('title', 'Analysis History - Vera AI'); ?>

<?php $__env->startSection('content'); ?>
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Reports / History</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Analysis History</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">
                    Tinjau histori sampling, tren unsur hara, dan status implementasi rekomendasi pada setiap zona.
                </p>
            </div>
            <div class="flex flex-wrap gap-3">
                <div class="rounded-2xl border border-outline bg-surface px-4 py-3 text-sm text-slate-500">All Zones</div>
                <div class="rounded-2xl border border-outline bg-surface px-4 py-3 text-sm text-slate-500">Last 6 Months</div>
                <a href="<?php echo e(route('zones.index')); ?>" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">Run New Analysis</a>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Ringkasan Tren pH</h2>
                        <p class="text-sm text-slate-500">Snapshot riwayat nilai pH dari data historis yang tersedia.</p>
                    </div>
                    <div class="rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">Current zone</div>
                </div>
                <div class="mt-6 h-72">
                    <canvas id="historyPhChart"></canvas>
                </div>
            </section>

            <div class="space-y-6">
                <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                    <div class="flex items-center gap-4">
                        <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-accent">
                            <span class="material-symbols-outlined">water_drop</span>
                        </div>
                        <div>
                            <div class="text-sm font-semibold text-slate-500">Avg Moisture</div>
                            <div class="mt-1 text-5xl font-extrabold tracking-tight text-primary"><?php echo e(number_format($historicalData->getCollection()->avg('soil_moisture') ?? 0, 0)); ?>%</div>
                        </div>
                    </div>
                    <div class="mt-4 text-sm text-slate-500">Rata-rata historis dari semua sampel yang memiliki data kelembapan.</div>
                </section>

                <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                    <div class="text-sm font-semibold text-slate-500">Action Rate</div>
                    <div class="mt-3 flex items-end gap-2">
                        <div class="text-5xl font-extrabold tracking-tight text-slate-900">75%</div>
                    </div>
                    <div class="mt-4 h-2 rounded-full bg-slate-200">
                        <div class="h-2 rounded-full bg-primary" style="width: 75%"></div>
                    </div>
                    <div class="mt-3 text-sm text-slate-500">Estimasi tingkat rekomendasi yang sudah dieksekusi di lapangan.</div>
                </section>
            </div>
        </div>

        <section class="overflow-hidden rounded-3xl border border-outline bg-surface shadow-panel">
            <div class="flex flex-col gap-3 border-b border-outline px-6 py-5 md:flex-row md:items-center md:justify-between">
                <div>
                    <h2 class="text-3xl font-bold tracking-tight text-slate-900">Analysis Ledger</h2>
                    <p class="text-sm text-slate-500">Riwayat sampling yang dipakai dalam analisis dan monitoring.</p>
                </div>
                <button class="rounded-2xl border border-outline px-4 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                    Export CSV
                </button>
            </div>

            <div class="overflow-x-auto">
                <table class="min-w-full text-left text-sm">
                    <thead class="bg-surface-soft text-slate-500">
                        <tr>
                            <th class="px-6 py-4 font-semibold">Date</th>
                            <th class="px-6 py-4 font-semibold">Zone Name</th>
                            <th class="px-6 py-4 font-semibold">Soil Summary</th>
                            <th class="px-6 py-4 font-semibold">Recommended Crop</th>
                            <th class="px-6 py-4 font-semibold">Action Taken</th>
                            <th class="px-6 py-4 font-semibold text-right">Detail</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-outline">
                        <?php $__empty_1 = true; $__currentLoopData = $historicalData; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $data): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?>
                            <?php
                                $recommendedPlant = $data->zone?->active_crop ?: ($data->recommended_plant ?: 'Belum ditanam');
                                $actionLabel = $data->zone?->active_crop ? 'Ditanam' : 'Dipantau';
                                $statusClass = $data->zone?->active_crop ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600';
                            ?>
                            <tr class="hover:bg-surface-soft/70">
                                <td class="px-6 py-5 text-slate-700"><?php echo e(optional($data->sampled_at ?? $data->created_at)->format('Y-m-d H:i')); ?></td>
                                <td class="px-6 py-5">
                                    <div class="flex items-center gap-3">
                                        <span class="inline-block h-2.5 w-2.5 rounded-full bg-primary"></span>
                                        <span class="font-semibold text-slate-900"><?php echo e($data->zone?->name ?? 'Zona tak dikenal'); ?></span>
                                    </div>
                                </td>
                                <td class="px-6 py-5 text-slate-600">
                                    <div>pH: <span class="font-semibold text-slate-900"><?php echo e(number_format($data->ph, 1)); ?></span></div>
                                    <div>NPK: <?php echo e(number_format($data->nitrogen, 0)); ?>-<?php echo e(number_format($data->phosphorus, 0)); ?>-<?php echo e(number_format($data->potassium, 0)); ?></div>
                                </td>
                                <td class="px-6 py-5 font-semibold text-primary"><?php echo e($recommendedPlant); ?></td>
                                <td class="px-6 py-5">
                                    <span class="rounded-full px-3 py-1 text-xs font-semibold <?php echo e($statusClass); ?>"><?php echo e($actionLabel); ?></span>
                                </td>
                                <td class="px-6 py-5 text-right">
                                    <?php if($data->zone): ?>
                                        <a href="<?php echo e(route('zones.show', $data->zone)); ?>" class="font-semibold text-primary hover:text-success">Lihat</a>
                                    <?php else: ?>
                                        <span class="text-slate-300">-</span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                        <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?>
                            <tr>
                                <td colspan="6" class="px-6 py-14 text-center text-slate-500">Belum ada histori sampling tersimpan.</td>
                            </tr>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>

            <div class="border-t border-outline px-6 py-4">
                <?php echo e($historicalData->links()); ?>

            </div>
        </section>
    </div>
<?php $__env->stopSection(); ?>

<?php $__env->startPush('scripts'); ?>
    <?php
        $historyChartRows = $historicalData->getCollection()->values()->map(function ($item) {
            return [
                'label' => optional($item->sampled_at ?? $item->created_at)->format('d M'),
                'ph' => round($item->ph, 2),
            ];
        });
    ?>
    <script>
        const historyRows = <?php echo json_encode($historyChartRows, 15, 512) ?>;
        const historyCtx = document.getElementById('historyPhChart');

        if (historyCtx) {
            new Chart(historyCtx, {
                type: 'line',
                data: {
                    labels: historyRows.map(item => item.label),
                    datasets: [{
                        label: 'pH',
                        data: historyRows.map(item => item.ph),
                        borderColor: '#154212',
                        backgroundColor: '#154212',
                        tension: 0.35
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { suggestedMin: 4.5, suggestedMax: 8, grid: { color: '#ecece4' } },
                        x: { grid: { display: false } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }
    </script>
<?php $__env->stopPush(); ?>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /var/www/html/resources/views/history.blade.php ENDPATH**/ ?>