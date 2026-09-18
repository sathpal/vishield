#!/bin/bash
# First-boot setup for the ViShield host (Amazon Linux 2023). Rendered by Terraform.
set -euxo pipefail

dnf update -y
dnf install -y docker
systemctl enable --now docker

# Docker Compose v2 plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

mkdir -p /opt/vishield/data
chown 1000:1000 /opt/vishield/data   # the container runs as uid 1000

cat > /opt/vishield/docker-compose.yml <<'COMPOSE'
${compose}
COMPOSE

cat > /opt/vishield/Caddyfile <<'CADDY'
${caddyfile}
CADDY

cat > /opt/vishield/.env <<ENV
ECR_IMAGE=${ecr_image}
IMAGE_TAG=latest
SITE_ADDRESS=${site_address}
AWS_REGION=${region}
LOG_GROUP=${log_group}
ENV

# deploy.sh <tag>: log in to ECR, pull that tag, restart the stack. Run by GitHub Actions through SSM,
# or by hand from a Session Manager shell.
cat > /opt/vishield/deploy.sh <<'DEPLOY'
#!/bin/bash
set -euo pipefail
cd /opt/vishield
TAG="$${1:-latest}"
sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=$TAG/" .env
REGION=$(grep '^AWS_REGION=' .env | cut -d= -f2)
REGISTRY=$(grep '^ECR_IMAGE=' .env | cut -d= -f2 | cut -d/ -f1)
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"
docker compose pull
docker compose up -d --remove-orphans
docker image prune -f
docker compose ps
DEPLOY
chmod +x /opt/vishield/deploy.sh

# First boot: the image may not have been pushed yet. Try, but do not fail the boot.
/opt/vishield/deploy.sh latest || echo "No image in ECR yet. Run the deploy workflow or 'make cloud-push cloud-deploy'."
