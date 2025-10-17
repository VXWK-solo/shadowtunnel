FROM node:18-alpine AS webpanel-builder

WORKDIR /app
COPY roles/webpanel/package*.json ./
RUN npm ci --only=production

COPY roles/webpanel/ ./
RUN npm run build

FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    jq \
    openssl \
    ufw \
    fail2ban \
    htop \
    nano \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r vpn && useradd -r -g vpn vpn

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN chown -R vpn:vpn /app
USER vpn

EXPOSE 2053 3000 9090 443 8388

CMD ["python", "-m", "pytest", "tests/", "-v"]

FROM base AS production

RUN apt-get update && apt-get install -y \
    xray \
    v2ray \
    shadowsocks-libev \
    nginx \
    prometheus \
    grafana \
    && rm -rf /var/lib/apt/lists/*

COPY --from=webpanel-builder /app/dist /app/webpanel/dist

COPY . .

RUN mkdir -p /var/log/vpn /etc/vpn /opt/vpn \
    && chown -R vpn:vpn /var/log/vpn /etc/vpn /opt/vpn

COPY docker/entrypoint.sh /usr/local/bin/
COPY docker/healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh

RUN chown -R vpn:vpn /app
USER vpn

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

EXPOSE 2053 3000 9090 443 8388 80

CMD ["/usr/local/bin/entrypoint.sh"]

FROM base AS testing

RUN pip install --no-cache-dir pytest pytest-cov pytest-mock

COPY . .

RUN chown -R vpn:vpn /app
USER vpn

CMD ["python", "-m", "pytest", "tests/", "--cov=src/", "--cov-report=xml"]
