<x-app-layout>
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between" data-tour="admin-overview">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Admin Console</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Kontrol operasional Vera AI</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">
                    Kelola user, device, dan kesiapan data zona agar workflow rekomendasi petani tetap stabil.
                </p>
            </div>
            <a href="{{ route('devices.index') }}" class="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-success">
                <span class="material-symbols-outlined text-[20px]">router</span>
                Kelola Device
            </a>
        </div>

        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4" data-tour="admin-metrics">
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
                    <span class="material-symbols-outlined">group</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight">{{ $stats['total_users'] }}</div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Total User</div>
                <div class="mt-3 text-sm text-slate-500">{{ $stats['farmers'] }} petani, {{ $stats['admins'] }} admin</div>
            </div>
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-soft text-slate-600">
                    <span class="material-symbols-outlined">potted_plant</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight">{{ $stats['total_zones'] }}</div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Total Zona</div>
                <div class="mt-3 text-sm text-slate-500">{{ $stats['active_zones'] }} zona sedang ditanam</div>
            </div>
            <div class="rounded-3xl border border-outline bg-surface p-6 shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-accent">
                    <span class="material-symbols-outlined">science</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight">{{ $stats['samples_24h'] }}</div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Sampling / 24 Jam</div>
                <div class="mt-3 text-sm text-slate-500">Aktivitas data terbaru</div>
            </div>
            <div class="rounded-3xl border border-primary/10 bg-primary p-6 text-white shadow-panel">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                    <span class="material-symbols-outlined">router</span>
                </div>
                <div class="text-4xl font-extrabold tracking-tight">{{ $stats['online_devices'] }} / {{ $stats['devices'] }}</div>
                <div class="mt-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-100">Device Online</div>
                <div class="mt-3 text-sm text-emerald-50">Kesiapan integrasi sensor</div>
            </div>
        </div>

        <div class="grid gap-6 xl:grid-cols-[1.25fr,0.75fr]">
            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel" data-tour="user-management">
                <div class="mb-5 flex items-center justify-between gap-3">
                    <div>
                        <h2 class="text-2xl font-bold tracking-tight text-slate-900">Manajemen User</h2>
                        <p class="text-sm text-slate-500">Admin dapat mengubah role user sesuai kebutuhan operasional.</p>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full min-w-[680px] text-left">
                        <thead>
                            <tr class="border-b border-outline text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                                <th class="py-3 pr-4">Nama</th>
                                <th class="py-3 pr-4">Email</th>
                                <th class="py-3 pr-4">Role</th>
                                <th class="py-3 text-right">Aksi</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-outline">
                            @foreach ($users as $user)
                                <tr>
                                    <td class="py-4 pr-4 font-semibold text-slate-800">{{ $user->name }}</td>
                                    <td class="py-4 pr-4 text-sm text-slate-500">{{ $user->email }}</td>
                                    <td class="py-4 pr-4">
                                        <span class="rounded-full px-3 py-1 text-xs font-semibold {{ $user->role === 'admin' ? 'bg-primary-soft text-primary' : 'bg-slate-100 text-slate-600' }}">
                                            {{ $user->role === 'admin' ? 'Admin' : 'Petani' }}
                                        </span>
                                    </td>
                                    <td class="py-4 text-right">
                                        <form action="{{ route('admin.users.role.update', $user) }}" method="POST" class="inline-flex items-center gap-2">
                                            @csrf
                                            @method('PATCH')
                                            <select name="role" class="rounded-xl border-outline bg-surface-soft text-sm focus:ring-primary">
                                                <option value="farmer" @selected($user->role === 'farmer')>Petani</option>
                                                <option value="admin" @selected($user->role === 'admin')>Admin</option>
                                            </select>
                                            <button type="submit" class="rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-white hover:bg-success">
                                                Simpan
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            </section>

            <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel" data-tour="device-summary">
                <div class="mb-5">
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Device Terbaru</h2>
                    <p class="text-sm text-slate-500">Ringkasan koneksi sensor/gateway.</p>
                </div>
                <div class="space-y-3">
                    @forelse ($devices as $device)
                        <div class="rounded-2xl border border-outline bg-surface-soft p-4">
                            <div class="flex items-start justify-between gap-3">
                                <div>
                                    <div class="font-bold text-slate-800">{{ $device->name }}</div>
                                    <div class="mt-1 font-mono text-xs text-slate-500">{{ $device->client_id }}</div>
                                </div>
                                <span class="rounded-full px-3 py-1 text-xs font-semibold {{ $device->status === 'online' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500' }}">
                                    {{ ucfirst($device->status) }}
                                </span>
                            </div>
                        </div>
                    @empty
                        <div class="rounded-2xl border border-dashed border-outline bg-surface-soft p-6 text-center text-sm text-slate-500">
                            Belum ada device terdaftar.
                        </div>
                    @endforelse
                </div>
            </section>
        </div>

        <section class="rounded-3xl border border-outline bg-surface p-6 shadow-panel" data-tour="zone-readiness">
            <div class="mb-5 flex items-center justify-between gap-3">
                <div>
                    <h2 class="text-2xl font-bold tracking-tight text-slate-900">Kesiapan Zona</h2>
                    <p class="text-sm text-slate-500">Admin memantau apakah zona punya sampling cukup untuk dianalisis.</p>
                </div>
                <a href="{{ route('zones.index') }}" class="text-sm font-semibold text-primary hover:text-success">Lihat semua zona</a>
            </div>
            <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                @forelse ($zones as $zone)
                    <article class="rounded-2xl border border-outline bg-surface-soft p-4">
                        <div class="font-bold text-slate-900">{{ $zone->name }}</div>
                        <div class="mt-1 text-sm text-slate-500">{{ $zone->area_label }}</div>
                        <div class="mt-4 flex items-center justify-between gap-3 text-sm">
                            <span class="text-slate-500">Sampling</span>
                            <span class="font-semibold text-slate-900">{{ $zone->soil_data_count }} / {{ $zone->sample_target_count }}</span>
                        </div>
                        <div class="mt-2 flex items-center justify-between gap-3 text-sm">
                            <span class="text-slate-500">Tanaman</span>
                            <span class="font-semibold text-primary">{{ $zone->active_crop ?: 'Belum aktif' }}</span>
                        </div>
                    </article>
                @empty
                    <div class="rounded-2xl border border-dashed border-outline bg-surface-soft p-6 text-center text-sm text-slate-500 md:col-span-2 xl:col-span-4">
                        Belum ada zona.
                    </div>
                @endforelse
            </div>
        </section>
    </div>
</x-app-layout>
