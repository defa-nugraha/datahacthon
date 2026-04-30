<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="dicoding:email" content="starduststr0@gmail.com">
    <meta name="dicoding:email" content="tsaqib.nur@gmail.com">
    <meta name="dicoding:email" content="tsaqib.nur@gmail.com">
    <title>{{ config('app.name', 'Vera AI') }}</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
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
        .vera-tour-root.hidden {
            display: none;
        }
        .vera-tour-root {
            position: fixed;
            inset: 0;
            z-index: 80;
            pointer-events: none;
        }
        .vera-tour-backdrop {
            position: absolute;
            inset: 0;
            background: rgba(15, 23, 42, 0.56);
            backdrop-filter: blur(2px);
            pointer-events: auto;
        }
        .vera-tour-highlight {
            position: fixed;
            border-radius: 24px;
            border: 2px solid rgba(255, 255, 255, 0.96);
            box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.54), 0 18px 60px rgba(21, 66, 18, 0.25);
            transition: width 180ms ease, height 180ms ease, transform 180ms ease;
            pointer-events: none;
        }
        .vera-tour-card {
            position: fixed;
            width: min(360px, calc(100vw - 32px));
            border-radius: 24px;
            background: #ffffff;
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
            pointer-events: auto;
            transition: left 180ms ease, top 180ms ease;
        }
    </style>
    @stack('head')
