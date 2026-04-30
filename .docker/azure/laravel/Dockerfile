ARG COMPOSER_VERSION=2.8
ARG PHP_VERSION=8.4

FROM composer:${COMPOSER_VERSION} AS composer_bin

FROM php:${PHP_VERSION}-fpm-bookworm AS app

ARG NODE_MAJOR=22

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        nginx \
        sqlite3 \
        supervisor \
        unzip \
        zip \
        libicu-dev \
        libonig-dev \
        libsqlite3-dev \
        libxml2-dev \
        libzip-dev \
    && docker-php-ext-install -j"$(nproc)" \
        bcmath \
        intl \
        pdo_mysql \
        pdo_sqlite \
        zip \
    && curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer_bin /usr/bin/composer /usr/local/bin/composer

WORKDIR /var/www/html

COPY composer.json composer.lock ./
RUN composer install \
    --no-dev \
    --no-interaction \
    --prefer-dist \
    --optimize-autoloader \
    --no-scripts

COPY package.json ./
RUN npm install --ignore-scripts

COPY . .

RUN npm run build \
    && composer dump-autoload --optimize \
    && mkdir -p \
        /var/lib/nginx/body \
        /var/log/supervisor \
        bootstrap/cache \
        database \
        storage/app \
        storage/framework/cache \
        storage/framework/sessions \
        storage/framework/views \
        storage/logs \
    && touch database/database.sqlite \
    && chown -R www-data:www-data /var/www/html /var/lib/nginx /var/log/nginx /var/log/supervisor \
    && chmod -R ug+rwX storage bootstrap/cache database

COPY .docker/azure/laravel/nginx.conf /etc/nginx/nginx.conf
COPY .docker/azure/laravel/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY .docker/azure/laravel/entrypoint.sh /usr/local/bin/azure-laravel-entrypoint
RUN chmod +x /usr/local/bin/azure-laravel-entrypoint

EXPOSE 8080

ENTRYPOINT ["azure-laravel-entrypoint"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
