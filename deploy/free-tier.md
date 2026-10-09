# Hosting it free, with no credit card

Three services, three free accounts, none of which asks for a card:

| Part | Where | Free plan |
|---|---|---|
| PostgreSQL | **Neon** | 0.5 GB storage, 100 compute-hours a month, no expiry |
| Backend + AI service | **Render** | 512 MB each, 750 instance-hours a month; sleeps after 15 minutes idle |
| Frontend | **Netlify** | 100 GB bandwidth, 300 build minutes a month |

Render's *own* free PostgreSQL is not used here: it expires 30 days after creation, which would
end a demo mid-semester. Neon's does not expire.

**The one thing to know before you show this to anyone:** a sleeping Render service takes about
a minute to wake. Open the app a few minutes before a demo, or see §6.

---

## 1. Database — Neon

1. Sign up at **neon.tech** (sign in with GitHub; no card).
2. Create a project, any name, region closest to you.
3. Copy the **connection string**. It looks like
   `postgresql://user:pass@ep-something.aws.neon.tech/neondb?sslmode=require`.
4. **Make two edits** before using it, or the backend cannot connect:
   - `postgresql://` → `postgresql+asyncpg://`
   - `?sslmode=require` → `?ssl=true` (asyncpg does not understand `sslmode`)

   Final shape: `postgresql+asyncpg://user:pass@ep-something.aws.neon.tech/neondb?ssl=true`

## 2. Backend and AI service — Render

1. Sign up at **render.com** with GitHub (no card).
2. **New → Blueprint**, choose this repository. Render reads [`render.yaml`](../render.yaml) and
   proposes two services: `teamsync-ai-service` and `teamsync-backend`.
3. It asks for the values marked *sync: false*. For the first deploy:
   - `DATABASE_URL` — the edited Neon string from §1
   - `AI_SERVICE_URL` — put `https://teamsync-ai-service.onrender.com` (correct it in step 5 if
     Render assigned a different hostname)
   - `CORS_ORIGINS` — leave empty for now; it is filled in once the frontend exists
4. Apply. The first build takes five to ten minutes for both.
5. When they are live, check the hostnames Render actually gave them, and fix `AI_SERVICE_URL`
   on the backend if it differs. Then:

   ```
   https://<your-backend>.onrender.com/health   →  {"status":"healthy", ...}
   ```

## 3. Frontend — Netlify

From the repository, with the backend's address:

```bash
cd frontend
```

```bash
NEXT_PUBLIC_API_URL=https://<your-backend>.onrender.com netlify deploy --build --prod
```

The first run asks which site to create. Netlify prints the address, something like
`https://teamsync-ai.netlify.app`.

Because `NEXT_PUBLIC_*` is compiled into the browser bundle, changing the API address later
means deploying again, not just changing a setting.

## 4. Let the browser call the API

On Render, set `CORS_ORIGINS` on **teamsync-backend** to your Netlify address
(`https://teamsync-ai.netlify.app`, no trailing slash) and save. Render restarts the service.

Without this the pages load and every request fails — that is what a CORS error looks like.

## 5. First run

Open the Netlify address and **sign up — the first account owns the workspace**, so do it before
sharing the link.

To load the real Apache Mesos sprint the demo uses, from your own machine:

```bash
cd backend
```

```bash
python -m app.scripts.import_real_sprint app/scripts/fixtures/mesos_sprint_74.json --at 0.5 --api https://<your-backend>.onrender.com
```

It replays the sprint through the public API and prints an account to sign in with. Expect it to
be slow the first time: the service has to wake up.

## 6. Living with the sleep

A free Render service stops after 15 minutes without traffic.

- Before a demo, open the app and wait for the first page; everything after that is quick.
- A free uptime pinger (uptimerobot.com, every 10 minutes, no card) keeps it awake within the
  750 monthly hours — enough for one service continuously, or both if you only ping during the
  day.
- Or use **Azure for Students** instead: $100 of credit, no card, and nothing sleeps. It needs a
  university email. That is the better option if your college address works.

## 7. Updating

Render redeploys both services on every push to `main` (`autoDeploy: true`). The frontend does
not: run the Netlify command in §3 again.

## 8. What this setup is not

- **Not quick on the first request** after idle — about a minute.
- **Not big**: 512 MB per service and 0.5 GB of database. Fine for the demo sprint and a small
  team; not for the 2,000-task projects in the scaling figures.
- **Not backed up.** Neon keeps point-in-time recovery on the free plan for a short window; take
  your own dump before anything that matters: `pg_dump "<connection string>" > backup.sql`.
