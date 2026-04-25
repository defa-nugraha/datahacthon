<?php $__env->startSection('title', $zone->name . ' - Detail Zona'); ?>

<?php $__env->startSection('content'); ?>
    <?php
        $editModalId = 'zone-edit-modal';
        $samplingModalId = 'sampling-create-modal';
        $isEditModalActive = old('_open_modal') === $editModalId;
        $samplingPointLabels = old('point_label', []);
        $samplingPh = old('ph', []);
        $samplingNitrogen = old('nitrogen', []);
        $samplingPhosphorus = old('phosphorus', []);
        $samplingPotassium = old('potassium', []);
        $samplingMoisture = old('soil_moisture', []);
        $samplingRowsCount = max(count($samplingPointLabels), 4);
    ?>

    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
                <div class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Field Zones / Detail</div>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900"><?php echo e($zone->name); ?></h1>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-sm text-slate-500">
                    <span class="inline-flex items-center gap-2"><span class="material-symbols-outlined text-base">location_on</span><?php echo e($zone->area_label); ?></span>
                    <span class="inline-flex items-center gap-2"><span class="material-symbols-outlined text-base">pin_drop</span><?php echo e($zone->location_description); ?></span>
                    <span class="inline-flex items-center gap-2"><span class="material-symbols-outlined text-base">schedule</span>Last updated: <?php echo e(optional($samples->last()?->sampled_at ?? $samples->last()?->created_at)?->format('d M Y, H:i') ?: 'Belum ada data'); ?></span>
                </div>
                <?php if($zone->active_crop): ?>
                    <div class="mt-4 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-800">
                        <span class="material-symbols-outlined text-base">grass</span>
                        <span>Tanaman aktif: <?php echo e($zone->active_crop); ?></span>
                    </div>
                <?php endif; ?>
            </div>
            <div class="flex flex-wrap gap-3">
                <button
                    type="button"
                    data-modal-open="<?php echo e($samplingModalId); ?>"
                    class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft"
                >
                    Tambah Sampling
                </button>
                <button
                    type="button"
                    data-modal-open="<?php echo e($editModalId); ?>"
                    class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft"
                >
                    Edit Zona
                </button>
                <form action="<?php echo e(route('zones.analyze', $zone)); ?>" method="POST">
                    <?php echo csrf_field(); ?>
                    <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                        Jalankan Analisis AI
                    </button>
                </form>
                <?php if($zone->active_crop): ?>
                    <form action="<?php echo e(route('zones.plant.reset', $zone)); ?>" method="POST">
                        <?php echo csrf_field(); ?>
                        <button type="submit" class="rounded-2xl border border-rose-200 px-5 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-50">
                            Reset Tanaman Aktif
                        </button>
                    </form>
                <?php endif; ?>
                <form
                    action="<?php echo e(route('zones.destroy', $zone)); ?>"
                    method="POST"
                    data-confirm-delete
                    data-confirm-title="Hapus zona <?php echo e($zone->name); ?>?"
                    data-confirm-text="Seluruh sampling dan adaptive advice pada zona ini akan ikut terhapus."
                    data-confirm-button="Ya, hapus zona"
                >
                    <?php echo csrf_field(); ?>
                    <?php echo method_field('DELETE'); ?>
                    <button type="submit" class="rounded-2xl border border-rose-200 px-5 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-50">
                        Hapus Zona
                    </button>
                </form>
            </div>
        </div>

        <?php if($quality_notice): ?>
            <div class="flex items-start justify-between gap-3 rounded-3xl border border-sky-200 bg-sky-50 px-5 py-4 text-sky-900">
                <div>
                    <div class="font-semibold">Data Quality Notice</div>
                    <div class="mt-1 text-sm text-sky-800"><?php echo e($quality_notice); ?></div>
                </div>
                <button type="button" data-modal-open="<?php echo e($samplingModalId); ?>" class="text-sm font-semibold text-accent">View details</button>
            </div>
        <?php endif; ?>

        <div class="grid gap-5 xl:grid-cols-3">
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-start justify-between gap-3">
                    <div>
                        <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Mean pH</div>
                        <div class="mt-4 text-5xl font-extrabold tracking-tight"><?php echo e(number_format($aggregate['ph']['mean'] ?? 0, 1)); ?></div>
                    </div>
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                        <span class="material-symbols-outlined">water_drop</span>
                    </div>
                </div>
                <div class="mt-4 flex items-center gap-2 text-sm">
                    <span class="rounded-full bg-emerald-100 px-3 py-1 font-semibold text-emerald-700">
                        <?php echo e(($aggregate['ph']['mean'] ?? 0) >= 6 && ($aggregate['ph']['mean'] ?? 0) <= 7 ? 'Optimal' : 'Perlu perhatian'); ?>

                    </span>
                </div>
                <div class="mt-5 h-2 rounded-full bg-slate-200">
                    <div class="h-2 rounded-full bg-primary" style="width: <?php echo e(min(max((($aggregate['ph']['mean'] ?? 0) / 7) * 100, 10), 100)); ?>%"></div>
                </div>
            </div>

            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-start justify-between gap-3">
                    <div>
                        <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Mean NPK (mg/kg)</div>
                        <div class="mt-4 flex gap-5 text-4xl font-extrabold tracking-tight">
                            <span><?php echo e(number_format($aggregate['nitrogen']['mean'] ?? 0, 0)); ?><span class="ml-1 text-lg font-semibold text-slate-400">N</span></span>
                            <span><?php echo e(number_format($aggregate['phosphorus']['mean'] ?? 0, 0)); ?><span class="ml-1 text-lg font-semibold text-slate-400">P</span></span>
                            <span><?php echo e(number_format($aggregate['potassium']['mean'] ?? 0, 0)); ?><span class="ml-1 text-lg font-semibold text-slate-400">K</span></span>
                        </div>
                    </div>
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-accent">
                        <span class="material-symbols-outlined">science</span>
                    </div>
                </div>
                <div class="mt-4 text-sm text-slate-500">
                    <?php echo e(($aggregate['phosphorus']['mean'] ?? 0) < 20 ? 'Fosfor masih di bawah rentang target.' : 'Komposisi NPK relatif stabil untuk dianalisis.'); ?>

                </div>
            </div>

            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex items-start justify-between gap-3">
                    <div>
                        <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Soil Moisture</div>
                        <div class="mt-4 text-5xl font-extrabold tracking-tight"><?php echo e(number_format($aggregate['soil_moisture']['mean'] ?? 0, 0)); ?>%</div>
                    </div>
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-600">
                        <span class="material-symbols-outlined">humidity_percentage</span>
                    </div>
                </div>
                <div class="mt-4 text-sm text-slate-500">
                    Rentang <?php echo e(number_format($aggregate['soil_moisture']['min'] ?? 0, 0)); ?>% - <?php echo e(number_format($aggregate['soil_moisture']['max'] ?? 0, 0)); ?>%
                </div>
                <div class="mt-5 grid grid-cols-5 gap-2">
                    <?php for($i = 1; $i <= 5; $i++): ?>
                        <div class="h-6 rounded-md <?php echo e($i <= ceil((($aggregate['soil_moisture']['mean'] ?? 0) / 20)) ? 'bg-primary/80' : 'bg-slate-100'); ?>"></div>
                    <?php endfor; ?>
                </div>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Sample Points Data</h2>
                        <p class="text-sm text-slate-500">Titik sampling yang dipakai untuk representasi zona.</p>
                    </div>
                    <div class="text-sm font-semibold text-primary">Total <?php echo e(count($sample_cards)); ?> titik</div>
                </div>

                <?php if(count($sample_cards) === 0): ?>
                    <div class="mt-6 rounded-2xl border border-dashed border-outline bg-surface-soft px-6 py-10 text-center text-slate-500">
                        Belum ada titik sampling untuk zona ini.
                    </div>
                <?php else: ?>
                    <div class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                        <?php $__currentLoopData = $sample_cards; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $sample): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                            <div class="rounded-2xl border border-outline bg-surface-soft px-4 py-4">
                                <div class="flex items-center justify-between">
                                    <span class="rounded-lg bg-white px-3 py-1 text-xs font-semibold text-slate-500"><?php echo e($sample['point_label']); ?></span>
                                    <span class="inline-block h-2.5 w-2.5 rounded-full <?php echo e($sample['status'] === 'good' ? 'bg-emerald-500' : 'bg-rose-500'); ?>"></span>
                                </div>
                                <div class="mt-5 space-y-2 text-sm">
                                    <div class="flex justify-between"><span class="text-slate-500">pH</span><span class="font-semibold text-slate-900"><?php echo e(number_format($sample['ph'], 1)); ?></span></div>
                                    <div class="flex justify-between"><span class="text-slate-500">NPK</span><span class="font-semibold text-slate-900"><?php echo e(number_format($sample['nitrogen'], 0)); ?>/<?php echo e(number_format($sample['phosphorus'], 0)); ?>/<?php echo e(number_format($sample['potassium'], 0)); ?></span></div>
                                    <div class="flex justify-between"><span class="text-slate-500">Moisture</span><span class="font-semibold text-slate-900"><?php echo e($sample['soil_moisture'] !== null ? number_format($sample['soil_moisture'], 0) . '%' : '-'); ?></span></div>
                                </div>
                                <div class="mt-4 text-xs text-slate-400"><?php echo e($sample['sampled_at']); ?></div>
                            </div>
                        <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                    </div>
                <?php endif; ?>
            </section>

            <aside class="space-y-6">
                <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                    <h2 class="text-3xl font-bold tracking-tight text-slate-900">Profile Analysis</h2>
                    <p class="mt-2 text-sm text-slate-500">Current vs ideal benchmark untuk <?php echo e($zone->name); ?>.</p>
                    <div class="mt-5 h-72">
                        <canvas id="zoneRadarChart"></canvas>
                    </div>
                </section>

                <?php if($latest_advice): ?>
                    <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                        <div class="flex items-center justify-between gap-3">
                            <div>
                                <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">AI Adaptive Advice</div>
                                <h3 class="mt-2 text-2xl font-bold tracking-tight text-slate-900"><?php echo e($latest_advice->crop_name); ?></h3>
                            </div>
                            <span class="rounded-full px-3 py-1 text-xs font-semibold <?php echo e($latest_advice->urgency_level === 'high' ? 'bg-rose-100 text-rose-700' : ($latest_advice->urgency_level === 'low' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700')); ?>">
                                <?php echo e(ucfirst($latest_advice->urgency_level)); ?>

                            </span>
                        </div>
                        <p class="mt-4 text-sm leading-6 text-slate-600"><?php echo e($latest_advice->advice_summary); ?></p>
                        <div class="mt-4 space-y-3">
                            <?php $__currentLoopData = ($latest_advice->recommendations ?? []); $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $recommendation): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                                <div class="rounded-2xl bg-surface-soft px-4 py-3">
                                    <div class="font-semibold text-slate-900"><?php echo e($recommendation['title'] ?? 'Rekomendasi'); ?></div>
                                    <div class="mt-1 text-sm text-slate-500"><?php echo e($recommendation['detail'] ?? ''); ?></div>
                                </div>
                            <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                        </div>
                        <form action="<?php echo e(route('zones.care.refresh', $zone)); ?>" method="POST" class="mt-4">
                            <?php echo csrf_field(); ?>
                            <button type="submit" class="w-full rounded-2xl border border-outline px-4 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                                Refresh Advice
                            </button>
                        </form>
                    </section>
                <?php endif; ?>
            </aside>
        </div>
    </div>

    <?php if (isset($component)) { $__componentOriginal9f64f32e90b9102968f2bc548315018c = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal9f64f32e90b9102968f2bc548315018c = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.modal','data' => ['id' => $editModalId,'title' => 'Edit zona','description' => 'Perbarui identitas dan target sampling untuk '.$zone->name.'.','maxWidth' => 'max-w-2xl']] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('modal'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes(['id' => \Illuminate\View\Compilers\BladeCompiler::sanitizeComponentAttribute($editModalId),'title' => 'Edit zona','description' => \Illuminate\View\Compilers\BladeCompiler::sanitizeComponentAttribute('Perbarui identitas dan target sampling untuk '.$zone->name.'.'),'max-width' => 'max-w-2xl']); ?>
        <form action="<?php echo e(route('zones.update', $zone)); ?>" method="POST" class="grid gap-4 sm:grid-cols-2">
            <?php echo csrf_field(); ?>
            <?php echo method_field('PUT'); ?>
            <input type="hidden" name="_open_modal" value="<?php echo e($editModalId); ?>">

            <div class="sm:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700">Nama zona</label>
                <input
                    type="text"
                    name="name"
                    value="<?php echo e($isEditModalActive ? old('name') : $zone->name); ?>"
                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                    required
                >
            </div>

            <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Blok / sektor</label>
                <input
                    type="text"
                    name="area_label"
                    value="<?php echo e($isEditModalActive ? old('area_label') : $zone->area_label); ?>"
                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                >
            </div>

            <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Target titik</label>
                <input
                    type="number"
                    name="sample_target_count"
                    min="3"
                    max="24"
                    value="<?php echo e($isEditModalActive ? old('sample_target_count', $zone->sample_target_count) : $zone->sample_target_count); ?>"
                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                >
            </div>

            <div class="sm:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700">Deskripsi lokasi</label>
                <textarea
                    name="location_description"
                    rows="4"
                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                ><?php echo e($isEditModalActive ? old('location_description') : $zone->location_description); ?></textarea>
            </div>

            <div class="flex flex-wrap justify-end gap-3 sm:col-span-2">
                <button type="button" data-modal-close class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-slate-600 transition hover:bg-surface-soft">
                    Batal
                </button>
                <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                    Simpan Perubahan
                </button>
            </div>
        </form>
     <?php echo $__env->renderComponent(); ?>
<?php endif; ?>
<?php if (isset($__attributesOriginal9f64f32e90b9102968f2bc548315018c)): ?>
<?php $attributes = $__attributesOriginal9f64f32e90b9102968f2bc548315018c; ?>
<?php unset($__attributesOriginal9f64f32e90b9102968f2bc548315018c); ?>
<?php endif; ?>
<?php if (isset($__componentOriginal9f64f32e90b9102968f2bc548315018c)): ?>
<?php $component = $__componentOriginal9f64f32e90b9102968f2bc548315018c; ?>
<?php unset($__componentOriginal9f64f32e90b9102968f2bc548315018c); ?>
<?php endif; ?>

    <?php if (isset($component)) { $__componentOriginal9f64f32e90b9102968f2bc548315018c = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal9f64f32e90b9102968f2bc548315018c = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.modal','data' => ['id' => $samplingModalId,'title' => 'Input data sampling','description' => 'Masukkan beberapa titik sampling untuk merepresentasikan '.$zone->name.' secara lebih akurat.','maxWidth' => 'max-w-6xl']] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('modal'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes(['id' => \Illuminate\View\Compilers\BladeCompiler::sanitizeComponentAttribute($samplingModalId),'title' => 'Input data sampling','description' => \Illuminate\View\Compilers\BladeCompiler::sanitizeComponentAttribute('Masukkan beberapa titik sampling untuk merepresentasikan '.$zone->name.' secara lebih akurat.'),'max-width' => 'max-w-6xl']); ?>
        <div class="grid gap-6 xl:grid-cols-[2fr,1fr]">
            <section class="space-y-5">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Progress Sampling</h2>
                    <p class="mt-1 text-sm text-slate-500">Target minimum <?php echo e($zone->sample_target_count); ?> titik untuk zona ini.</p>
                </div>
                <div class="h-3 rounded-full bg-slate-200">
                    <?php
                        $progress = min(100, (($samples->count() ?? 0) / max($zone->sample_target_count, 1)) * 100);
                    ?>
                    <div class="h-3 rounded-full bg-primary" style="width: <?php echo e($progress); ?>%"></div>
                </div>
                <div class="text-sm font-medium text-slate-600"><?php echo e($samples->count()); ?> dari <?php echo e($zone->sample_target_count); ?> titik terisi</div>

                <form action="<?php echo e(route('zones.sampling.store', $zone)); ?>" method="POST" class="space-y-4">
                    <?php echo csrf_field(); ?>
                    <input type="hidden" name="_open_modal" value="<?php echo e($samplingModalId); ?>">

                    <div>
                        <label class="mb-2 block text-sm font-semibold text-slate-700">Waktu sampling</label>
                        <input type="datetime-local" name="sampled_at" value="<?php echo e(old('sampled_at', now()->format('Y-m-d\TH:i'))); ?>" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
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
                        <div id="samplingRowsModal" class="divide-y divide-outline">
                            <?php for($i = 0; $i < $samplingRowsCount; $i++): ?>
                                <div class="grid gap-3 bg-white px-5 py-4 md:grid-cols-[1.3fr,repeat(5,minmax(0,1fr))]">
                                    <input type="text" name="point_label[]" value="<?php echo e($samplingPointLabels[$i] ?? 'Point '.$zone->name.'-'.($i + 1)); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="Point Alpha-1" required>
                                    <input type="number" step="0.1" min="0" max="14" name="ph[]" value="<?php echo e($samplingPh[$i] ?? ''); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="6.4" required>
                                    <input type="number" step="0.1" min="0" name="nitrogen[]" value="<?php echo e($samplingNitrogen[$i] ?? ''); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="110" required>
                                    <input type="number" step="0.1" min="0" name="phosphorus[]" value="<?php echo e($samplingPhosphorus[$i] ?? ''); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="45" required>
                                    <input type="number" step="0.1" min="0" name="potassium[]" value="<?php echo e($samplingPotassium[$i] ?? ''); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="85" required>
                                    <input type="number" step="0.1" min="0" max="100" name="soil_moisture[]" value="<?php echo e($samplingMoisture[$i] ?? ''); ?>" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" placeholder="42">
                                </div>
                            <?php endfor; ?>
                        </div>
                    </div>

                    <div class="flex flex-wrap gap-3">
                        <button id="addSamplingRow" type="button" class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                            + Tambah Titik
                        </button>
                        <div class="ml-auto flex flex-wrap gap-3">
                            <button type="button" data-modal-close class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-slate-600 transition hover:bg-surface-soft">
                                Tutup
                            </button>
                            <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                                Simpan Sampling
                            </button>
                        </div>
                    </div>
                </form>
            </section>

            <aside class="rounded-3xl border border-outline bg-surface-soft p-6">
                <h2 class="text-2xl font-bold tracking-tight text-slate-900">Estimasi Zona</h2>
                <div class="mt-5 space-y-4">
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-slate-500">Rata-rata pH</span>
                        <span class="font-bold text-slate-900"><?php echo e(number_format($aggregate['ph']['mean'] ?? 0, 2)); ?></span>
                    </div>
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-slate-500">Rata-rata NPK</span>
                        <span class="font-bold text-slate-900">
                            <?php echo e(number_format($aggregate['nitrogen']['mean'] ?? 0, 0)); ?>/<?php echo e(number_format($aggregate['phosphorus']['mean'] ?? 0, 0)); ?>/<?php echo e(number_format($aggregate['potassium']['mean'] ?? 0, 0)); ?>

                        </span>
                    </div>
                    <div class="rounded-2xl border border-sky-200 bg-sky-50 px-4 py-4 text-sm text-sky-900">
                        Selesaikan input minimal <?php echo e(max(4, $zone->sample_target_count)); ?> titik agar rekomendasi AI lebih stabil dan lebih mewakili variasi zona.
                    </div>
                </div>
            </aside>
        </div>
     <?php echo $__env->renderComponent(); ?>
<?php endif; ?>
<?php if (isset($__attributesOriginal9f64f32e90b9102968f2bc548315018c)): ?>
<?php $attributes = $__attributesOriginal9f64f32e90b9102968f2bc548315018c; ?>
<?php unset($__attributesOriginal9f64f32e90b9102968f2bc548315018c); ?>
<?php endif; ?>
<?php if (isset($__componentOriginal9f64f32e90b9102968f2bc548315018c)): ?>
<?php $component = $__componentOriginal9f64f32e90b9102968f2bc548315018c; ?>
<?php unset($__componentOriginal9f64f32e90b9102968f2bc548315018c); ?>
<?php endif; ?>
<?php $__env->stopSection(); ?>

<?php $__env->startPush('scripts'); ?>
    <script>
        const radarProfile = <?php echo json_encode($radar_profile, 15, 512) ?>;
        const radarCtx = document.getElementById('zoneRadarChart');

        if (radarCtx) {
            new Chart(radarCtx, {
                type: 'radar',
                data: {
                    labels: radarProfile.labels,
                    datasets: [
                        {
                            label: 'Current',
                            data: radarProfile.current,
                            borderColor: '#0b4f7d',
                            backgroundColor: 'rgba(11, 79, 125, 0.14)',
                            pointBackgroundColor: '#0b4f7d',
                        },
                        {
                            label: 'Ideal',
                            data: radarProfile.ideal,
                            borderColor: '#154212',
                            backgroundColor: 'rgba(21, 66, 18, 0.05)',
                            pointBackgroundColor: '#154212',
                            borderDash: [6, 6],
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: '#e5e7eb' },
                            grid: { color: '#e5e7eb' },
                            pointLabels: { color: '#475569', font: { size: 11, weight: '600' } },
                            ticks: { display: false }
                        }
                    },
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        document.getElementById('addSamplingRow')?.addEventListener('click', function () {
            const container = document.getElementById('samplingRowsModal');
            const count = container.children.length + 1;
            const row = document.createElement('div');
            row.className = 'grid gap-3 bg-white px-5 py-4 md:grid-cols-[1.3fr,repeat(5,minmax(0,1fr))]';
            row.innerHTML = `
                <input type="text" name="point_label[]" value="Point <?php echo e($zone->name); ?>-${count}" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" max="14" name="ph[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="nitrogen[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="phosphorus[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" name="potassium[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
                <input type="number" step="0.1" min="0" max="100" name="soil_moisture[]" class="rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
            `;
            container.appendChild(row);
        });
    </script>
<?php $__env->stopPush(); ?>

<?php echo $__env->make('layouts.app', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?><?php /**PATH /var/www/html/resources/views/zones/show.blade.php ENDPATH**/ ?>