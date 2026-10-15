FROM php:7.4-cli-bullseye
RUN echo "deb http://archive.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list \
    && echo "deb http://archive.debian.org/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list \
    && echo "Acquire::Check-Valid-Until \"false\";" > /etc/apt/apt.conf.d/99no-check-valid-until \
    && apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && docker-php-ext-install pgsql \
    && pecl install xdebug-3.1.6 \
    && docker-php-ext-enable xdebug \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PHP_CLI_SERVER_WORKERS=4
ENV PHP_IDE_CONFIG="serverName=airnet-assessment"

# Команда запуска с жестко встроенными параметрами конфигурации Xdebug 3.1.6
CMD php \
    -d display_errors=0 \
    -d xdebug.mode=debug \
    -d xdebug.start_with_request=yes \
    -d xdebug.client_host=host.docker.internal \
    -d xdebug.client_port=9003 \
    -d xdebug.log=/app/xdebug.log \
    -S 0.0.0.0:8080 \
    -t public \
    public/router.php