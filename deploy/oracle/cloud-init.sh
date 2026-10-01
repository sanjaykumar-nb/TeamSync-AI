#!/bin/bash
# Paste this into "Advanced options → cloud-init script" when creating the instance.
# It installs Docker, fetches the code, and starts the whole stack with HTTPS.
#
# Written for Oracle's Always Free Ampere (ARM) shape running Ubuntu 24.04. Every
# image the stack uses is published for ARM, so nothing needs changing.
#
# Two things here are specific to Oracle: their Ubuntu images block all inbound
# traffic except SSH with local iptables rules, on top of the cloud firewall, so
# ports 80 and 443 have to be opened in both places; and the instance has plenty
# of memory but no swap.
set -euxo pipefail
exec > >(tee /var/log/teamsync-setup.log) 2>&1

REPO_URL="https://github.com/sanjaykumar-nb/TeamSync-AI.git"
ACME_EMAIL="admin@example.com"   # put your address here: Let's Encrypt emails expiry warnings

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl git jq iptables-persistent

# --- 1. let HTTP and HTTPS in (the cloud firewall is separate; see README)
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
netfilter-persistent save

# --- 2. Docker from its own repository
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

# --- 3. hostnames from the instance's own address, so TLS works with no domain
#        nip.io resolves any name containing an IP back to that IP.
IP=$(curl -fsS --max-time 10 https://api.ipify.org || curl -fsS ifconfig.me)
DASHED="${IP//./-}"
APP_DOMAIN="app.$DASHED.nip.io"
API_DOMAIN="api.$DASHED.nip.io"

# --- 4. the code and its settings
git clone --depth 1 "$REPO_URL" /opt/teamsync
cd /opt/teamsync
secret() { python3 -c "import secrets; print(secrets.token_urlsafe(36))"; }
cat > .env <<ENV
JWT_SECRET=$(secret)
DB_PASSWORD=$(secret)
DOMAIN=$APP_DOMAIN
API_DOMAIN=$API_DOMAIN
ACME_EMAIL=$ACME_EMAIL
GROQ_API_KEY=
GITHUB_TOKEN=
ENV
chmod 600 .env
chown -R ubuntu:ubuntu /opt/teamsync

# --- 5. build and run everything (frontend included: 12 GB has room for it)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

cat > /etc/motd <<MOTD

  TeamSync AI
    app   https://$APP_DOMAIN
    API   https://$API_DOMAIN/health
    code  /opt/teamsync      logs: docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
    setup /var/log/teamsync-setup.log

MOTD
echo "ready: https://$APP_DOMAIN"
