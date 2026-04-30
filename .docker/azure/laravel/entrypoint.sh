#!/usr/bin/env sh
set -eu

cd /var/www/html

mkdir -p \
    bootstrap/cache \
    database \
    storage/app \
    storage/framework/cache \
    storage/framework/sessions \
    storage/framework/views \
    storage/logs

touch "${DB_DATABASE:-/var/www/html/database/database.sqlite}"
chown -R www-data:www-data storage bootstrap/cache database || true
chmod -R ug+rwX storage bootstrap/cache database || true
chmod 0666 "${DB_DATABASE:-/var/www/html/database/database.sqlite}" || true

if [ -n "${APP_KEY:-}" ]; then
    php artisan config:clear --ansi || true
else
    echo "APP_KEY belum diset. Membuat key sementara untuk runtime demo Azure." >&2
    export APP_KEY="$(php -r 'echo "base64:".base64_encode(random_bytes(32));')"
    php artisan config:clear --ansi || true
fi

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    php artisan migrate --force --ansi
fi

if [ "${RUN_SEEDERS:-true}" = "true" ]; then
    php artisan db:seed --force --ansi
fi

if [ "${APP_ENV:-production}" = "production" ]; then
    php artisan config:cache --ansi || true
    php artisan route:cache --ansi || true
    php artisan view:cache --ansi || true
fi

exec "$@"
