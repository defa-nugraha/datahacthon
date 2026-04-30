#!/usr/bin/env sh
set -eu

cd /var/www/html

git config --global --add safe.directory /var/www/html || true

if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
fi

mkdir -p \
    bootstrap/cache \
    database \
    storage/app \
    storage/framework/cache \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs

touch database/database.sqlite

# PHP-FPM workers run as www-data, while this entrypoint runs as root.
# In the bind-mounted dev workspace, permissive writes are the least brittle
# option so Blade compilation, sessions, cache, and SQLite work reliably.
chmod -R 0777 storage bootstrap/cache database || true
chmod 0666 database/database.sqlite || true

if [ "${SKIP_APP_BOOTSTRAP:-0}" = "1" ]; then
    exec "$@"
fi

if [ ! -f vendor/autoload.php ]; then
    attempt=1
    max_attempts=3
    install_succeeded=0

    while [ "$attempt" -le "$max_attempts" ]; do
        if composer install --no-interaction --prefer-dist; then
            install_succeeded=1
            break
        fi

        echo "composer install gagal pada percobaan ${attempt}; membersihkan cache sementara lalu mencoba lagi" >&2
        rm -rf vendor/* || true
        rm -rf vendor/composer/tmp-* || true
        composer clear-cache || true
        attempt=$((attempt + 1))
    done

    if [ "$install_succeeded" -ne 1 ]; then
        echo "composer install --prefer-dist gagal; fallback ke --prefer-source" >&2
        rm -rf vendor/* || true
        composer clear-cache || true
        composer install --no-interaction --prefer-source
    fi
fi

if [ -f package.json ] && [ ! -f public/build/manifest.json ]; then
    if [ ! -d node_modules ] || [ -z "$(ls -A node_modules 2>/dev/null)" ]; then
        npm install --ignore-scripts
    fi

    npm run build
fi

if [ -f artisan ] && [ -f .env ] && grep -q '^APP_KEY=$' .env; then
    php artisan key:generate --force --ansi || true
fi

exec "$@"
