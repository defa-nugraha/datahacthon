<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ config('app.name', 'Vera AI') }}</title>

        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="min-h-screen bg-[#fafaf4] font-sans text-slate-900 antialiased">
        <main class="flex min-h-screen items-center justify-center px-4 py-10">
            <section class="w-full max-w-md">
                <div class="mb-8 text-center">
                    <a href="/" class="inline-flex flex-col items-center gap-4">
                        <x-application-logo class="h-20 w-20" />
                        <span>
                            <span class="block text-3xl font-extrabold tracking-tight text-[#154212]">Vera AI</span>
                            <span class="mt-1 block text-sm font-medium text-slate-500">AI vegetation advisor berbasis zona</span>
                        </span>
                    </a>
                </div>

                <div class="rounded-3xl border border-[#d8d9d2] bg-white p-6 shadow-[0_20px_60px_rgba(21,66,18,0.08)] sm:p-8">
                    {{ $slot }}
                </div>

                <p class="mt-6 text-center text-xs text-slate-500">
                    Gunakan akun demo dari seeder untuk masuk dan mencoba dashboard zona.
                </p>
            </section>
        </main>
    </body>
</html>
