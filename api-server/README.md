# MultiDesk Self-Hosted Address Book API Server

A self-hosted, database-based address book system with user permissions for MultiDesk.

## Features

- ✅ Database-backed address book (SQLite/PostgreSQL)
- ✅ User authentication with JWT tokens
- ✅ Role-based access control (admin, user, viewer)
- ✅ Per-client permission system (read, write, admin)
- ✅ RustDesk API compatible endpoints
- ✅ Admin interface for managing users and permissions

## Quick Start

### 1. Install Dependencies

```bash
cd api-server
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
export DATABASE_URL="sqlite:///./multidesk_ab.db"  # or PostgreSQL URL
export SECRET_KEY="your-secret-key-change-this"
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Create Admin User

The first user needs to be created manually in the database or via a script:

```python
from main import SessionLocal, User, get_password_hash

db = SessionLocal()
admin = User(
    username="admin",
    password_hash=get_password_hash("admin123"),
    role="admin"
)
db.add(admin)
db.commit()
```

### 5. Configure MultiDesk Client

In MultiDesk settings:
1. Go to Settings → ID/Relay Server
2. Set API Server to: `http://your-server:8000` (or `https://your-server:8000`)
3. Login with your username and password

## API Endpoints

### Authentication
- `POST /api/login` - Login and get JWT token
- `GET /api/currentUser` - Get current user info
- `POST /api/logout` - Logout

### Address Book (RustDesk Compatible)
- `GET /api/ab/list` - List address books
- `POST /api/ab/peers` - Get peers (client IDs) with pagination
- `POST /api/ab/peer/add/{ab_guid}` - Add peer
- `PUT /api/ab/peer/update/{ab_guid}` - Update peer
- `DELETE /api/ab/peer/delete/{ab_guid}/{client_id}` - Delete peer

### Admin (Admin Only)
- `POST /api/admin/users` - Create user
- `GET /api/admin/users` - List all users
- `GET /api/admin/clients` - List all client IDs
- `POST /api/admin/permissions/grant` - Grant permission
- `GET /api/admin/permissions/{client_id}` - Get permissions for client

## Database Schema

See `DATABASE_ADDRESS_BOOK_DESIGN.md` for full schema details.

## Docker Deployment

```bash
docker build -t multidesk-api .
docker run -d -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./multidesk_ab.db" \
  -e SECRET_KEY="your-secret-key" \
  -v $(pwd)/data:/app/data \
  multidesk-api
```

## Production Considerations

1. **Use PostgreSQL** instead of SQLite for production
2. **Change SECRET_KEY** to a strong random value
3. **Enable HTTPS** with reverse proxy (nginx, Caddy)
4. **Set up backups** for the database
5. **Configure CORS** appropriately
6. **Use environment variables** for sensitive data

## Integration with MultiDesk

The API is compatible with RustDesk's address book API. Once configured:
1. Users login via MultiDesk settings
2. Address book syncs automatically
3. Only client IDs the user has permission for are visible
4. Admins can manage all clients and users
