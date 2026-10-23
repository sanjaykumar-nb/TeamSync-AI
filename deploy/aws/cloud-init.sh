#!/bin/bash
# Runs once, on first boot of the instance. Installs Docker, fetches the code,
# writes the settings, and starts the production stack.
#
# Placeholders (__NAME__) are filled in by deploy/aws/launch.sh before launch.
set -euxo pipefail
exec > >(tee /var/log/teamsync-setup.log) 2>&1

REPO_URL="__REPO_URL__"
API_DOMAIN="__API_DOMAIN__"
APP_DOMAIN="__APP_DOMAIN__"
ACME_EMAIL="__ACME_EMAIL__"
JWT_SECRET="__JWT_SECRET__"
DB_PASSWORD="__DB_PASSWORD__"

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl git

# Docker, from Docker's own repository (Ubuntu's package is older).
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker ubuntu

# 2 GB of RAM runs the stack comfortably but `next build` wants more than that
# for a few minutes, so give it swap to lean on rather than a bigger instance.
if [ ! -f /swapfile ]; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

git clone --depth 1 "$REPO_URL" /opt/teamsync
cd /opt/teamsync

cat > .env <<ENV
JWT_SECRET=$JWT_SECRET
DB_PASSWORD=$DB_PASSWORD
DOMAIN=$APP_DOMAIN
API_DOMAIN=$API_DOMAIN
ACME_EMAIL=$ACME_EMAIL
GROQ_API_KEY=
GITHUB_TOKEN=
ENV
chmod 600 .env
chown -R ubuntu:ubuntu /opt/teamsync

# Everything on one box: Caddy serves the app on DOMAIN and the API on API_DOMAIN,
# so CORS_ORIGINS (derived from DOMAIN) is correct by construction, and both names
# resolve to this instance, which is what the ACME challenge needs.
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

cat > /etc/motd <<MOTD

  TeamSync AI
    app   https://$APP_DOMAIN
    API   https://$API_DOMAIN/health
    code  /opt/teamsync      setup log: /var/log/teamsync-setup.log

MOTD
echo "ready: https://$APP_DOMAIN"
