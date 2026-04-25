<?php $attributes ??= new \Illuminate\View\ComponentAttributeBag;

$__newAttributes = [];
$__propNames = \Illuminate\View\ComponentAttributeBag::extractPropNames(([
    'id',
    'title' => null,
    'description' => null,
    'maxWidth' => 'max-w-3xl',
]));

foreach ($attributes->all() as $__key => $__value) {
    if (in_array($__key, $__propNames)) {
        $$__key = $$__key ?? $__value;
    } else {
        $__newAttributes[$__key] = $__value;
    }
}

$attributes = new \Illuminate\View\ComponentAttributeBag($__newAttributes);

unset($__propNames);
unset($__newAttributes);

foreach (array_filter(([
    'id',
    'title' => null,
    'description' => null,
    'maxWidth' => 'max-w-3xl',
]), 'is_string', ARRAY_FILTER_USE_KEY) as $__key => $__value) {
    $$__key = $$__key ?? $__value;
}

$__defined_vars = get_defined_vars();

foreach ($attributes->all() as $__key => $__value) {
    if (array_key_exists($__key, $__defined_vars)) unset($$__key);
}

unset($__defined_vars, $__key, $__value); ?>

<div
    id="<?php echo e($id); ?>"
    data-modal
    class="fixed inset-0 z-[70] hidden"
    role="dialog"
    aria-modal="true"
    aria-labelledby="<?php echo e($id); ?>-title"
>
    <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" data-modal-close></div>
    <div class="relative flex min-h-full items-end justify-center p-4 sm:items-center sm:p-6">
        <div class="relative w-full <?php echo e($maxWidth); ?> overflow-hidden rounded-[2rem] border border-outline bg-surface shadow-2xl">
            <div class="flex items-start justify-between gap-4 border-b border-outline px-5 py-4 sm:px-6">
                <div class="min-w-0">
                    <?php if($title): ?>
                        <h2 id="<?php echo e($id); ?>-title" class="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl"><?php echo e($title); ?></h2>
                    <?php endif; ?>
                    <?php if($description): ?>
                        <p class="mt-1 text-sm text-slate-500"><?php echo e($description); ?></p>
                    <?php endif; ?>
                </div>
                <button
                    type="button"
                    data-modal-close
                    class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-slate-500 transition hover:bg-surface-soft hover:text-slate-900"
                    aria-label="Tutup modal"
                >
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <div class="app-scrollbar max-h-[calc(100vh-6rem)] overflow-y-auto px-5 py-5 sm:px-6 sm:py-6">
                <?php echo e($slot); ?>

            </div>
        </div>
    </div>
</div>
<?php /**PATH /var/www/html/resources/views/components/modal.blade.php ENDPATH**/ ?>