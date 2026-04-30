@props([
    'id' => null,
    'name' => null,
    'title' => null,
    'description' => null,
    'show' => false,
    'maxWidth' => '2xl',
])

@php
    $modalId = $id ?? $name;
    $maxWidthClass = [
        'sm' => 'sm:max-w-sm',
        'md' => 'sm:max-w-md',
        'lg' => 'sm:max-w-lg',
        'xl' => 'sm:max-w-xl',
        '2xl' => 'sm:max-w-2xl',
        'max-w-md' => 'sm:max-w-md',
        'max-w-2xl' => 'sm:max-w-2xl',
        'max-w-3xl' => 'sm:max-w-3xl',
        'max-w-4xl' => 'sm:max-w-4xl',
    ][$maxWidth ?? '2xl'] ?? 'sm:max-w-2xl';
@endphp

<div
    id="{{ $modalId }}"
    data-modal
    x-data="{
        open() {
            $el.classList.remove('hidden');
            document.body.classList.add('overflow-y-hidden');
            {{ $attributes->has('focusable') ? 'setTimeout(() => this.firstFocusable()?.focus(), 100);' : '' }}
        },
        close() {
            $el.classList.add('hidden');
            document.body.classList.remove('overflow-y-hidden');
        },
        focusables() {
            const selector = 'a, button, input:not([type=\'hidden\']), textarea, select, details, [tabindex]:not([tabindex=\'-1\'])';
            return [...$el.querySelectorAll(selector)].filter((element) => ! element.hasAttribute('disabled'));
        },
        firstFocusable() { return this.focusables()[0]; },
        lastFocusable() { return this.focusables().slice(-1)[0]; },
        nextFocusable() { return this.focusables()[(this.focusables().indexOf(document.activeElement) + 1) % this.focusables().length] || this.firstFocusable(); },
        previousFocusable() { return this.focusables()[Math.max(0, this.focusables().indexOf(document.activeElement) - 1)] || this.lastFocusable(); },
    }"
    x-on:open-modal.window="$event.detail === '{{ $modalId }}' ? open() : null"
    x-on:close-modal.window="$event.detail === '{{ $modalId }}' ? close() : null"
    x-on:close.window="close()"
    x-on:keydown.escape.window="close()"
    x-on:keydown.tab.prevent="$event.shiftKey ? previousFocusable()?.focus() : nextFocusable()?.focus()"
    class="{{ $show ? '' : 'hidden' }} fixed inset-0 z-50 overflow-y-auto px-4 py-6 sm:px-0"
>
    <div class="fixed inset-0 bg-slate-900/55 backdrop-blur-sm" x-on:click="close()"></div>

    <div class="relative mb-6 overflow-hidden rounded-3xl bg-white shadow-xl sm:mx-auto sm:w-full {{ $maxWidthClass }}">
        @if ($title || $description)
            <div class="border-b border-outline px-6 py-5">
                @if ($title)
                    <h2 class="text-xl font-bold tracking-tight text-slate-900">{{ $title }}</h2>
                @endif

                @if ($description)
                    <p class="mt-1 text-sm text-slate-500">{{ $description }}</p>
                @endif
            </div>
        @endif

        <div class="{{ $title || $description ? 'p-6' : '' }}">
            {{ $slot }}
        </div>
    </div>
</div>
