<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $__env->yieldContent('title', 'Vera AI'); ?></title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        background: '#fafaf4',
                        surface: '#ffffff',
                        'surface-soft': '#f4f4ee',
                        'surface-muted': '#eeeee9',
                        primary: '#154212',
                        'primary-soft': '#e5f0e1',
                        secondary: '#5e5e5c',
                        accent: '#0b4f7d',
                        outline: '#d8d9d2',
                        success: '#2d5a27',
                        warning: '#a15c00',
                        danger: '#c63b2d',
                    },
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    boxShadow: {
                        panel: '0 8px 28px rgba(21, 66, 18, 0.05)',
                    },
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        body.modal-open { overflow: hidden; }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .app-scrollbar::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        .app-scrollbar::-webkit-scrollbar-thumb {
            background: #d7d9d0;
            border-radius: 999px;
        }
    </style>
    <?php echo $__env->yieldPushContent('head'); ?>
</head>
<body class="bg-background text-slate-900 antialiased overflow-hidden">
    <div class="flex h-screen">
        <aside class="hidden md:flex w-72 shrink-0 flex-col border-r border-outline bg-surface">
            <div class="px-6 py-6 border-b border-outline">
                <div class="flex items-center gap-3">
                    <div class="h-12 w-12 rounded-xl bg-primary text-white flex items-center justify-center shadow-panel">
                        <span class="material-symbols-outlined">spa</span>
                    </div>
                    <div>
                        <div class="text-2xl font-extrabold tracking-tight text-primary">Vera AI</div>
                        <div class="text-sm text-slate-500">Precision Vegetation</div>
                    </div>
                </div>
            </div>

            <nav class="flex-1 px-4 py-5 space-y-1 app-scrollbar overflow-y-auto">
                <?php
                    $navItems = [
                        ['route' => 'dashboard', 'label' => 'Dashboard', 'icon' => 'dashboard'],
                        ['route' => 'zones.index', 'label' => 'Field Zones', 'icon' => 'potted_plant'],
                        ['route' => 'history', 'label' => 'Reports', 'icon' => 'analytics'],
                    ];
                ?>

                <?php $__currentLoopData = $navItems; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $item): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                    <a
                        href="<?php echo e(route($item['route'])); ?>"
                        class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition <?php echo e(request()->routeIs($item['route']) || ($item['route'] === 'zones.index' && request()->routeIs('zones.*')) ? 'bg-primary-soft text-primary border-l-4 border-primary' : 'text-slate-600 hover:bg-surface-soft hover:text-primary'); ?>"
                    >
                        <span class="material-symbols-outlined"><?php echo e($item['icon']); ?></span>
                        <span><?php echo e($item['label']); ?></span>
                    </a>
                <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>

                <div class="pt-4 mt-4 border-t border-outline">
                    <div class="px-4 pb-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Workflow</div>
                    <a href="<?php echo e(route('zones.index')); ?>" class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-600 hover:bg-surface-soft hover:text-primary">
                        <span class="material-symbols-outlined">science</span>
                        <span>Soil Lab</span>
                    </a>
                    <a href="<?php echo e(route('zones.index')); ?>" class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-600 hover:bg-surface-soft hover:text-primary">
                        <span class="material-symbols-outlined">psychology</span>
                        <span>AI Advisor</span>
                    </a>
                </div>
            </nav>

            <div class="p-4 border-t border-outline space-y-3">
                <a href="<?php echo e(route('zones.index')); ?>" class="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-success">
                    <span class="material-symbols-outlined text-[20px]">add_chart</span>
                    <span>Run New Analysis</span>
                </a>
                <div class="space-y-1 text-sm">
                    <div class="flex items-center gap-3 rounded-xl px-4 py-3 text-slate-500">
                        <span class="material-symbols-outlined text-[20px]">settings</span>
                        <span>Settings</span>
                    </div>
                    <div class="flex items-center gap-3 rounded-xl px-4 py-3 text-slate-500">
                        <span class="material-symbols-outlined text-[20px]">contact_support</span>
                        <span>Support</span>
                    </div>
                </div>
            </div>
        </aside>

        <div class="flex min-w-0 flex-1 flex-col">
            <header class="sticky top-0 z-30 border-b border-outline bg-white/90 backdrop-blur">
                <div class="flex items-center justify-between gap-4 px-5 py-4 md:px-8">
                    <div class="flex min-w-0 items-center gap-4">
                        <a href="<?php echo e(route('dashboard')); ?>" class="md:hidden text-xl font-extrabold tracking-tight text-primary">Vera AI</a>
                        <div class="hidden md:flex items-center relative w-80 max-w-full">
                            <span class="material-symbols-outlined absolute left-3 text-slate-400">search</span>
                            <input type="text" placeholder="Cari zona, rekomendasi, atau titik sampling..." class="w-full rounded-full border-0 bg-surface-soft pl-10 pr-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:ring-2 focus:ring-primary/15">
                        </div>
                    </div>
                    <div class="flex items-center gap-2 md:gap-3">
                        <button class="rounded-full p-2 text-slate-500 hover:bg-surface-soft">
                            <span class="material-symbols-outlined">notifications</span>
                        </button>
                        <button class="rounded-full p-2 text-slate-500 hover:bg-surface-soft">
                            <span class="material-symbols-outlined">settings</span>
                        </button>
                        <button class="rounded-full p-2 text-slate-500 hover:bg-surface-soft">
                            <span class="material-symbols-outlined">help</span>
                        </button>
                        <div class="ml-1 flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft text-primary font-bold">
                            AI
                        </div>
                    </div>
                </div>
            </header>

            <main class="app-scrollbar flex-1 overflow-y-auto px-4 py-5 md:px-8 md:py-8">
                <?php if(session('success')): ?>
                    <div class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-800">
                        <?php echo e(session('success')); ?>

                    </div>
                <?php endif; ?>

                <?php if($errors->any()): ?>
                    <div class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-800">
                        <div class="font-semibold mb-1">Ada input yang perlu diperbaiki.</div>
                        <ul class="list-disc pl-5 space-y-1">
                            <?php $__currentLoopData = $errors->all(); $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $error): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?>
                                <li><?php echo e($error); ?></li>
                            <?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?>
                        </ul>
                    </div>
                <?php endif; ?>

                <?php echo $__env->yieldContent('content'); ?>
            </main>
        </div>
    </div>

    <?php echo $__env->yieldPushContent('scripts'); ?>
    <script>
        (function () {
            const initialModalId = <?php echo json_encode(old('_open_modal', request('modal')), 512) ?>;
            const modalSelector = '[data-modal]';

            const setBodyLock = () => {
                const hasVisibleModal = Array.from(document.querySelectorAll(modalSelector)).some((modal) => !modal.classList.contains('hidden'));
                document.body.classList.toggle('modal-open', hasVisibleModal);
            };

            const openModal = (modalId) => {
                const modal = document.getElementById(modalId);

                if (!modal) {
                    return;
                }

                modal.classList.remove('hidden');
                setBodyLock();
            };

            const closeModal = (modal) => {
                if (!modal) {
                    return;
                }

                modal.classList.add('hidden');
                setBodyLock();
            };

            document.querySelectorAll('[data-modal-open]').forEach((trigger) => {
                trigger.addEventListener('click', () => openModal(trigger.dataset.modalOpen));
            });

            document.querySelectorAll('[data-modal-close]').forEach((trigger) => {
                trigger.addEventListener('click', () => closeModal(trigger.closest(modalSelector)));
            });

            document.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape') {
                    return;
                }

                const activeModal = Array.from(document.querySelectorAll(modalSelector)).find((modal) => !modal.classList.contains('hidden'));
                closeModal(activeModal);
            });

            document.querySelectorAll('form[data-confirm-delete]').forEach((form) => {
                form.addEventListener('submit', (event) => {
                    event.preventDefault();

                    Swal.fire({
                        title: form.dataset.confirmTitle || 'Hapus data ini?',
                        text: form.dataset.confirmText || 'Tindakan ini tidak bisa dibatalkan.',
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: form.dataset.confirmButton || 'Ya, hapus',
                        cancelButtonText: 'Batal',
                        confirmButtonColor: '#c63b2d',
                        cancelButtonColor: '#64748b',
                        reverseButtons: true,
                        focusCancel: true,
                    }).then((result) => {
                        if (result.isConfirmed) {
                            form.submit();
                        }
                    });
                });
            });

            if (initialModalId) {
                openModal(initialModalId);
            }
        }());
    </script>
</body>
</html>
<?php /**PATH /var/www/html/resources/views/layouts/app.blade.php ENDPATH**/ ?>