# Database-Based Address Book Design

This document outlines the design for a self-hosted, database-based address book system with user permissions, similar to RustDesk's paid version.

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

The existing address book system in MultiDesk already supports API-based address books. We need to:

1. **Configure API Server URL** - Set `api-server` option to point to self-hosted server
2. **Authentication** - Use existing login system or add custom auth
3. **API Compatibility** - Ensure API endpoints match RustDesk's expected format

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

1. Choose implementation option (Python recommended for quick start)
2. Create API server with database schema
3. Implement authentication and permission system
4. Create admin interface for managing users and permissions
5. Test integration with MultiDesk client
6. Deploy and configure
