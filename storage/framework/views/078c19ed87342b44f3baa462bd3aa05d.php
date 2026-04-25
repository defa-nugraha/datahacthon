<?php $__env->startSection('title', 'Recommendation Results - Vera AI'); ?>

<?php $__env->startSection('content'); ?>
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">AI Advisor / Recommendation</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Recommendation Results</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">
                    Berdasarkan komposisi unsur hara dan profil zona <?php echo e($zone->name); ?>, berikut rekomendasi tanaman paling relevan saat ini.
                </p>
            </div>
            <div class="rounded-full border border-outline bg-surface px-4 py-2 text-sm font-semibold text-slate-500">
                Model: <?php echo e($model_info['model_name'] ?? 'N/A'); ?>

            </div>
        </div>

        <?php if(!empty($warnings)): ?>
            <div class="rounded-3xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-900">
                <div class="font-semibold">Catatan analisis</div>
                <ul class="mt-2 list-disc space-y-1 pl-5">
                    <?php $__currentLoopData = $warnings; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $warning): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <li><?php echo e($warning); ?></li>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                </ul>
            </div>
        <?php endif; ?>

        <div class="grid gap-6 xl:grid-cols-[1.85fr,0.95fr]">
            <section class="overflow-hidden rounded-3xl border border-outline bg-surface shadow-panel">
                <div class="relative overflow-hidden bg-[radial-gradient(circle_at_top_right,_rgba(255,255,255,0.14),_transparent_35%),linear-gradient(135deg,#1f5d1a_0%,#154212_45%,#11360f_100%)] px-8 py-10 text-white">
                    <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80')] bg-cover bg-center opacity-30"></div>
                    <div class="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
                        <div>
                            <div class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-100">Primary Match</div>
                            <h2 class="mt-3 text-5xl font-extrabold tracking-tight"><?php echo e($primary_recommendation['label']); ?></h2>
                            <p class="mt-3 max-w-2xl text-base text-emerald-50">
                                Model menemukan kecocokan tertinggi antara profil hara zona ini dan pola pertumbuhan tanaman tersebut.
                            </p>
                        </div>
                        <div class="inline-flex items-center gap-3 rounded-full bg-white/10 px-5 py-3 text-xl font-bold backdrop-blur">
                            <span class="material-symbols-outlined">verified</span>
                            <span><?php echo e(number_format($primary_recommendation['confidence'], 1)); ?>% Confidence</span>
                        </div>
                    </div>
                </div>

                <div class="p-6 md:p-8">
                    <div class="rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-5">
                        <div class="flex items-center gap-3 text-primary">
                            <span class="material-symbols-outlined">psychology</span>
                            <span class="text-lg font-bold">AI Reasoning</span>
                        </div>
                        <p class="mt-3 text-base leading-7 text-slate-700"><?php echo e($primary_recommendation['reasoning']); ?></p>
                    </div>

                    <div class="mt-6 grid gap-4 md:grid-cols-3">
                        <div class="rounded-2xl border border-outline bg-surface-soft px-5 py-5">
                            <div class="text-sm font-semibold text-slate-500">Water Needs</div>
                            <div class="mt-3 text-2xl font-bold text-slate-900"><?php echo e($primary_recommendation['water_need']); ?></div>
                        </div>
                        <div class="rounded-2xl border border-outline bg-surface-soft px-5 py-5">
                            <div class="text-sm font-semibold text-slate-500">Harvest Time</div>
                            <div class="mt-3 text-2xl font-bold text-slate-900"><?php echo e($primary_recommendation['harvest_time_days']); ?> hari</div>
                        </div>
                        <div class="rounded-2xl border border-outline bg-surface-soft px-5 py-5">
                            <div class="text-sm font-semibold text-slate-500">Risk Factor</div>
                            <div class="mt-3 text-2xl font-bold text-slate-900"><?php echo e($primary_recommendation['risk_factor']); ?></div>
                        </div>
                    </div>

                    <div class="mt-6">
                        <div class="flex items-center justify-between text-sm font-semibold text-slate-500">
                            <span>Overall Suitability Score</span>
                            <span><?php echo e(number_format($primary_recommendation['suitability_score'], 1)); ?>%</span>
                        </div>
                        <div class="mt-2 h-3 rounded-full bg-slate-200">
                            <div class="h-3 rounded-full bg-primary" style="width: <?php echo e($primary_recommendation['suitability_score']); ?>%"></div>
                        </div>
                    </div>

                    <div class="mt-8 grid gap-3 md:grid-cols-2">
                        <form action="<?php echo e(route('zones.plant.start', $zone)); ?>" method="POST">
                            <?php echo csrf_field(); ?>
                            <input type="hidden" name="crop_name" value="<?php echo e($primary_recommendation['label']); ?>">
                            <button type="submit" class="w-full rounded-2xl bg-primary px-6 py-4 text-base font-semibold text-white transition hover:bg-success">
                                Mulai Tanam
                            </button>
                        </form>
                        <a href="<?php echo e(route('zones.show', $zone)); ?>" class="w-full rounded-2xl border border-outline px-6 py-4 text-center text-base font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                            Simpan & Kembali ke Zona
                        </a>
                    </div>
                </div>
            </section>

            <aside class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <h2 class="text-3xl font-bold tracking-tight text-slate-900">Top Alternatives</h2>
                <div class="mt-5 space-y-5">
                    <?php $__currentLoopData = $alternatives; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $alternative): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                        <div>
                            <div class="flex items-center justify-between gap-3">
                                <div class="flex items-center gap-3">
                                    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft text-primary font-bold">
                                        <?php echo e($alternative['rank']); ?>

                                    </div>
                                    <div class="font-semibold text-slate-900"><?php echo e($alternative['label']); ?></div>
                                </div>
                                <div class="text-lg font-bold text-slate-700"><?php echo e($alternative['match_rate']); ?>%</div>
                            </div>
                            <div class="mt-3 h-2 rounded-full bg-slate-200">
                                <div class="h-2 rounded-full bg-primary" style="width: <?php echo e($alternative['match_rate']); ?>%"></div>
                            </div>
                        </div>
                    <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                </div>

                <div class="mt-10 rounded-2xl border border-outline bg-surface-soft p-5">
                    <div class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Agregasi Zona</div>
                    <div class="mt-4 space-y-3 text-sm">
                        <div class="flex justify-between"><span class="text-slate-500">pH Mean</span><span class="font-semibold text-slate-900"><?php echo e(number_format(data_get($aggregated_features, 'ph.mean', data_get($aggregated_features, 'ph_mean', 0)), 2)); ?></span></div>
                        <div class="flex justify-between"><span class="text-slate-500">Nitrogen Mean</span><span class="font-semibold text-slate-900"><?php echo e(number_format(data_get($aggregated_features, 'nitrogen.mean', data_get($aggregated_features, 'nitrogen_mean', 0)), 1)); ?></span></div>
                        <div class="flex justify-between"><span class="text-slate-500">Phosphorus Mean</span><span class="font-semibold text-slate-900"><?php echo e(number_format(data_get($aggregated_features, 'phosphorus.mean', data_get($aggregated_features, 'phosphorus_mean', 0)), 1)); ?></span></div>
                        <div class="flex justify-between"><span class="text-slate-500">Potassium Mean</span><span class="font-semibold text-slate-900"><?php echo e(number_format(data_get($aggregated_features, 'potassium.mean', data_get($aggregated_features, 'potassium_mean', 0)), 1)); ?></span></div>
                    </div>
                </div>

                <a href="<?php echo e(route('zones.show', $zone)); ?>" class="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl border border-outline px-5 py-4 text-base font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                    <span class="material-symbols-outlined text-[20px]">compare_arrows</span>
                    <span>Bandingkan dengan Zona</span>
                </a>
            </aside>
        </div>
    </div>
<?php $__env->stopSection(); ?>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /var/www/html/resources/views/recommendation.blade.php ENDPATH**/ ?>