</head>
<body class="bg-background text-slate-900 antialiased overflow-hidden">
    <div class="flex h-screen">
        <aside class="hidden md:flex w-72 shrink-0 flex-col border-r border-outline bg-surface">
            <div class="px-6 py-6 border-b border-outline">
                <div class="flex items-center gap-3" data-tour="brand">
                    <x-application-logo class="h-16 w-16" />
                    <div>
                        <div class="text-2xl font-extrabold tracking-tight text-primary">Vera AI</div>
                        <div class="text-sm text-slate-500">Precision Vegetation</div>
                    </div>
                </div>
            </div>

            <nav class="flex-1 px-4 py-5 space-y-1 app-scrollbar overflow-y-auto" data-tour="navigation">
                @php
                    $isAdmin = Auth::user()?->isAdmin();
                    $navItems = $isAdmin
                        ? [
                            ['route' => 'admin.dashboard', 'label' => 'Admin Console', 'icon' => 'admin_panel_settings', 'active' => 'admin.*'],
                            ['route' => 'zones.index', 'label' => 'Field Zones', 'icon' => 'potted_plant', 'active' => 'zones.*'],
                            ['route' => 'devices.index', 'label' => 'Devices', 'icon' => 'router', 'active' => 'devices.*'],
                            ['route' => 'history', 'label' => 'Reports', 'icon' => 'analytics', 'active' => 'history'],
                        ]
                        : [
                            ['route' => 'dashboard', 'label' => 'Dashboard', 'icon' => 'dashboard', 'active' => 'dashboard'],
                            ['route' => 'zones.index', 'label' => 'Zona Lahan', 'icon' => 'potted_plant', 'active' => 'zones.*'],
                            ['route' => 'history', 'label' => 'Riwayat', 'icon' => 'analytics', 'active' => 'history'],
                        ];
                @endphp

                @foreach ($navItems as $item)
                    <a
                        href="{{ route($item['route']) }}"
                        class="flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition {{ request()->routeIs($item['active']) ? 'bg-primary-soft text-primary border-l-4 border-primary' : 'text-slate-600 hover:bg-surface-soft hover:text-primary' }}"
                    >
                        <span class="material-symbols-outlined">{{ $item['icon'] }}</span>
                        <span>{{ $item['label'] }}</span>
                    </a>
                @endforeach

            </nav>

            <div class="p-4 border-t border-outline space-y-3">
                <a href="{{ route($isAdmin ? 'admin.dashboard' : 'zones.index') }}" data-tour="primary-action" class="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-success">
                    <span class="material-symbols-outlined text-[20px]">add_chart</span>
                    <span>{{ $isAdmin ? 'Open Admin Console' : 'Run New Analysis' }}</span>
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
                        <a href="{{ route(Auth::user()?->isAdmin() ? 'admin.dashboard' : 'dashboard') }}" class="md:hidden text-xl font-extrabold tracking-tight text-primary">Vera AI</a>
                        <div class="hidden md:flex items-center relative w-80 max-w-full" data-tour="search">
                            <span class="material-symbols-outlined absolute left-3 text-slate-400">search</span>
                            <input type="text" placeholder="Cari zona, rekomendasi, atau titik sampling..." class="w-full rounded-full border-0 bg-surface-soft pl-10 pr-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:ring-2 focus:ring-primary/15">
                        </div>
                    </div>
                    <div class="flex items-center gap-2 md:gap-3">
                        <button type="button" data-tour-restart class="rounded-full p-2 text-slate-500 hover:bg-surface-soft" title="Panduan aplikasi" aria-label="Buka panduan aplikasi">
                            <span class="material-symbols-outlined">help</span>
                        </button>
                        <button class="rounded-full p-2 text-slate-500 hover:bg-surface-soft">
                            <span class="material-symbols-outlined">notifications</span>
                        </button>
                        @if (Auth::user()?->isAdmin())
                            <a href="{{ route('devices.index') }}" class="rounded-full p-2 text-slate-500 hover:bg-surface-soft transition-colors" title="Manage Devices">
                                <span class="material-symbols-outlined">router</span>
                            </a>
                        @endif
                        
                        <div x-data="{ open: false }" class="relative" data-tour="profile-menu">
                            <button @click="open = !open" @click.outside="open = false" class="flex items-center transition duration-150 ease-in-out focus:outline-none">
                                <div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft text-primary font-bold hover:bg-primary hover:text-white transition-all shadow-sm">
                                    {{ strtoupper(substr(Auth::user()->name, 0, 2)) }}
                                </div>
                            </button>

                            <div x-show="open" 
                                x-transition:enter="transition ease-out duration-200"
                                x-transition:enter-start="opacity-0 scale-95"
                                x-transition:enter-end="opacity-100 scale-100"
                                x-transition:leave="transition ease-in duration-75"
                                x-transition:leave-start="opacity-100 scale-100"
                                x-transition:leave-end="opacity-0 scale-95"
                                class="absolute right-0 mt-2 w-56 rounded-2xl border border-outline bg-white shadow-panel z-50 py-2 origin-top-right"
                                style="display: none;">
                                
                                <div class="px-4 py-2 border-b border-outline mb-1">
                                    <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">User Profile</p>
                                    <p class="text-sm font-bold text-slate-800 truncate">{{ Auth::user()->name }}</p>
                                    <p class="text-[11px] text-slate-500 truncate">{{ Auth::user()->email }}</p>
                                </div>

                                <a href="{{ route('profile.edit') }}" class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-surface-soft hover:text-primary transition">
                                    <span class="material-symbols-outlined text-[20px]">settings</span>
                                    <span>Settings Profile</span>
                                </a>

                                <div class="border-t border-outline mt-1 pt-1">
                                    <form method="POST" action="{{ route('logout') }}">
                                        @csrf
                                        <button type="submit" class="flex w-full items-center gap-3 px-4 py-2.5 text-sm font-bold text-rose-600 hover:bg-rose-50 transition">
                                            <span class="material-symbols-outlined text-[20px]">logout</span>
                                            <span>Log Out</span>
                                        </button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <main class="app-scrollbar flex-1 overflow-y-auto px-4 py-5 md:px-8 md:py-8">
                @if (session('success'))
                    <div class="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-800">
                        {{ session('success') }}
                    </div>
                @endif

                @if ($errors->any())
                    <div class="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-800">
                        <div class="font-semibold mb-1">Ada input yang perlu diperbaiki.</div>
                        <ul class="list-disc pl-5 space-y-1">
                            @foreach ($errors->all() as $error)
                                <li>{{ $error }}</li>
                            @endforeach
                        </ul>
                    </div>
                @endif

                @if(isset($slot))
                    {{ $slot }}
                @else
                    @yield('content')
                @endif
            </main>
        </div>
    </div>

    <div id="veraTourRoot" class="vera-tour-root hidden" aria-live="polite" aria-modal="true" role="dialog">
        <div class="vera-tour-backdrop" data-tour-close></div>
        <div id="veraTourHighlight" class="vera-tour-highlight"></div>
        <section id="veraTourCard" class="vera-tour-card border border-outline p-5">
            <div class="flex items-start gap-4">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                    <span id="veraTourIcon" class="material-symbols-outlined">explore</span>
                </div>
                <div class="min-w-0">
                    <div id="veraTourEyebrow" class="text-[11px] font-bold uppercase tracking-[0.2em] text-slate-400">Panduan</div>
                    <h2 id="veraTourTitle" class="mt-1 text-xl font-extrabold tracking-tight text-slate-900">Selamat datang</h2>
                    <p id="veraTourBody" class="mt-2 text-sm leading-6 text-slate-600"></p>
                </div>
            </div>
            <div class="mt-5 h-1.5 rounded-full bg-surface-soft">
                <div id="veraTourProgress" class="h-1.5 rounded-full bg-primary transition-all"></div>
            </div>
            <div class="mt-5 flex items-center justify-between gap-3">
                <button type="button" id="veraTourSkip" class="text-sm font-semibold text-slate-500 hover:text-slate-800">Lewati</button>
                <div class="flex items-center gap-2">
                    <button type="button" id="veraTourBack" class="rounded-xl border border-outline px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-surface-soft">Kembali</button>
                    <button type="button" id="veraTourNext" class="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-success">Lanjut</button>
                </div>
            </div>
        </section>
    </div>

    @stack('scripts')
    <script>
        (function () {
            const initialModalId = @json(old('_open_modal', request('modal')));
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
    <script>
        (function () {
            const role = @json($isAdmin ? 'admin' : 'farmer');
            const storageKey = `vera-ai-onboarding-v3-${role}`;
            const forceTourFromUrl = new URLSearchParams(window.location.search).get('tour') === '1';
            const root = document.getElementById('veraTourRoot');
            const card = document.getElementById('veraTourCard');
            const highlight = document.getElementById('veraTourHighlight');
            const title = document.getElementById('veraTourTitle');
            const body = document.getElementById('veraTourBody');
            const eyebrow = document.getElementById('veraTourEyebrow');
            const icon = document.getElementById('veraTourIcon');
            const progress = document.getElementById('veraTourProgress');
            const backButton = document.getElementById('veraTourBack');
            const nextButton = document.getElementById('veraTourNext');
            const skipButton = document.getElementById('veraTourSkip');
            let activeSteps = [];
            let currentIndex = 0;
            let isOpen = false;

            if (!root || !card || !highlight) {
                return;
            }

            const allSteps = [
                {
                    target: 'brand',
                    roles: ['farmer', 'admin'],
                    icon: 'psychiatry',
                    title: 'Vera AI berbasis zona',
                    body: 'Aplikasi ini membaca beberapa titik sampling dalam satu zona, lalu menghasilkan rekomendasi tanaman dan saran penanganan yang lebih representatif.'
                },
                {
                    target: 'navigation',
                    roles: ['farmer', 'admin'],
                    icon: 'menu',
                    title: 'Navigasi utama',
                    body: 'Gunakan menu ini untuk berpindah antara dashboard, zona lahan, riwayat, dan fitur khusus sesuai role akun.'
                },
                {
                    target: 'dashboard-overview',
                    roles: ['farmer'],
                    icon: 'dashboard',
                    title: 'Ringkasan operasional',
                    body: 'Bagian ini menampilkan status umum sistem: jumlah zona, sampling terbaru, dan rekomendasi AI yang sudah tersedia.'
                },
                {
                    target: 'zone-metrics',
                    roles: ['farmer'],
                    icon: 'monitoring',
                    title: 'KPI zona',
                    body: 'Kartu ini membantu melihat apakah data zona sudah cukup aktif dan siap dianalisis.'
                },
                {
                    target: 'soil-trend',
                    roles: ['farmer'],
                    icon: 'show_chart',
                    title: 'Tren unsur hara',
                    body: 'Grafik NPK dan pH dipakai untuk membaca perubahan kondisi tanah, bukan hanya satu nilai sesaat.'
                },
                {
                    target: 'start-analysis',
                    roles: ['farmer'],
                    icon: 'science',
                    title: 'Mulai analisis',
                    body: 'Masuk ke daftar zona untuk menambah titik sampling atau menjalankan rekomendasi vegetasi.'
                },
                {
                    target: 'field-zones-summary',
                    roles: ['farmer'],
                    icon: 'potted_plant',
                    title: 'Zona lahan',
                    body: 'Setiap kartu zona menunjukkan status sampling, tanaman aktif, dan akses menuju detail monitoring.'
                },
                {
                    target: 'zones-header',
                    roles: ['farmer', 'admin'],
                    icon: 'map',
                    title: 'Kelola zona tanam',
                    body: 'Halaman ini dipakai untuk membuat, mengedit, menghapus, dan membuka detail zona.'
                },
                {
                    target: 'add-zone',
                    roles: ['farmer', 'admin'],
                    icon: 'add_location_alt',
                    title: 'Tambah zona',
                    body: 'Buat zona baru sebelum mengisi data sampling. Minimal beberapa titik diperlukan agar analisis lebih stabil.'
                },
                {
                    target: 'zone-list',
                    roles: ['farmer', 'admin'],
                    icon: 'grid_view',
                    title: 'Daftar zona',
                    body: 'Gunakan kartu zona untuk melihat status data, menambah sampling, membuka live monitor, atau melihat detail.'
                },
                {
                    target: 'zone-detail-header',
                    roles: ['farmer', 'admin'],
                    icon: 'fact_check',
                    title: 'Detail zona',
                    body: 'Di halaman detail, data titik sampling diringkas menjadi representasi zona untuk model AI.'
                },
                {
                    target: 'detail-add-sampling',
                    roles: ['farmer', 'admin'],
                    icon: 'add_circle',
                    title: 'Input titik sampling',
                    body: 'Tambahkan beberapa titik dengan pH, N, P, K, dan kelembapan agar variasi kondisi lahan tetap terbaca.'
                },
                {
                    target: 'run-ai-analysis',
                    roles: ['farmer', 'admin'],
                    icon: 'psychology',
                    title: 'Jalankan analisis AI',
                    body: 'Setelah sampling cukup, tombol ini mengirim agregasi zona ke model rekomendasi vegetasi.'
                },
                {
                    target: 'zone-health-cards',
                    roles: ['farmer', 'admin'],
                    icon: 'health_and_safety',
                    title: 'Kesehatan zona',
                    body: 'Kartu ini menampilkan rata-rata dan rentang kondisi tanah yang dipakai untuk memahami kesiapan zona.'
                },
                {
                    target: 'adaptive-advice',
                    roles: ['farmer', 'admin'],
                    icon: 'tips_and_updates',
                    title: 'Saran penanganan',
                    body: 'Jika tanaman aktif sudah dipilih, Vera AI dapat memberi rekomendasi tindakan berdasarkan histori unsur hara terakhir.'
                },
                {
                    target: 'admin-overview',
                    roles: ['admin'],
                    icon: 'admin_panel_settings',
                    title: 'Admin Console',
                    body: 'Admin memantau kesiapan user, device, sampling, dan zona sebelum dipakai petani.'
                },
                {
                    target: 'admin-metrics',
                    roles: ['admin'],
                    icon: 'analytics',
                    title: 'Metrik operasional',
                    body: 'Kartu ini membantu admin mengecek jumlah user, zona, sampling 24 jam, dan device online.'
                },
                {
                    target: 'user-management',
                    roles: ['admin'],
                    icon: 'manage_accounts',
                    title: 'Manajemen user',
                    body: 'Admin dapat mengatur role user agar halaman petani dan admin tetap terpisah.'
                },
                {
                    target: 'device-summary',
                    roles: ['admin'],
                    icon: 'router',
                    title: 'Ringkasan device',
                    body: 'Pantau sensor atau gateway yang terhubung sebagai sumber data sampling lahan.'
                },
                {
                    target: 'zone-readiness',
                    roles: ['admin'],
                    icon: 'verified',
                    title: 'Kesiapan zona',
                    body: 'Admin dapat mengecek zona mana yang sudah punya sampling cukup untuk dianalisis.'
                },
                {
                    target: 'primary-action',
                    roles: ['farmer', 'admin'],
                    icon: 'rocket_launch',
                    title: 'Aksi cepat',
                    body: role === 'admin'
                        ? 'Gunakan tombol ini untuk kembali ke pusat kontrol admin.'
                        : 'Gunakan tombol ini untuk masuk cepat ke alur analisis zona.'
                }
            ];

            const isVisible = (element) => {
                if (!element) {
                    return false;
                }

                const style = window.getComputedStyle(element);
                return style.display !== 'none'
                    && style.visibility !== 'hidden'
                    && element.getClientRects().length > 0;
            };

            const collectSteps = () => allSteps
                .filter((step) => step.roles.includes(role))
                .map((step) => ({ ...step, element: document.querySelector(`[data-tour="${step.target}"]`) }))
                .filter((step) => isVisible(step.element));

            const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

            const positionTour = () => {
                if (!isOpen || !activeSteps[currentIndex]) {
                    return;
                }

                const target = activeSteps[currentIndex].element;
                const rect = target.getBoundingClientRect();
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;
                const padding = viewportWidth < 640 ? 8 : 12;
                const margin = 16;

                highlight.style.width = `${Math.max(rect.width + padding * 2, 48)}px`;
                highlight.style.height = `${Math.max(rect.height + padding * 2, 48)}px`;
                highlight.style.transform = `translate(${Math.max(rect.left - padding, margin / 2)}px, ${Math.max(rect.top - padding, margin / 2)}px)`;

                const cardRect = card.getBoundingClientRect();
                let left = rect.left + (rect.width / 2) - (cardRect.width / 2);
                left = clamp(left, margin, viewportWidth - cardRect.width - margin);

                let top = rect.bottom + 16;
                if (top + cardRect.height > viewportHeight - margin) {
                    top = rect.top - cardRect.height - 16;
                }
                if (top < margin) {
                    top = clamp((viewportHeight - cardRect.height) / 2, margin, viewportHeight - cardRect.height - margin);
                }

                card.style.left = `${left}px`;
                card.style.top = `${top}px`;
            };

            const renderStep = () => {
                const step = activeSteps[currentIndex];

                if (!step) {
                    closeTour(true);
                    return;
                }

                eyebrow.textContent = `Panduan ${currentIndex + 1} dari ${activeSteps.length}`;
                icon.textContent = step.icon || 'explore';
                title.textContent = step.title;
                body.textContent = step.body;
                progress.style.width = `${((currentIndex + 1) / activeSteps.length) * 100}%`;
                backButton.disabled = currentIndex === 0;
                backButton.classList.toggle('opacity-40', currentIndex === 0);
                nextButton.textContent = currentIndex === activeSteps.length - 1 ? 'Selesai' : 'Lanjut';

                step.element.scrollIntoView({ block: 'center', inline: 'center', behavior: 'smooth' });
                window.setTimeout(positionTour, 260);
            };

            const openTour = (force = false) => {
                if (!force && localStorage.getItem(storageKey) === 'completed') {
                    return;
                }

                activeSteps = collectSteps();
                if (activeSteps.length === 0) {
                    return;
                }

                currentIndex = 0;
                isOpen = true;
                root.classList.remove('hidden');
                document.body.classList.add('modal-open');
                renderStep();
            };

            const closeTour = (markCompleted = true) => {
                isOpen = false;
                root.classList.add('hidden');
                document.body.classList.remove('modal-open');

                if (markCompleted) {
                    localStorage.setItem(storageKey, 'completed');
                }
            };

            nextButton.addEventListener('click', () => {
                if (currentIndex >= activeSteps.length - 1) {
                    closeTour(true);
                    return;
                }

                currentIndex += 1;
                renderStep();
            });

            backButton.addEventListener('click', () => {
                if (currentIndex === 0) {
                    return;
                }

                currentIndex -= 1;
                renderStep();
            });

            skipButton.addEventListener('click', () => closeTour(true));
            root.querySelector('[data-tour-close]')?.addEventListener('click', () => closeTour(true));

            document.querySelectorAll('[data-tour-restart]').forEach((button) => {
                button.addEventListener('click', () => openTour(true));
            });

            window.addEventListener('resize', positionTour);
            document.querySelector('main')?.addEventListener('scroll', positionTour, { passive: true });
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape' && isOpen) {
                    closeTour(true);
                }
            });

            window.setTimeout(() => openTour(forceTourFromUrl), 600);
        }());
    </script>
</body>
</html>
