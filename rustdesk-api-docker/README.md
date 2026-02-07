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

## Optional: ID and relay server

This compose runs **only the API server** (address book, users, Web Admin). For full remote desktop you need an ID/relay server (e.g. [rustdesk-server](https://github.com/rustdesk/rustdesk-server) or [lejianwen/rustdesk-server](https://github.com/lejianwen/rustdesk-server)). Then set in this compose:

- `RUSTDESK_API_RUSTDESK_ID_SERVER=<host>:21116`
- `RUSTDESK_API_RUSTDESK_RELAY_SERVER=<host>:21117`
- `RUSTDESK_API_RUSTDESK_KEY=<your-key>` (if required)

See [lejianwen/rustdesk-api wiki](https://github.com/lejianwen/rustdesk-api/wiki) for full Docker setups.

## Stop

```bash
docker compose down
```

Data is kept in the `rustdesk-api-data` volume. To remove it: `docker compose down -v`.
