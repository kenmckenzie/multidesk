"""
MultiDesk Self-Hosted Address Book API Server

A self-hosted database-based address book system with user permissions.
Compatible with RustDesk/MultiDesk address book API.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./multidesk_ab.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI(title="MultiDesk Address Book API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, viewer
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client_permissions = relationship("UserClientPermission", back_populates="user")
    created_clients = relationship("ClientID", foreign_keys="ClientID.created_by", back_populates="creator")

class ClientID(Base):
    __tablename__ = "client_ids"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), unique=True, nullable=False, index=True)
    alias = Column(String(255))
    description = Column(Text)
    tags = Column(Text)  # JSON array
    password_hash = Column(String(255))  # Optional
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_clients")
    user_permissions = relationship("UserClientPermission", back_populates="client")

class UserClientPermission(Base):
    __tablename__ = "user_client_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("client_ids.id"), nullable=False)
    permission_type = Column(String(50), default="read")  # read, write, admin
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="client_permissions")
    client = relationship("ClientID", back_populates="user_permissions")
    
    __table_args__ = (UniqueConstraint('user_id', 'client_id', name='_user_client_uc'),)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class ClientIDCreate(BaseModel):
    client_id: str
    alias: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    password: Optional[str] = None
    notes: Optional[str] = None

class ClientIDUpdate(BaseModel):
    alias: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    password: Optional[str] = None
    notes: Optional[str] = None

class PermissionGrant(BaseModel):
    user_id: int
    client_id: int
    permission_type: str = "read"  # read, write, admin

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def check_permission(user: User, client: ClientID, permission: str, db: Session):
    """Check if user has permission on client"""
    if user.role == "admin":
        return True
    
    # Check direct permissions
    perm = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == user.id,
        UserClientPermission.client_id == client.id
    ).first()
    
    if perm:
        if permission == "read":
            return True
        elif permission == "write" and perm.permission_type in ["write", "admin"]:
            return True
        elif permission == "admin" and perm.permission_type == "admin":
            return True
    
    return False

# API Routes

@app.post("/api/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint"""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "type": "account",
        "user": {
            "name": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@app.get("/api/currentUser")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "name": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@app.post("/api/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout (stateless, just returns success)"""
    return {"message": "Logged out successfully"}

# Address Book Endpoints (RustDesk compatible)

@app.get("/api/ab/list")
async def list_address_books(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List address books - returns a default address book"""
    return [{
        "guid": "default",
        "name": "My address book",
        "share_rule": 0  # 0 = read, 1 = write
    }]

@app.post("/api/ab/peers")
async def get_peers(
    current: int = 1,
    pageSize: int = 100,
    ab: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get peers (client IDs) that the user has access to"""
    # Get all client IDs user has read access to
    if current_user.role == "admin":
        clients = db.query(ClientID).all()
    else:
        # Get clients user has permission for
        permissions = db.query(UserClientPermission).filter(
            UserClientPermission.user_id == current_user.id
        ).all()
        client_ids = [p.client_id for p in permissions]
        clients = db.query(ClientID).filter(ClientID.id.in_(client_ids)).all()
    
    # Pagination
    total = len(clients)
    start = (current - 1) * pageSize
    end = start + pageSize
    clients_page = clients[start:end]
    
    # Format response
    peers = []
    for client in clients_page:
        tags = json.loads(client.tags) if client.tags else []
        peers.append({
            "id": client.client_id,
            "alias": client.alias or client.client_id,
            "tags": tags,
            "note": client.notes or "",
            "username": "",  # Can be populated from recent sessions
            "hostname": "",  # Can be populated from recent sessions
            "platform": ""   # Can be populated from recent sessions
        })
    
    return {
        "total": total,
        "data": peers
    }

@app.post("/api/ab/peer/add/{ab_guid}")
async def add_peer(
    ab_guid: str,
    peer: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a peer to address book"""
    client_id_str = peer.get("id", "").replace(" ", "")
    if not client_id_str:
        return {"error": "Client ID is required"}
    
    # Check if client exists
    existing = db.query(ClientID).filter(ClientID.client_id == client_id_str).first()
    
    if existing:
        # Check if user has write permission
        if not check_permission(current_user, existing, "write", db):
            return {"error": "Permission denied"}
        
        # Update existing
        if "alias" in peer:
            existing.alias = peer["alias"]
        if "tags" in peer:
            existing.tags = json.dumps(peer["tags"])
        if "note" in peer:
            existing.notes = peer["note"]
        if "password" in peer and peer["password"]:
            existing.password_hash = get_password_hash(peer["password"])
    else:
        # Create new client
        new_client = ClientID(
            client_id=client_id_str,
            alias=peer.get("alias"),
            tags=json.dumps(peer.get("tags", [])),
            notes=peer.get("note"),
            created_by=current_user.id
        )
        if "password" in peer and peer["password"]:
            new_client.password_hash = get_password_hash(peer["password"])
        
        db.add(new_client)
        db.flush()
        
        # Grant admin permission to creator
        permission = UserClientPermission(
            user_id=current_user.id,
            client_id=new_client.id,
            permission_type="admin",
            granted_by=current_user.id
        )
        db.add(permission)
    
    db.commit()
    return {"message": "Success"}

@app.put("/api/ab/peer/update/{ab_guid}")
async def update_peer(
    ab_guid: str,
    peer: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a peer in address book"""
    client_id_str = peer.get("id", "").replace(" ", "")
    if not client_id_str:
        return {"error": "Client ID is required"}
    
    client = db.query(ClientID).filter(ClientID.client_id == client_id_str).first()
    if not client:
        return {"error": "Client not found"}
    
    if not check_permission(current_user, client, "write", db):
        return {"error": "Permission denied"}
    
    if "alias" in peer:
        client.alias = peer["alias"]
    if "tags" in peer:
        client.tags = json.dumps(peer["tags"])
    if "note" in peer:
        client.notes = peer["note"]
    
    db.commit()
    return {"message": "Success"}

@app.delete("/api/ab/peer/delete/{ab_guid}/{client_id}")
async def delete_peer(
    ab_guid: str,
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a peer from address book"""
    client_id_str = client_id.replace(" ", "")
    client = db.query(ClientID).filter(ClientID.client_id == client_id_str).first()
    if not client:
        return {"error": "Client not found"}
    
    if not check_permission(current_user, client, "admin", db):
        return {"error": "Permission denied"}
    
    db.delete(client)
    db.commit()
    return {"message": "Success"}

# Admin Endpoints

@app.post("/api/admin/users", dependencies=[Depends(get_current_user)])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if user exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

@app.get("/api/admin/users", dependencies=[Depends(get_current_user)])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]

@app.get("/api/admin/clients", dependencies=[Depends(get_current_user)])
async def list_all_clients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all client IDs (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    clients = db.query(ClientID).all()
    return [{
        "id": c.id,
        "client_id": c.client_id,
        "alias": c.alias,
        "tags": json.loads(c.tags) if c.tags else [],
        "notes": c.notes,
        "created_by": c.created_by,
        "created_at": c.created_at.isoformat() if c.created_at else None
    } for c in clients]

@app.post("/api/admin/permissions/grant", dependencies=[Depends(get_current_user)])
async def grant_permission(
    perm: PermissionGrant,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grant permission to user for client (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if permission exists
    existing = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == perm.user_id,
        UserClientPermission.client_id == perm.client_id
    ).first()
    
    if existing:
        existing.permission_type = perm.permission_type
        existing.granted_by = current_user.id
    else:
        new_perm = UserClientPermission(
            user_id=perm.user_id,
            client_id=perm.client_id,
            permission_type=perm.permission_type,
            granted_by=current_user.id
        )
        db.add(new_perm)
    
    db.commit()
    return {"message": "Permission granted"}

@app.get("/api/admin/permissions/{client_id}", dependencies=[Depends(get_current_user)])
async def get_client_permissions(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users with permissions for a client (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    permissions = db.query(UserClientPermission).filter(
        UserClientPermission.client_id == client_id
    ).all()
    
    return [{
        "user_id": p.user_id,
        "user": p.user.username,
        "permission_type": p.permission_type,
        "granted_at": p.granted_at.isoformat() if p.granted_at else None
    } for p in permissions]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
