# Database-Based Address Book Design

This document outlines the design for a self-hosted, database-based address book system with user permissions, similar to RustDesk's paid version.

## Recommendation: Use an Existing RustDesk API Server

**Prefer deploying an existing RustDesk-compatible API server instead of building a new one.** MultiDesk's client uses the same address book API as RustDesk, so any server that implements that API will work.

### Recommended: lejianwen/rustdesk-api

- **Repository:** [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api) (Go)
- **Features:** Full RustDesk PC API (login, address book, groups), Web Admin (users, devices, address books, tags, LDAP, OAuth), Web Client, SQLite/MySQL, Docker.
- **Compatibility:** Implements the same API contract the MultiDesk Flutter client expects (`/api/login`, `/api/currentUser`, `/api/ab/*`, etc.).
- **Deployment:** Set MultiDesk's **API Server** (Settings → ID/Relay Server) to your rustdesk-api URL (e.g. `http://your-server:21114`). No client code changes needed.

### Why use rustdesk-api instead of writing new

- One less codebase to maintain; focus on the MultiDesk client only.
- Battle-tested server, admin UI, and optional LDAP/OIDC.
- Same API surface MultiDesk already calls; no custom endpoints to implement.
- Active community and releases.

### When to use the in-repo api-server or a custom build

- You need a minimal, single-binary or Python stack and are fine with fewer features.
- You need strict control over schema, auth, or deployment and are willing to maintain it.
- You are extending the API in ways rustdesk-api does not support.

### Alternatives (other RustDesk API servers)

