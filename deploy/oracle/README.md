# Running TeamSync on Oracle Cloud's Always Free tier

One virtual machine runs everything — PostgreSQL, the backend, the AI service, the frontend and
Caddy for HTTPS — and stays free with no expiry date. The Always Free Ampere shape gives 2 CPUs
and 12 GB of RAM (halved from 4/24 in June 2026, and still far more than this needs).

You create the machine; everything on it is automatic.

---

## 1. Create the account

Go to **cloud.oracle.com/free** and sign up.

- A card is asked for **identity verification only**; Always Free resources are not charged. You
  may see a small temporary authorisation that is released.
- **Choose your home region carefully — it cannot be changed.** Pick one near you (for India,
  Mumbai or Hyderabad). If Ampere capacity is unavailable there later, see §5.
- When the account is ready, **do not upgrade to Pay As You Go**. On the free account, anything
  beyond the free limits simply fails to start instead of billing you.

## 2. Create the machine

Console → **Compute → Instances → Create instance**.

| Field | Choose |
|---|---|
| Name | `teamsync` |
| Image | **Canonical Ubuntu 24.04** |
| Shape | **Ampere → VM.Standard.A1.Flex**, **2 OCPUs**, **12 GB** memory |
| Networking | leave the new VCN, and keep **assign a public IPv4 address** |
| SSH keys | paste your public key, or let Oracle generate one and **download the private key** |
| Boot volume | 50 GB is plenty (200 GB total is free) |

Then open **Advanced options → Management → cloud-init script**, paste the contents of
[`cloud-init.sh`](cloud-init.sh), and change `ACME_EMAIL` to your address first.

Click **Create**. Note the **public IP address** shown when it starts.

## 3. Open ports 80 and 443

The instance has two firewalls, and both must allow traffic. The cloud-init script handles the
one inside Ubuntu; this is the other:

Console → **Networking → Virtual cloud networks →** your VCN **→ Security Lists → Default
Security List → Add Ingress Rules**, and add two rules:

| Source CIDR | IP protocol | Destination port |
|---|---|---|
| `0.0.0.0/0` | TCP | `80` |
| `0.0.0.0/0` | TCP | `443` |

## 4. Wait, then open it

First boot installs Docker and builds the images: around five to ten minutes on this shape. With
an IP of `1.2.3.4`, your addresses are:

- app — `https://app.1-2-3-4.nip.io`
- API — `https://api.1-2-3-4.nip.io/health`

`nip.io` turns any name containing an IP back into that IP, so Caddy can get real certificates
without you buying a domain. If a certificate fails to issue — `nip.io` is shared by everyone, so
Let's Encrypt occasionally rate-limits it — take a free subdomain from duckdns.org, point it at
your IP, and put it in `/opt/teamsync/.env` as `DOMAIN` and `API_DOMAIN`, then re-run the compose
command in §7. To watch progress:

```bash
ssh -i <your-key> ubuntu@<ip> 'sudo tail -f /var/log/teamsync-setup.log'
```

Sign up in the app — **the first account owns the workspace**, so do that before sharing the link.

To load the real Apache Mesos sprint the demo uses:

```bash
ssh -i <your-key> ubuntu@<ip> 'cd /opt/teamsync && docker compose exec -T backend python -m app.scripts.import_real_sprint app/scripts/fixtures/mesos_sprint_74.json --at 0.5'
```

## 5. If Ampere capacity is unavailable

"Out of host capacity" is common for the free ARM shape in busy regions. Options, in order:

1. Try again at a different time of day — capacity is released constantly.
2. Use **two AMD micro instances** instead (`VM.Standard.E2.1.Micro`, also Always Free) — but
   each has only 1 GB of RAM, so put PostgreSQL and the backend on one, the AI service on the
   other, and the frontend on Netlify or Vercel.
3. Create the instance in another region (a second, non-home region is allowed on free accounts
   in some cases) or fall back to the AWS instructions in [`../aws/`](../aws).

## 6. Keeping it free

- Never upgrade to Pay As You Go unless you intend to spend money.
- One Ampere instance with 2 CPUs and 12 GB uses the whole free ARM allowance — a second one
  would exceed it and fail.
- Oracle reclaims **idle** Always Free compute instances. A server answering requests is not
  idle; one left untouched for weeks may be. Keep the demo warm, or expect to restart it.
- Set a budget alert at $1 (Console → Billing → Budgets) so any surprise reaches you early.

## 7. Updating it later

```bash
ssh -i <your-key> ubuntu@<ip>
cd /opt/teamsync && git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Backups, GitHub webhooks and what is hardened are in [`../../docs/DEPLOY.md`](../../docs/DEPLOY.md).
