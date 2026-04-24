@extends('layouts.app')

@section('title', 'Field Zones - Vera AI')

@section('content')
    <div class="mx-auto max-w-7xl space-y-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Field Zones</p>
                <h1 class="mt-2 text-4xl font-extrabold tracking-tight text-slate-900">Kelola zona tanam aktif</h1>
                <p class="mt-2 max-w-3xl text-base text-slate-600">
                    Monitor status sampling, tanaman aktif, dan kesiapan setiap zona sebelum analisis AI dijalankan.
                </p>
            </div>
            <div class="flex flex-wrap gap-3">
                <a href="{{ route('dashboard') }}" class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                    Kembali ke Dashboard
                </a>
                <button
                    type="button"
                    data-modal-open="zone-create-modal"
                    class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success"
                >
                    Tambah Zona
                </button>
            </div>
        </div>

        @if (collect($zones)->isEmpty())
            <div class="rounded-3xl border border-dashed border-outline bg-surface px-8 py-16 text-center shadow-panel">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary-soft text-primary">
                    <span class="material-symbols-outlined text-3xl">potted_plant</span>
                </div>
                <h2 class="mt-5 text-2xl font-bold tracking-tight text-slate-900">Belum ada zona terdaftar</h2>
                <p class="mt-2 text-slate-500">Buat zona pertama untuk mulai mengumpulkan data sampling dan menjalankan rekomendasi AI.</p>
                <button
                    type="button"
                    data-modal-open="zone-create-modal"
                    class="mt-6 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success"
                >
                    Buat Zona Pertama
                </button>
            </div>
        @else
            <div class="grid gap-5 lg:grid-cols-2 2xl:grid-cols-3">
                @foreach ($zones as $zone)
                    @php
                        $statusClasses = match($zone['status']['tone']) {
                            'green' => 'bg-emerald-100 text-emerald-800',
                            'blue' => 'bg-sky-100 text-sky-800',
                            default => 'bg-amber-100 text-amber-800',
                        };
                        $editModalId = 'zone-edit-modal-'.$zone['id'];
                        $isEditModalActive = old('_open_modal') === $editModalId;
                    @endphp
                    <article class="overflow-hidden rounded-3xl border border-outline bg-surface shadow-panel">
                        <div class="p-6">
                            <div class="flex items-start justify-between gap-3">
                                <div class="min-w-0">
                                    <h2 class="text-3xl font-bold tracking-tight text-slate-900">{{ $zone['name'] }}</h2>
                                    <p class="mt-1 text-sm text-slate-500">{{ $zone['area_label'] }}</p>
                                    <p class="mt-2 line-clamp-2 text-sm text-slate-500">{{ $zone['location_description'] }}</p>
                                </div>
                                <div class="flex items-center gap-2">
                                    <button
                                        type="button"
                                        data-modal-open="{{ $editModalId }}"
                                        class="rounded-full p-2 text-slate-500 transition hover:bg-surface-soft hover:text-primary"
                                        aria-label="Edit zona {{ $zone['name'] }}"
                                    >
                                        <span class="material-symbols-outlined">edit</span>
                                    </button>
                                    <form
                                        action="{{ route('zones.destroy', $zone['id']) }}"
                                        method="POST"
                                        data-confirm-delete
                                        data-confirm-title="Hapus zona {{ $zone['name'] }}?"
                                        data-confirm-text="Seluruh sampling dan adaptive advice pada zona ini akan ikut terhapus."
                                        data-confirm-button="Ya, hapus zona"
                                    >
                                        @csrf
                                        @method('DELETE')
                                        <button
                                            type="submit"
                                            class="rounded-full p-2 text-slate-500 transition hover:bg-rose-50 hover:text-rose-700"
                                            aria-label="Hapus zona {{ $zone['name'] }}"
                                        >
                                            <span class="material-symbols-outlined">delete</span>
                                        </button>
                                    </form>
                                </div>
                            </div>

                            <div class="mt-4 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold {{ $statusClasses }}">
                                <span class="material-symbols-outlined text-sm">verified</span>
                                <span>{{ $zone['status']['label'] }}</span>
                            </div>

                            <div class="mt-5 grid grid-cols-2 gap-3">
                                <div class="rounded-2xl border border-outline bg-surface-soft px-4 py-4">
                                    <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Sampling Points</div>
                                    <div class="mt-3 flex items-center gap-2 text-lg font-bold text-slate-900">
                                        <span class="material-symbols-outlined text-primary">location_on</span>
                                        <span>{{ $zone['sample_count'] }} / {{ $zone['target_sample_count'] }} titik</span>
                                    </div>
                                </div>
                                <div class="rounded-2xl border border-outline bg-surface-soft px-4 py-4">
                                    <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ $zone['active_crop'] ? 'Current Crop' : 'Recommended Crop' }}</div>
                                    <div class="mt-3 flex items-center gap-2 text-lg font-bold text-primary">
                                        <span class="material-symbols-outlined">grass</span>
                                        <span>{{ $zone['active_crop'] ?: ($zone['latest_recommendation_label'] ?: 'Pending') }}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="mt-4 flex flex-wrap gap-2">
                                @if ($zone['has_complete_data'])
                                    <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">Data Lengkap</span>
                                @else
                                    <span class="rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700">Sample Sedikit</span>
                                @endif

                                @if ($zone['latest_recommendation_confidence'])
                                    <span class="rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-800">
                                        Confidence {{ number_format($zone['latest_recommendation_confidence'], 0) }}%
                                    </span>
                                @endif
                            </div>
                        </div>

                        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-outline bg-surface-soft px-6 py-4">
                            <a href="{{ route('zones.show', ['zone' => $zone['id'], 'modal' => 'sampling-create-modal']) }}" class="text-sm font-semibold text-danger hover:text-rose-700">
                                Tambah Sampling
                            </a>
                            <div class="flex flex-wrap gap-3">
                                <a href="{{ route('zones.monitor', $zone['id']) }}" class="rounded-2xl border border-outline px-4 py-2 text-sm font-semibold text-primary transition hover:border-primary hover:bg-primary-soft">
                                    Live
                                </a>
                                <a href="{{ route('zones.show', $zone['id']) }}" class="rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-success">
                                    View Detail
                                </a>
                            </div>
                        </div>
                    </article>

                    <x-modal
                        :id="$editModalId"
                        title="Edit zona"
                        :description="'Perbarui identitas dan target sampling untuk '.$zone['name'].'.'"
                        max-width="max-w-2xl"
                    >
                        <form action="{{ route('zones.update', $zone['id']) }}" method="POST" class="grid gap-4 sm:grid-cols-2">
                            @csrf
                            @method('PUT')
                            <input type="hidden" name="_open_modal" value="{{ $editModalId }}">

                            <div class="sm:col-span-2">
                                <label class="mb-2 block text-sm font-semibold text-slate-700">Nama zona</label>
                                <input
                                    type="text"
                                    name="name"
                                    value="{{ $isEditModalActive ? old('name') : $zone['name'] }}"
                                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                                    required
                                >
                            </div>

                            <div>
                                <label class="mb-2 block text-sm font-semibold text-slate-700">Blok / sektor</label>
                                <input
                                    type="text"
                                    name="area_label"
                                    value="{{ $isEditModalActive ? old('area_label') : $zone['area_label'] }}"
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
                                    value="{{ $isEditModalActive ? old('sample_target_count', $zone['target_sample_count']) : $zone['target_sample_count'] }}"
                                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                                >
                            </div>

                            <div class="sm:col-span-2">
                                <label class="mb-2 block text-sm font-semibold text-slate-700">Deskripsi lokasi</label>
                                <textarea
                                    name="location_description"
                                    rows="4"
                                    class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm"
                                >{{ $isEditModalActive ? old('location_description') : $zone['location_description'] }}</textarea>
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
                    </x-modal>
                @endforeach
            </div>
        @endif
    </div>

    <x-modal
        id="zone-create-modal"
        title="Register New Zone"
        description="Buat zona baru untuk mulai mengumpulkan titik sampling dan menjalankan analisis AI."
        max-width="max-w-2xl"
    >
        <form action="{{ route('zones.store') }}" method="POST" class="grid gap-4 sm:grid-cols-2">
            @csrf
            <input type="hidden" name="_open_modal" value="zone-create-modal">

            <div class="sm:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700">Nama zona</label>
                <input type="text" name="name" value="{{ old('name') }}" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm" required>
            </div>

            <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Blok / sektor</label>
                <input type="text" name="area_label" value="{{ old('area_label') }}" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
            </div>

            <div>
                <label class="mb-2 block text-sm font-semibold text-slate-700">Target titik</label>
                <input type="number" name="sample_target_count" min="3" max="24" value="{{ old('sample_target_count', 8) }}" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">
            </div>

            <div class="sm:col-span-2">
                <label class="mb-2 block text-sm font-semibold text-slate-700">Deskripsi lokasi</label>
                <textarea name="location_description" rows="4" class="w-full rounded-2xl border-outline bg-surface-soft px-4 py-3 text-sm">{{ old('location_description') }}</textarea>
            </div>

            <div class="flex flex-wrap justify-end gap-3 sm:col-span-2">
                <button type="button" data-modal-close class="rounded-2xl border border-outline px-5 py-3 text-sm font-semibold text-slate-600 transition hover:bg-surface-soft">
                    Batal
                </button>
                <button type="submit" class="rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-success">
                    Simpan Zona
                </button>
            </div>
        </form>
    </x-modal>
@endsection
