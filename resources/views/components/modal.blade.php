@props([
    'id',
    'title' => null,
    'description' => null,
    'maxWidth' => 'max-w-3xl',
])

<div
    id="{{ $id }}"
    data-modal
    class="fixed inset-0 z-[70] hidden"
    role="dialog"
    aria-modal="true"
    aria-labelledby="{{ $id }}-title"
>
    <div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" data-modal-close></div>
    <div class="relative flex min-h-full items-end justify-center p-4 sm:items-center sm:p-6">
        <div class="relative w-full {{ $maxWidth }} overflow-hidden rounded-[2rem] border border-outline bg-surface shadow-2xl">
            <div class="flex items-start justify-between gap-4 border-b border-outline px-5 py-4 sm:px-6">
                <div class="min-w-0">
                    @if ($title)
                        <h2 id="{{ $id }}-title" class="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">{{ $title }}</h2>
                    @endif
                    @if ($description)
                        <p class="mt-1 text-sm text-slate-500">{{ $description }}</p>
                    @endif
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
                {{ $slot }}
            </div>
        </div>
    </div>
</div>