| Project | Language | Status | Pros | Cons |
|--------|----------|--------|------|------|
| **[lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api)** | Go | **Recommended** — very active (e.g. v2.7 Sept 2025), 2.6k+ stars | Full API, Web Admin, LDAP/OAuth, SQLite/MySQL/PostgreSQL, Docker, frequent releases | Go stack (different from MultiDesk); v2.7 removed webclient2 (DMCA) |
| **[sctg-development/sctgdesk-server](https://github.com/sctg-development/sctgdesk-server)** | **Rust** | Active; integrated ID/relay + API + web console in one | Same language as MultiDesk; Pro-like API (personal + shared address book); single binary or [standalone API](https://github.com/sctg-development/sctgdesk-api-server) | README states *not yet ready for production*; Bearer tokens in-memory only (re-login after restart); smaller community |
| **[lantongxue/rustdesk-api-server-pro](https://github.com/lantongxue/rustdesk-api-server-pro)** | Go | Maintained, ~239 stars | Full address book API, Web UI, open-source | AGPL-3.0; smaller community than lejianwen |
| **Official [RustDesk Server Pro](https://rustdesk.com/docs/en/self-host/rustdesk-server-pro/)** | — | Commercial | Official, production support | Paid; some past reports of address book API (403) issues |

**Summary:** For **most up-to-date and stable** in the open-source ecosystem, **lejianwen/rustdesk-api** remains the best choice (active releases, large user base, production-ready). If you strongly prefer a **Rust** stack and can accept “development” status and token persistence limits, **sctgdesk-server** / **sctgdesk-api-server** is the Rust alternative to watch.

The schema, endpoint list, and security notes below remain useful as **reference** for the API contract and for custom implementations.

---

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ MultiDesk   │──────│ API Server   │──────│  Database   │
│  Client     │      │ (Self-hosted)│      │ (SQLite/    │
│             │      │              │      │  PostgreSQL)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            │
                    ┌───────┴───────┐
                    │   User Auth   │
                    │  & Permissions│
                    └───────────────┘
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'user', 'viewer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Client IDs Table
```sql
CREATE TABLE client_ids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id VARCHAR(255) UNIQUE NOT NULL,
    alias VARCHAR(255),
    description TEXT,
    tags TEXT, -- JSON array of tags
    password_hash VARCHAR(255), -- Optional stored password
    notes TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### User-Client Permissions Table
```sql
CREATE TABLE user_client_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    permission_type VARCHAR(50) DEFAULT 'read', -- 'read', 'write', 'admin'
    granted_by INTEGER,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (client_id) REFERENCES client_ids(id),
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(user_id, client_id)
);
```

### Groups Table (Optional - for bulk permission management)
```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_groups (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE group_client_permissions (
    group_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    permission_type VARCHAR(50) DEFAULT 'read',
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (client_id) REFERENCES client_ids(id),
    PRIMARY KEY (group_id, client_id)
);
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Address Book
- `GET /api/ab/list` - List all address books (for compatibility)
- `GET /api/ab/peers` - Get peers (client IDs) user has access to
  - Query params: `page`, `pageSize`, `tags`, `search`
- `POST /api/ab/peer/add` - Add new client ID (requires write permission)
- `PUT /api/ab/peer/update/:id` - Update client ID (requires write permission)
- `DELETE /api/ab/peer/delete/:id` - Delete client ID (requires admin permission)

### Permissions
- `GET /api/permissions/clients` - List all client IDs with permissions
- `POST /api/permissions/grant` - Grant permission to user
- `DELETE /api/permissions/revoke/:user_id/:client_id` - Revoke permission
- `GET /api/permissions/users/:client_id` - Get users with access to client

### Admin (if user is admin)
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Delete user
- `GET /api/admin/clients` - List all client IDs
- `POST /api/admin/clients` - Create client ID
- `PUT /api/admin/clients/:id` - Update client ID
- `DELETE /api/admin/clients/:id` - Delete client ID

## Implementation Options

### Option 1: Python Flask/FastAPI Server (Recommended for Quick Start)

**Pros:**
- Fast development
- Easy database integration (SQLAlchemy)
- Good for prototyping

**Tech Stack:**
- FastAPI or Flask
- SQLAlchemy ORM
- SQLite (development) / PostgreSQL (production)
- JWT for authentication

### Option 2: Rust Actix-Web Server

**Pros:**
- Same language as MultiDesk
- High performance
- Type safety

**Tech Stack:**
- Actix-web
- Diesel or SQLx
- SQLite / PostgreSQL

### Option 3: Node.js Express Server

**Pros:**
- JavaScript ecosystem
- Easy to find developers
- Good libraries

**Tech Stack:**
- Express.js
- Sequelize or TypeORM
- SQLite / PostgreSQL

## Integration with MultiDesk

The existing address book system in MultiDesk already supports API-based address books. Any server that implements the RustDesk API (e.g. rustdesk-api) works without client changes.

1. **Configure API Server URL** - Set `api-server` option (Settings → ID/Relay Server) to your API server base URL.
2. **Authentication** - MultiDesk calls `POST /api/login`, `POST /api/currentUser`, and `GET /api/login-options`; the server must implement these.
3. **API Compatibility** - Address book endpoints must match the formats below (same as RustDesk client).

### Required API Response Formats

**Get Peers:**
```json
{
  "total": 100,
  "data": [
    {
      "id": "123 456 789",
      "alias": "Client Name",
      "tags": ["tag1", "tag2"],
      "note": "Notes here",
      "username": "user@hostname",
      "hostname": "hostname",
      "platform": "Windows"
    }
  ]
}
```

**Add Peer:**
```json
{
  "id": "123 456 789",
  "alias": "Client Name",
  "tags": ["tag1"],
  "note": "Notes"
}
```

## Security Considerations

1. **Password Storage** - Use bcrypt/argon2 for password hashing
2. **JWT Tokens** - Use JWT for stateless authentication
3. **HTTPS** - Always use HTTPS in production
4. **Input Validation** - Validate all inputs
5. **SQL Injection** - Use parameterized queries
6. **Rate Limiting** - Implement rate limiting on API endpoints

## Deployment

### Docker Compose Setup
```yaml
version: '3.8'
services:
  api:
    build: ./api-server
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/multidesk_ab
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=multidesk_ab
      - POSTGRES_USER=multidesk
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

## Next Steps

**If using an existing RustDesk API server (recommended):**

1. Deploy [lejianwen/rustdesk-api](https://github.com/lejianwen/rustdesk-api) (Docker or binary; see its README).
2. Optionally pair with [lejianwen/rustdesk-server](https://github.com/lejianwen/rustdesk-server) for ID/relay if self-hosting full stack.
3. In MultiDesk: Settings → ID/Relay Server → set **API Server** to your rustdesk-api URL.
4. Log in with a user created in the API server (default admin password is printed on first run; change it).

**If building a custom server instead:**

1. Choose implementation option (Python/Rust/Node as in Implementation Options).
2. Implement the API contract above (auth: `/api/login`, `/api/currentUser`; address book: `/api/ab/*` as used by MultiDesk).
3. Use the database schema and security considerations in this document.
4. Test with MultiDesk client and deploy.
