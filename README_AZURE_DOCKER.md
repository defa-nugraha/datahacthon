# Azure Docker Deployment

Setup ini menjalankan dua container:

- `laravel`: Laravel + Nginx + PHP-FPM dalam satu image production.
- `fastapi`: service AI FastAPI untuk rekomendasi zona dan care advice.

Database tetap memakai SQLite di path:

```text
/var/www/html/database/database.sqlite
```

Pada Azure, mount path `/var/www/html/database` ke persistent storage agar data SQLite tidak hilang saat restart/redeploy.

## Build dan run lokal

```bash
cp .env.azure.example .env.azure
docker compose --env-file .env.azure -f docker-compose.azure.yml up --build -d
```

Akses:

```text
Laravel: http://127.0.0.1:8080
FastAPI: http://127.0.0.1:8001/docs
```

Saat container Laravel start, entrypoint otomatis menjalankan:

```bash
php artisan migrate --force
php artisan db:seed --force
```

Seeder demo tetap bisa berjalan di `APP_ENV=production` karena `.env.azure.example` menyetel:

```env
ALLOW_DEMO_SEEDING_IN_PRODUCTION=true
RUN_MIGRATIONS=true
RUN_SEEDERS=true
```

Jika aplikasi sudah berisi data real, ubah:

```env
RUN_SEEDERS=false
ALLOW_DEMO_SEEDING_IN_PRODUCTION=false
```

## Azure Container Registry

Contoh build dan push ke ACR:

```bash
az acr login --name <acr-name>

docker compose --env-file .env.azure -f docker-compose.azure.yml build

docker tag verai-laravel:azure <acr-name>.azurecr.io/verai-laravel:latest
docker tag verai-fastapi:azure <acr-name>.azurecr.io/verai-fastapi:latest

docker push <acr-name>.azurecr.io/verai-laravel:latest
docker push <acr-name>.azurecr.io/verai-fastapi:latest
```

Lalu set image di environment:

```env
AZURE_LARAVEL_IMAGE=<acr-name>.azurecr.io/verai-laravel:latest
AZURE_FASTAPI_IMAGE=<acr-name>.azurecr.io/verai-fastapi:latest
```

## Environment penting

Laravel:

```env
APP_KEY=base64:...
APP_URL=https://your-app.azurewebsites.net
DB_CONNECTION=sqlite
DB_DATABASE=/var/www/html/database/database.sqlite
AI_ADVISOR_BASE_URL=http://fastapi:8001
```

FastAPI Azure OpenAI:

```env
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_KEY=your-key
```

Untuk demo tanpa Azure OpenAI, biarkan:

```env
AZURE_OPENAI_ENABLED=false
```

FastAPI akan memakai fallback rule-based untuk care advice.

## Catatan SQLite di Azure

SQLite tidak membutuhkan layanan database Azure terpisah, tetapi file database harus persistent. Jika container disk tidak persistent, data hasil seed, sampling, dan advice bisa hilang saat redeploy.

Untuk production multi-instance, gunakan Azure Database for MySQL/PostgreSQL. Untuk demo single-instance/hackathon, SQLite + persistent volume cukup.
