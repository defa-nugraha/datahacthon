<x-guest-layout>
    <div class="mb-6">
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Masuk Dashboard</p>
        <h1 class="mt-2 text-2xl font-extrabold tracking-tight text-slate-900">Pantau kondisi zona lahan</h1>
        <p class="mt-2 text-sm leading-6 text-slate-500">
            Kelola sampling tanah, rekomendasi vegetasi, dan saran penanganan tanaman dari satu layar.
        </p>
    </div>

    <x-auth-session-status class="mb-4" :status="session('status')" />

    <form method="POST" action="{{ route('login') }}" class="space-y-5">
        @csrf

        <div>
            <label for="email" class="mb-2 block text-sm font-semibold text-slate-700">Email</label>
            <input
                id="email"
                type="email"
                name="email"
                value="{{ old('email', 'petani@agrozonal.test') }}"
                required
                autofocus
                autocomplete="username"
                class="w-full rounded-2xl border border-[#d8d9d2] bg-[#f4f4ee] px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#154212] focus:bg-white focus:ring-4 focus:ring-[#e5f0e1]"
            >
            <x-input-error :messages="$errors->get('email')" class="mt-2" />
        </div>

        <div>
            <label for="password" class="mb-2 block text-sm font-semibold text-slate-700">Password</label>
            <input
                id="password"
                type="password"
                name="password"
                required
                autocomplete="current-password"
                placeholder="password"
                class="w-full rounded-2xl border border-[#d8d9d2] bg-[#f4f4ee] px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#154212] focus:bg-white focus:ring-4 focus:ring-[#e5f0e1]"
            >
            <x-input-error :messages="$errors->get('password')" class="mt-2" />
        </div>

        <div class="flex items-center justify-between gap-3">
            <label for="remember_me" class="inline-flex items-center gap-2 text-sm text-slate-600">
                <input id="remember_me" type="checkbox" class="rounded border-slate-300 text-[#154212] focus:ring-[#154212]" name="remember">
                <span>Ingat saya</span>
            </label>

            @if (Route::has('password.request'))
                <a class="text-sm font-semibold text-[#154212] transition hover:text-[#2d5a27]" href="{{ route('password.request') }}">
                    Lupa password?
                </a>
            @endif
        </div>

        <button type="submit" class="w-full rounded-2xl bg-[#154212] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-green-950/10 transition hover:bg-[#2d5a27] focus:outline-none focus:ring-4 focus:ring-[#e5f0e1]">
            Masuk
        </button>
    </form>

    <div class="mt-6 rounded-2xl border border-[#d8d9d2] bg-[#f4f4ee] px-4 py-3 text-sm text-slate-600">
        <div class="font-semibold text-slate-900">Akun demo</div>
        <div class="mt-1 font-mono text-xs">petani@agrozonal.test / password</div>
        <div class="mt-1 font-mono text-xs">admin@agrozonal.test / password</div>
    </div>
</x-guest-layout>
