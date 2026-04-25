<?php $__env->startSection('title', 'Dashboard - Vera AI'); ?>

<?php $__env->startSection('content'); ?>
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Operations Overview</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Pemantauan zona dan rekomendasi AI</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">
                    Pantau sampling terbaru, status telemetri, dan hasil rekomendasi vegetasi berbasis zona secara real-time.
                </p>
            </div>
            <div class="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-800">
                <span class="inline-block h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                <span>System Online</span>
            </div>
        </div>

        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-soft text-slate-600">
                    <span class="material-symbols-outlined">layers</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight"><?php echo e($stats['total_zones']); ?></div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Total Zones</div>
            </div>
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex items-start justify-between">
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                        <span class="material-symbols-outlined">eco</span>
                    </div>
                    <span class="rounded-full bg-primary-soft px-3 py-1 text-xs font-semibold text-primary">Ready <?php echo e($stats['ready_zones']); ?></span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight"><?php echo e($stats['active_zones']); ?></div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Active Zones</div>
            </div>
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-accent">
                    <span class="material-symbols-outlined">science</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight"><?php echo e($stats['latest_samples']); ?></div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Latest Samples / 24h</div>
            </div>
            <div class="rounded-3xl border border-primary/10 bg-primary p-6 text-white shadow-panel">
                <div class="mb-4 flex items-start justify-between">
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                        <span class="material-symbols-outlined">psychology</span>
                    </div>
                    <span class="inline-block h-2.5 w-2.5 rounded-full bg-emerald-300"></span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight"><?php echo e($stats['new_ai_recommendations']); ?></div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100">Zones With AI Recs</div>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-5 flex items-start justify-between gap-3">
                    <div>
                        <h2 class="text-2xl font-bold tracking-tight text-slate-900">Soil Trend: NPK Average</h2>
                        <p class="text-sm text-slate-500">Rata-rata 7 hari terakhir untuk seluruh zona aktif.</p>
                    </div>
                    <div class="inline-flex items-center gap-2 text-sm text-slate-500">
                        <span class="inline-block h-2.5 w-2.5 rounded-full bg-primary"></span>
                        Current
                    </div>
                </div>
                <div class="h-80">
                    <canvas id="dashboardTrendChart"></canvas>
                </div>
            </section>

            <div class="space-y-6">
                <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Telemetry Status</h2>
                    <div class="mt-6 flex items-center gap-6">
                        <div class="flex h-28 w-28 items-center justify-center rounded-full border-[10px] border-primary text-3xl font-extrabold text-primary">
                            <?php echo e($telemetry['sensor_percentage']); ?>%
                        </div>
                        <div class="space-y-3 text-sm">
                            <div class="flex items-center gap-3">
                                <span class="inline-block h-3 w-3 rounded-full bg-primary"></span>
                                <div>
                                    <div class="font-semibold text-slate-900">Sensor Aktif</div>
                                    <div class="text-slate-500"><?php echo e($telemetry['sensor_percentage']); ?>% dari zona</div>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="inline-block h-3 w-3 rounded-full bg-slate-300"></span>
                                <div>
                                    <div class="font-semibold text-slate-900">Input Manual</div>
                                    <div class="text-slate-500"><?php echo e($telemetry['manual_percentage']); ?>% dari zona</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <div class="grid gap-4 sm:grid-cols-2">
                    <a href="<?php echo e(route('zones.index')); ?>" class="rounded-3xl bg-primary px-6 py-6 text-white shadow-panel transition hover:bg-success">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined">science</span>
                            <span class="text-lg font-bold">Start Analysis</span>
                        </div>
                        <p class="mt-2 text-sm text-emerald-50">Lanjut ke input sampling atau analisis per zona.</p>
                    </a>
                    <a href="<?php echo e(route('zones.index')); ?>" class="rounded-3xl border border-outline bg-surface px-6 py-6 shadow-panel transition hover:border-primary/30">
                        <div class="flex items-center gap-3 text-primary">
                            <span class="material-symbols-outlined">add_location_alt</span>
                            <span class="text-lg font-bold">Add Zone</span>
                        </div>
                        <p class="mt-2 text-sm text-slate-500">Daftarkan zona baru dan tentukan target jumlah sampling.</p>
                    </a>
                </div>
            </div>
        </div>

        <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Field Zones</h2>
                    <p class="text-sm text-slate-500">Ringkasan status untuk setiap zona aktif.</p>
                </div>
                <a href="<?php echo e(route('zones.index')); ?>" class="text-sm font-semibold text-primary hover:text-success">Lihat semua zona</a>
            </div>

            <?php if(collect($zones)->isEmpty()): ?>
                <div class="mt-6 rounded-2xl border border-dashed border-outline bg-surface-soft px-6 py-10 text-center text-slate-500">
                    Belum ada zona. Tambahkan zona pertama untuk memulai alur sampling dan analisis AI.
                </div>
            <?php else: ?>
                <div class="mt-6 grid gap-4 lg:grid-cols-3">
                    <?php $__currentLoopData = $zones; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $zone): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <?php
                            $statusClass = match($zone['status']['tone']) {
                                'green' => 'bg-emerald-100 text-emerald-800',
                                'blue' => 'bg-sky-100 text-sky-800',
                                default => 'bg-amber-100 text-amber-800',
                            };
                        ?>
                        <div class="rounded-3xl border border-outline bg-surface-soft p-5">
                            <div class="flex items-start justify-between gap-3">
                                <div>
                                    <h3 class="text-2xl font-bold tracking-tight text-slate-900"><?php echo e($zone['name']); ?></h3>
                                    <p class="mt-1 text-sm text-slate-500"><?php echo e($zone['area_label']); ?></p>
                                </div>
                                <span class="rounded-full px-3 py-1 text-xs font-semibold <?php echo e($statusClass); ?>">
                                    <?php echo e($zone['status']['label']); ?>

                                </span>
                            </div>
                            <div class="mt-5 grid grid-cols-2 gap-3">
                                <div class="rounded-2xl bg-white px-4 py-3 border border-outline">
                                    <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Sampling</div>
                                    <div class="mt-2 text-lg font-bold text-slate-900"><?php echo e($zone['sample_count']); ?> titik</div>
                                </div>
                                <div class="rounded-2xl bg-white px-4 py-3 border border-outline">
                                    <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Rekomendasi</div>
                                    <div class="mt-2 text-lg font-bold text-primary"><?php echo e($zone['latest_recommendation_label'] ?? 'Belum ada'); ?></div>
                                </div>
                            </div>
                            <div class="mt-4 flex items-center gap-2 text-sm text-slate-500">
                                <span class="material-symbols-outlined text-base text-primary">grass</span>
                                <span><?php echo e($zone['active_crop'] ?: 'Belum ada tanaman aktif'); ?></span>
                            </div>
                            <div class="mt-5 flex gap-3">
                                <a href="<?php echo e(route('zones.show', $zone['id'])); ?>" class="flex-1 rounded-2xl border border-outline px-4 py-3 text-center text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                                    View Detail
                                </a>
                                <a href="<?php echo e(route('zones.monitor', $zone['id'])); ?>" class="rounded-2xl bg-primary px-4 py-3 text-sm font-semibold text-white transition hover:bg-success">
                                    Live
                                </a>
                            </div>
                        </div>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                </div>
            <?php endif; ?>
        </section>

        <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
            <div class="flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Recent Activity</h2>
                    <p class="text-sm text-slate-500">Update sampling dan analisis terbaru di seluruh zona.</p>
                </div>
                <a href="<?php echo e(route('history')); ?>" class="text-sm font-semibold text-primary hover:text-success">View all log</a>
            </div>
            <div class="mt-5 divide-y divide-outline">
                <?php $__empty_1 = true; $__currentLoopData = $recent_activity; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $activity): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?>
                    <div class="flex flex-col gap-3 py-4 md:flex-row md:items-start md:justify-between">
                        <div class="flex gap-4">
                            <div class="mt-1 flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft text-primary">
                                <span class="material-symbols-outlined text-[20px]">check</span>
                            </div>
                            <div>
                                <div class="font-semibold text-slate-900"><?php echo e($activity['title']); ?></div>
                                <div class="mt-1 text-sm text-slate-500"><?php echo e($activity['description']); ?></div>
                            </div>
                        </div>
                        <div class="text-sm text-slate-400"><?php echo e($activity['time']); ?></div>
                    </div>
                <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?>
                    <div class="py-8 text-center text-slate-500">Belum ada aktivitas terbaru.</div>
                <?php endif; ?>
            </div>
        </section>
    </div>
