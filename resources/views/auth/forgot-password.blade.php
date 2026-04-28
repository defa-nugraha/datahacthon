<x-guest-layout>
    <div class="mb-4 text-sm text-gray-600">
        {{ __('Lupa password? Santai bre. Kasih tau aja email lu, nanti gua kirimin link buat bikin password baru lewat email.') }}
    </div>

    <x-auth-session-status class="mb-4" :status="session('status')" />

    <form method="POST" action="{{ route('password.email') }}">
        @csrf

        <div>
            <x-input-label for="email" :value="__('Email')" />
            <x-text-input id="email" class="block mt-1 w-full" type="email" name="email" :value="old('email')" required autofocus />
            <x-input-error :messages="$errors->get('email')" class="mt-2" />
        </div>

        <div class="flex items-center justify-between mt-4">
            <a class="text-sm text-gray-600 hover:text-primary font-medium transition-colors" href="{{ route('login') }}">
                {{ __('Kembali ke Login') }}
            </a>

            <x-primary-button>
                {{ __('Kirim Link Reset') }}
            </x-primary-button>
        </div>
    </form>
</x-guest-layout>