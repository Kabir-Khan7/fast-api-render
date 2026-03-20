from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import bcrypt
from typing import Optional

from database import get_db
from models.user import User
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verify_password(p: str, h: str) -> bool:
    return bcrypt.checkpw(p.encode(), h.encode())

def create_token(user_id: int, email: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "email": email, "exp": exp},
                      settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    # 1. Bearer header (production cross-domain)
    token = creds.credentials if creds else None
    # 2. httpOnly cookie (local dev)
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", status_code=201)
async def register(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email    = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        raise HTTPException(400, "Email and password required")
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")
    db.add(User(email=email, password_hash=hash_password(password)))
    db.commit()
    return {"message": "Account created", "email": email}


@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    body = await request.json()
    email    = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_token(user.id, user.email)
    # Cookie for same-domain (local dev)
    response.set_cookie(
        key="access_token", value=token,
        httponly=True, samesite="none", secure=True,
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )
    # Return token in body for cross-domain (production)
    return {"message": "Login successful", "email": user.email, "token": token}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", samesite="none", secure=True)
    return {"message": "Logged out"}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email,
            "created_at": current_user.created_at}