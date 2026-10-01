#!/usr/bin/env bash
# Put the API side of TeamSync on one EC2 instance, with HTTPS.
#
#   aws login                 # you sign in; this script never handles credentials
#   bash deploy/aws/launch.sh
#
# What it makes, all inside your account: an Elastic IP (so the hostname is stable),
# a key pair saved to ~/.ssh, a security group open on 22, 80 and 443, and one
# t3.micro instance that installs Docker and starts the stack on first boot.
#
# Hostnames come from nip.io, which resolves any name containing an IP back to that
# IP — so TLS works with no domain to buy. Set DOMAIN_BASE to use your own instead.
set -euo pipefail

REGION="${REGION:-us-east-1}"
NAME="${NAME:-teamsync}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"
REPO_URL="${REPO_URL:-https://github.com/sanjaykumar-nb/TeamSync-AI.git}"
ACME_EMAIL="${ACME_EMAIL:-admin@example.com}"
KEY_PATH="${KEY_PATH:-$HOME/.ssh/$NAME-aws.pem}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

say() { printf '\n== %s\n' "$1"; }

say "Account and region"
aws sts get-caller-identity --output table --region "$REGION"

say "An address that will not change"
allocation=$(aws ec2 describe-addresses --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAME" --query 'Addresses[0].AllocationId' --output text)
if [ "$allocation" = "None" ] || [ -z "$allocation" ]; then
  allocation=$(aws ec2 allocate-address --region "$REGION" --domain vpc \
    --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$NAME}]" \
    --query AllocationId --output text)
fi
ip=$(aws ec2 describe-addresses --region "$REGION" --allocation-ids "$allocation" \
  --query 'Addresses[0].PublicIp' --output text)
dashed="${ip//./-}"
APP_DOMAIN="${DOMAIN_BASE:+app.$DOMAIN_BASE}"
API_DOMAIN="${DOMAIN_BASE:+api.$DOMAIN_BASE}"
APP_DOMAIN="${APP_DOMAIN:-app.$dashed.nip.io}"
API_DOMAIN="${API_DOMAIN:-api.$dashed.nip.io}"
echo "address $ip  ->  API https://$API_DOMAIN"

say "Key pair (so you can log in later)"
if ! aws ec2 describe-key-pairs --region "$REGION" --key-names "$NAME" >/dev/null 2>&1; then
  mkdir -p "$(dirname "$KEY_PATH")"
  aws ec2 create-key-pair --region "$REGION" --key-name "$NAME" \
    --query KeyMaterial --output text > "$KEY_PATH"
  chmod 600 "$KEY_PATH"
  echo "saved $KEY_PATH"
else
  echo "key pair $NAME already exists (keep using $KEY_PATH)"
fi

say "Firewall: SSH, HTTP, HTTPS, nothing else"
group=$(aws ec2 describe-security-groups --region "$REGION" \
  --filters "Name=group-name,Values=$NAME" --query 'SecurityGroups[0].GroupId' --output text)
if [ "$group" = "None" ] || [ -z "$group" ]; then
  group=$(aws ec2 create-security-group --region "$REGION" --group-name "$NAME" \
    --description "TeamSync API host" --query GroupId --output text)
  for port in 22 80 443; do
    aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$group" \
      --protocol tcp --port "$port" --cidr 0.0.0.0/0 >/dev/null
  done
fi
echo "security group $group"

say "First-boot script"
secret() { python -c "import secrets; print(secrets.token_urlsafe(36))"; }
user_data=$(mktemp)
sed -e "s|__REPO_URL__|$REPO_URL|" \
    -e "s|__API_DOMAIN__|$API_DOMAIN|" \
    -e "s|__APP_DOMAIN__|$APP_DOMAIN|" \
    -e "s|__ACME_EMAIL__|$ACME_EMAIL|" \
    -e "s|__JWT_SECRET__|$(secret)|" \
    -e "s|__DB_PASSWORD__|$(secret)|" \
    "$here/cloud-init.sh" > "$user_data"

say "Launching $INSTANCE_TYPE (Ubuntu 24.04)"
ami=$(aws ssm get-parameter --region "$REGION" \
  --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query Parameter.Value --output text)
instance=$(aws ec2 run-instances --region "$REGION" --image-id "$ami" \
  --instance-type "$INSTANCE_TYPE" --key-name "$NAME" --security-group-ids "$group" \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3}' \
  --metadata-options 'HttpTokens=required' \
  --user-data "file://$user_data" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME}]" \
  --query 'Instances[0].InstanceId' --output text)
rm -f "$user_data"
echo "instance $instance"

aws ec2 wait instance-running --region "$REGION" --instance-ids "$instance"
aws ec2 associate-address --region "$REGION" --instance-id "$instance" \
  --allocation-id "$allocation" >/dev/null

cat <<DONE

Launched. The first boot installs Docker and builds the images, which takes
about five minutes. Then:

  API      https://$API_DOMAIN/health
  Log in   ssh -i $KEY_PATH ubuntu@$ip
  Progress sudo tail -f /var/log/teamsync-setup.log

Next, point the frontend at it (Netlify):

  cd frontend
  NEXT_PUBLIC_API_URL=https://$API_DOMAIN netlify deploy --build --prod

Then set CORS_ORIGINS on the instance to the Netlify address and restart the
backend, so the browser is allowed to call the API:

  ssh -i $KEY_PATH ubuntu@$ip
  cd /opt/teamsync && sed -i "s|^DOMAIN=.*|DOMAIN=<your-netlify-host>|" .env
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend

To take it all down again: bash deploy/aws/destroy.sh
DONE
