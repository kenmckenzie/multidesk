# Try rustdesk-api (lejianwen) with MultiDesk

Runs [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api) in Docker for address book and Web Admin.

**Docker:** Ensure Docker is running and your user can access it (`docker run hello-world`). If you see "permission denied", add your user to the `docker` group or run with `sudo`.

## Quick start

```bash
cd rustdesk-api-docker
docker compose up -d
```

- **Web Admin:** http://localhost:21114/_admin/
- **Default login:** username `admin`, password is **printed in the container log** on first run.

Get the initial admin password:

```bash
docker compose logs rustdesk-api 2>&1 | grep -i password
```

If no password appears, try `admin` / `admin` and change it after login.

## Configure MultiDesk

1. Open MultiDesk → **Settings** → **ID/Relay Server**.
2. Set **API Server** to: `http://localhost:21114` (or `http://<your-host>:21114` if testing from another machine).
3. Click **Login** and sign in with a user created in Web Admin (or the admin user).

Address book will sync after login.

## ID and relay server (same host)

This compose is set up for a server that also runs RustDesk ID (hbbs) and Relay (hbbr) on the same host. The API is configured with:

- `RUSTDESK_API_RUSTDESK_ID_SERVER=epyc1admin.multisaas.co.za:21116`
- `RUSTDESK_API_RUSTDESK_RELAY_SERVER=epyc1admin.multisaas.co.za:21117`

If your key differs from hbbs/hbbr, set `RUSTDESK_API_RUSTDESK_KEY` in the compose to match. If the API runs in Docker and cannot reach hbbs/hbbr on the host, ensure the hostname resolves from inside the container to the host (e.g. use the host’s LAN IP or add `extra_hosts` / host network as in the [lejianwen/rustdesk-api wiki](https://github.com/lejianwen/rustdesk-api/wiki)).

## Stop

```bash
docker compose down
```

Data is kept in the `rustdesk-api-data` volume. To remove it: `docker compose down -v`.