<?php $__env->stopSection(); ?>

<?php $__env->startPush('scripts'); ?>
    <script>
        const trendChartData = <?php echo json_encode($trend_chart, 15, 512) ?>;
        const dashboardTrendCtx = document.getElementById('dashboardTrendChart');

        if (dashboardTrendCtx) {
            new Chart(dashboardTrendCtx, {
                type: 'line',
                data: {
                    labels: trendChartData.labels,
                    datasets: [
                        {
                            label: 'Nitrogen',
                            data: trendChartData.nitrogen,
                            borderColor: '#154212',
                            backgroundColor: '#154212',
                            tension: 0.35
                        },
                        {
                            label: 'Fosfor',
                            data: trendChartData.phosphorus,
                            borderColor: '#0b4f7d',
                            backgroundColor: '#0b4f7d',
                            tension: 0.35
                        },
                        {
                            label: 'Kalium',
                            data: trendChartData.potassium,
                            borderColor: '#5e5e5c',
                            backgroundColor: '#5e5e5c',
                            tension: 0.35
                        },
                        {
                            label: 'pH',
                            data: trendChartData.ph,
                            borderColor: '#a15c00',
                            backgroundColor: '#a15c00',
                            borderDash: [6, 6],
                            yAxisID: 'y1',
                            tension: 0.35
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top', align: 'end' }
                    },
                    scales: {
                        y: {
                            grid: { color: '#ecece4' },
                            ticks: { color: '#64748b' }
                        },
                        y1: {
                            position: 'right',
                            grid: { drawOnChartArea: false },
                            ticks: { color: '#a15c00' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b' }
                        }
                    }
                }
            });
        }
    </script>
<?php $__env->stopPush(); ?>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /var/www/html/resources/views/welcome.blade.php ENDPATH**/ ?>