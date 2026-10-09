# Deploying TeamSync AI

Three services and a database, behind one proxy that handles HTTPS:

```
                 ┌── teamsync.example.com ──→ frontend (Next.js, built)
browser ──→ Caddy┤
                 └── api.example.com ───────→ backend (FastAPI) ──→ ai-service  (private)
                                                     └──────────→ PostgreSQL   (private)
```

The AI service and the database are never published. The AI service has no accounts of its
own: anything that can reach it can run analyses, so it stays on the internal network.

---

## 1. What you need

- A machine with Docker and the Compose plugin. 2 GB of RAM is comfortable; 1 GB works if the
  frontend is hosted elsewhere (see §6).
- Two hostnames pointing at it — one for the app, one for the API. Subdomains of one domain are
  fine (`teamsync.example.com`, `api.example.com`). Both must resolve **before** you start, or
  Caddy cannot get certificates.
- Ports 80 and 443 open. Nothing else needs to be.

## 2. Settings

Copy the example and fill it in, on the server:

```bash
cp .env.example .env
```

| Setting | Where it comes from |
|---|---|
| `JWT_SECRET` | You generate it: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. It signs every login — treat it like a password |
| `DB_PASSWORD` | You choose it; the database is created with it on first start |
| `DOMAIN` | The app's hostname, e.g. `teamsync.example.com` |
| `API_DOMAIN` | The API's hostname, e.g. `api.example.com` |
| `ACME_EMAIL` | Your email; Let's Encrypt sends expiry warnings there |
| `GROQ_API_KEY` | Optional. Without it the agents use their deterministic path, which is how every published result was measured |
| `GITHUB_TOKEN` | Optional, read-only. Public repositories work without one |

You do **not** need to set `CORS_ORIGINS`, `DEBUG` or `TRUST_PROXY_HEADERS` — the production
overlay sets all three correctly from `DOMAIN`.

## 3. Start it

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

The first build takes a few minutes, most of it the frontend. Then check:

```bash
curl -sf https://api.example.com/health && echo " API up"
```

Open `https://teamsync.example.com` and sign up — **the first account owns the workspace**, so
do this yourself before sharing the link.

Optionally load the real Apache Mesos sprint the demo uses:

```bash
docker compose exec backend python -m app.scripts.import_real_sprint app/scripts/fixtures/mesos_sprint_74.json --at 0.5
```

## 4. What the production overlay changes

Against `docker-compose.yml`, which is written for local work:

| | Local | Deployed |
|---|---|---|
| Frontend | `next dev`, source mounted | built image, `next start`, public URLs compiled in |
| Reload | on | off; the images are what runs |
| PostgreSQL | port 5432 published | internal only |
| AI service | port 8001 published | internal only |
| `DEBUG` | true, so `/docs` is open | false, `/docs` closed |
| SQL logging | off | off |
| Proxy headers | not trusted | trusted (Caddy is in front) |
| TLS | none | Caddy, certificates fetched and renewed automatically |
| Restarts | manual | `unless-stopped` |

## 5. Updating

```bash
git pull
```

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Note the frontend's public URLs are compiled in at build time, so a changed `API_DOMAIN`
needs a rebuild, not just a restart.

## 6. Smaller or free hosting

**One small VM** (Oracle Always Free, Hetzner, DigitalOcean) runs the whole stack exactly as
above. This is the simplest option.

**1 GB of RAM** (a GCP e2-micro or Azure B1s) is too tight for all four containers. Split it:
put the frontend on Vercel (set `NEXT_PUBLIC_API_URL` to your API hostname in its project
settings) and PostgreSQL on a managed free tier such as Neon, then run only the backend and AI
service on the VM. With a managed database, set `DATABASE_URL` yourself and remember two things:
it must start `postgresql+asyncpg://`, and `?sslmode=require` has to become `?ssl=true`, which
is what asyncpg understands.

**With no credit card at all**, [`deploy/free-tier.md`](../deploy/free-tier.md) walks through Neon,
Render and Netlify step by step; [`render.yaml`](../render.yaml) creates both Python services from
one click, and [`frontend/netlify.toml`](../frontend/netlify.toml) builds the frontend.

**Platforms instead of a server** (Render, Railway, Fly): deploy `backend/` and `ai-service/`
as two services from their Dockerfiles, and override the start command so they listen on the
platform's port: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Keep the AI service's URL
private if the platform allows it; if it cannot, at least leave `GROQ_API_KEY` off that service
so nobody can spend your quota.

## 7. Backups

Everything that matters is in PostgreSQL:

```bash
docker compose exec -T postgres pg_dump -U teamsync teamsync | gzip > backup-$(date +%F).sql.gz
```

Worth a daily cron job. There are no database migrations yet: tables are created at startup, so
a fresh deployment is fine, but a schema change on an existing database is a manual `ALTER TABLE`
(`backend/app/database.py` lists the columns added since the first release).

## 8. GitHub webhooks

Once the API has a public hostname, each project can get instant updates: **Project settings →
Set up a webhook**, then paste the payload URL and secret into the repository's *Settings →
Webhooks*, selecting the **push** and **pull request** events. Calls without a signature made
with that secret are refused before the body is read.

## 9. What is hardened, and what is not

Done:

- Passwords hashed with bcrypt, on a worker thread so a sign-in cannot stall the server.
- **Ten failed sign-ins a minute per caller** (`AUTH_RATE_LIMIT_ATTEMPTS`), after which every
  attempt from that caller is refused for the rest of the minute — the correct password included,
  or guessing would just continue until it worked. Only failures count, so a team signing in one
  after another is never mistaken for an attack. Creating accounts is limited by every attempt.
  The tally is in memory per worker, so with `--workers 2` the real limit is twice that; an exact
  shared limit would need Redis.
- Every state-changing endpoint carries a role check — 185 of them are verified by a test — with
  one deliberate exception, the GitHub webhook, which is verified by signature instead.
- The database and AI service are unreachable from outside; TLS and security headers at the proxy.

Not done, and worth knowing before real users arrive:

- No audit log of who changed what, beyond the analysis history.
- No password reset, email verification, or two-factor authentication.
- No database migrations (§7).
- Load tested to 50 simultaneous users on one laptop and on a CI runner; nothing larger has been
  measured. See [VALIDATION_REPORT.md](../VALIDATION_REPORT.md).
