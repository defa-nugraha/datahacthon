<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework.

In addition, [Laracasts](https://laracasts.com) contains thousands of video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

You can also watch bite-sized lessons with real-world projects on [Laravel Learn](https://laravel.com/learn), where you will be guided through building a Laravel application from scratch while learning PHP fundamentals.

## Agentic Development

Laravel's predictable structure and conventions make it ideal for AI coding agents like Claude Code, Cursor, and GitHub Copilot. Install [Laravel Boost](https://laravel.com/docs/ai) to supercharge your AI workflow:

```bash
composer require laravel/boost --dev

php artisan boost:install
```

Boost provides your agent 15+ tools and skills that help agents build Laravel applications while following best practices.

## Docker Development

Branch `interface` ini sekarang punya setup Docker dev yang konsisten untuk runtime utama:

- PHP `8.4`
- Composer `2.8`
- Node.js `22`
- Nginx `1.27-alpine`
- SQLite default dikontrol oleh `.env.docker`

Langkah awal:

```bash
cp .env.example .env
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker exec app php artisan migrate
```

Alamat service:

- App: `http://localhost:8080`
- Vite dev server: `http://localhost:5173`

Perintah yang sering dipakai:

```bash
docker compose --env-file .env.docker exec app php artisan test
docker compose --env-file .env.docker exec app composer install
docker compose --env-file .env.docker exec app php artisan migrate
docker compose --env-file .env.docker exec vite npm run build
```

Kalau queue worker juga ingin dijalankan:

```bash
docker compose --env-file .env.docker --profile workers up -d
```

## Zone-Based UI + AI Service

Interface sekarang sudah mengikuti alur zona:

- `Dashboard` menampilkan overview zona, telemetri, dan aktivitas terbaru.
- `Field Zones` menampilkan daftar zona dan status sampling.
- `Detail Zona` menampilkan agregasi zona, titik sampling, radar profile, dan advice terbaru.
- `Monitoring` menampilkan histori 1 jam terakhir dan adaptive advice.

Service AI Python ada di folder [`python_service/`](python_service/README.md).

Endpoint utama:

- `POST /predict/zone`
- `POST /advice/care`
- `GET /health`

Laravel memanggil service ini melalui:

```bash
AI_ADVISOR_BASE_URL=http://127.0.0.1:8001
```

Dalam Docker Compose, default-nya sudah diarahkan ke:

```bash
AI_ADVISOR_BASE_URL=http://ai:8001
```

Untuk menjalankan seluruh stack termasuk AI service:

```bash
docker compose --env-file .env.docker up --build -d app web ai
docker compose --env-file .env.docker exec app php artisan migrate
docker compose --env-file .env.docker exec app php artisan db:seed --force
```

Untuk mengaktifkan adaptive advice setiap 1 jam, jalankan scheduler:

```bash
docker compose --env-file .env.docker --profile workers up -d scheduler
```

Atau lokal:

```bash
php artisan schedule:work
```

## Contributing

Thank you for considering contributing to the Laravel framework! The contribution guide can be found in the [Laravel documentation](https://laravel.com/docs/contributions).

## Code of Conduct

In order to ensure that the Laravel community is welcoming to all, please review and abide by the [Code of Conduct](https://laravel.com/docs/contributions#code-of-conduct).

## Security Vulnerabilities

If you discover a security vulnerability within Laravel, please send an e-mail to Taylor Otwell via [taylor@laravel.com](mailto:taylor@laravel.com). All security vulnerabilities will be promptly addressed.

## License

The Laravel framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).
