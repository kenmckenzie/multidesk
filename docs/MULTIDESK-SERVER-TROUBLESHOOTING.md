# MultiDesk server not working (multidesk.multisaas.co.za / multisaas.multidesk.co.za)

Use this when the API / ID / Relay or login “still doesn’t work”.

## 1. Run the check script on the server

On the server, in your `rustdesk-api-docker` folder:

```bash
chmod +x check-multidesk-server.sh
./check-multidesk-server.sh
```

It checks: DNS, containers, ports 443/21114/21116/21117, local API, and HTTPS to the domain. Fix whatever the script reports as missing or failing.

## 2. Checklist (manual)

### DNS
- **multidesk.multisaas.co.za** must resolve to this server’s **public IP**.
- From the server: `getent ahosts multidesk.multisaas.co.za` or `nslookup multidesk.multisaas.co.za`.
- From your PC: same lookup; the IP must be the server’s public IP.

### Caddy
- Caddy must be running and serving **multidesk.multisaas.co.za** and/or **multisaas.multidesk.co.za** (see `rustdesk-api-docker/Caddyfile`). Both hostnames are configured to serve rustdesk-api.
- Restart after changing the Caddyfile:  
  `cd rustdesk-api-docker && docker compose up -d caddy --force-recreate`
- Check for certificate errors:  
  `docker compose logs caddy`
- From the server:  
  `curl -k -s -o /dev/null -w "%{http_code}" https://multidesk.multisaas.co.za/api/`  
  should return **200**.

### rustdesk-api
- Container must be running:  
  `docker ps | grep rustdesk-api`
- Env must match your domain:  
  `RUSTDESK_API_RUSTDESK_API_SERVER=https://multidesk.multisaas.co.za`
- Local API must respond:  
  `curl -s http://127.0.0.1:21114/api/`  
  should return JSON.

### ID and Relay (hbbs / hbbr)
- **21116** (ID) and **21117** (relay) must be **listening on the host** (hbbs/hbbr, not Docker).
- On the server:  
  `ss -tlnp | grep -E '21116|21117'`
- From the **internet**, **21116** and **21117** must be **reachable** (firewall and router/security group must allow them). MultiDesk connects to `multidesk.multisaas.co.za:21116` and `multidesk.multisaas.co.za:21117`.

### Client / MultiDesk app
- In Settings → ID/Relay server, use:
  - **API server:** `https://multidesk.multisaas.co.za` (no port)
  - **ID server:** `multidesk.multisaas.co.za` (app uses port 21116)
  - **Relay server:** `multidesk.multisaas.co.za` (app uses port 21117)
- If you had an old domain saved, clear the fields and re-enter the above, then Save and restart the app.

## 3. Common causes

| Symptom | Likely cause |
|--------|----------------|
| “Can’t connect” or timeout to API | DNS wrong, or Caddy not serving the domain, or 443 blocked |
| API works in browser but app can’t login | App still using old URL; clear and set `https://multidesk.multisaas.co.za` |
| ID/relay connection failed | 21116 or 21117 not open on server/firewall, or hbbs/hbbr not running |
| Certificate error in browser | Caddy didn’t get a cert for multidesk.multisaas.co.za; check `docker compose logs caddy` and DNS |

## 4. Get Caddy to pick up the Caddyfile

If you changed `rustdesk-api-docker/Caddyfile`:

```bash
cd rustdesk-api-docker
docker compose up -d caddy --force-recreate
docker compose logs -f caddy
```

Watch for ACME/certificate errors. Ensure **multidesk.multisaas.co.za** resolves to this server before Caddy runs.
