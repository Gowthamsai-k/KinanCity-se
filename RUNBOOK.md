# KinanCity local runbook

This runbook describes how to build and run the checked-out project locally. The default configuration is a safe synthetic dry run. It does not contact a target service, CAPTCHA provider, SMTP server, or proxy.

## 1. Clone the repository

```bash
git clone https://github.com/drallieiv/KinanCity.git
cd KinanCity
git checkout develop
```

For an existing checkout:

```bash
git status --short --branch
git log -1 --oneline
```

## 2. Prerequisites

- Docker Engine with Compose v2 (`docker compose version`)
- Git
- A browser
- Java 8 is the project target. The Docker build uses a modern JDK to compile the legacy source.

Verify Docker:

```bash
docker version
docker compose version
```

## 3. Create local configuration

```bash
cp .env.example .env
```

For the first test, leave:

```env
DRY_RUN=true
```

The `.env` file is ignored by Git. Never commit real API keys, passwords, SMTP credentials, or tokens.

## 4. Build and start the stack

```bash
docker compose config
docker compose up --build
```

Services:

| Service | Purpose | Address |
|---|---|---|
| `dashboard` | Browser UI | `http://127.0.0.1:8080` |
| `orchestrator` | Dashboard API and job state | `http://127.0.0.1:8090` |
| `mail` | KinanCity-mail container | port `2525` |
| `core-image` | Builds the KinanCity-core image | no public port |

Check health without starting a job:

```bash
curl http://127.0.0.1:8080/api/health
curl http://127.0.0.1:8080/api/status
```

## 5. Safe dry-run test

Open `http://127.0.0.1:8080`.

1. Enter a pattern such as `demo***`.
2. Enter a count such as `5`.
3. Click **Start authorized batch**.
4. Confirm the browser prompt.
5. Download the generated CSV after completion.

With `DRY_RUN=true`, records are synthetic. No core job or external request is made. Files are written to:

```text
runtime/kinancity-batch.csv
runtime/result.csv
runtime/links.log
```

These records are not usable external accounts.

## 6. Logs and status

```bash
docker compose ps
docker compose logs --tail=100 orchestrator
docker compose logs --tail=100 dashboard
docker compose logs --tail=100 mail
```

Stop the stack with:

```bash
docker compose down
```

## 7. Authorized real integration

 Set `DRY_RUN=false` only after the dry run works.

Configure `.env` privately with the values required by the checked-out adapters, then recreate the services:

```bash
docker compose down
docker compose up --build
```

The real pipeline can attempt a batch, receive activation messages, and export rows only when the core result is successful and the mail log reports `OK` or `DONE`. Success is not guaranteed because target behavior, CAPTCHA availability, SMTP/MX routing, rate limits, and current integrations can cause failures.

The orchestrator mounts `/var/run/docker.sock` to start the core image. Run it only on a machine you control and keep port `8090` private or access-controlled.

## 8. Troubleshooting

### Dashboard cannot connect

```bash
docker compose ps
curl http://127.0.0.1:8080/api/health
docker compose logs --tail=100 orchestrator dashboard
```

In Codespaces, forward ports `8080` and `8090` privately in the Ports panel, then reload the forwarded dashboard URL.

### `Unexpected token '<'`

The browser received an HTML gateway page instead of JSON. Check `/api/health` and the Nginx/orchestrator logs. Recreate the services:

```bash
docker compose up -d --force-recreate orchestrator dashboard
```

### Permission denied for `/runtime`

For direct local Python execution:

```bash
RUNTIME_DIR="$PWD/runtime" python3 orchestrator/server.py
```

Compose sets the container path automatically.

## 9. Source and build notes

See [`BUILD_NOTES.md`](BUILD_NOTES.md) for Maven, module, and architecture details. `Dockerfile` builds core, `Dockerfile.mail` builds mail, and `Dockerfile.orchestrator` builds the local dashboard API service.

The dashboard is a lightweight static page. It does not implement CAPTCHA solving, proxy rotation, or account verification by itself.
