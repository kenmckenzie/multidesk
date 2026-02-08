# Try rustdesk-api (lejianwen) with MultiDesk

Runs [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api) in Docker with **Caddy** in front for HTTPS (Let's Encrypt).

**Docker:** Ensure Docker is running and your user can access it (`docker run hello-world`). If you see "permission denied", add your user to the `docker` group or run with `sudo`.

## Prerequisites for HTTPS

- A **domain** that points to this server (e.g. `epyc1admin.multisaas.co.za`). Caddy will obtain and renew TLS certificates automatically.
- Ports **80** and **443** free on the host (Caddy binds them).

To use your own domain, edit `Caddyfile`: replace `epyc1admin.multisaas.co.za` with your domain, and in `docker-compose.yml` set `RUSTDESK_API_RUSTDESK_API_SERVER=https://<your-domain>`.

## Quick start

```bash
cd rustdesk-api-docker
docker compose up -d
```

- **Web Admin:** https://epyc1admin.multisaas.co.za/_admin/ (or your domain). Use HTTPS, not port 21114.
- **Default login:** username `admin`, password is **printed in the container log** on first run.

Get the initial admin password:

```bash
docker compose logs rustdesk-api 2>&1 | grep -i password
```

If no password appears, try `admin` / `admin` and change it after login.

## Configure MultiDesk

1. Open MultiDesk → **Settings** → **ID/Relay Server**.
2. Set **API Server** to: `https://epyc1admin.multisaas.co.za` (or your domain; use **https**).
3. Click **Login** and sign in with a user created in Web Admin (or the admin user).

Address book will sync after login.

## ID and relay server (same host)

This compose is set up for a server that also runs RustDesk ID (hbbs) and Relay (hbbr) on the **host**. The API runs in Docker and reaches them via `host.docker.internal`:

- `RUSTDESK_API_RUSTDESK_ID_SERVER=host.docker.internal:21116`
- `RUSTDESK_API_RUSTDESK_RELAY_SERVER=host.docker.internal:21117`

If your key differs from hbbs/hbbr, set `RUSTDESK_API_RUSTDESK_KEY` in the compose to match. On Linux, `extra_hosts: host.docker.internal:host-gateway` is already set so the container can reach the host.

## Caddy (HTTPS)

- **Caddy** listens on 80 and 443, serves the API at your domain, and obtains/renews Let's Encrypt certificates automatically.
- **rustdesk-api** is only exposed on the internal Docker network (port 21114); external access is via Caddy over HTTPS.

## Stop

```bash
docker compose down
```

Data is kept in the `rustdesk-api-data` and Caddy volumes. To remove everything: `docker compose down -v`.
