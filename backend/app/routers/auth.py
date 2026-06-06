from fastapi import APIRouter, HTTPException, status, Header, Depends
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.database import get_database
from app.config import settings
from typing import Optional
import bcrypt
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly."""
    # Truncate to 72 bytes to avoid bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        password_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and validate user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    from bson import ObjectId
    db = get_database()

    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        logger.error(f"DB lookup error: {e}")
        raise HTTPException(status_code=401, detail="User lookup failed")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user["id"] = str(user["_id"])
    return user


@router.post("/register", response_model=Token)
async def register(data: UserCreate):
    """Register a new user account."""
    db = get_database()

    # Check if email already exists
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists"
        )

    # Validate password length
    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    # Hash the password
    try:
        hashed_pw = hash_password(data.password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not process password. Please try again."
        )

    # Create user document
    doc = {
        "email": data.email,
        "full_name": data.full_name,
        "preferred_language": data.preferred_language,
        "hashed_password": hashed_pw,
        "created_at": datetime.utcnow(),
        "is_active": True
    }

    try:
        result = await db.users.insert_one(doc)
        user_id = str(result.inserted_id)
    except Exception as e:
        logger.error(f"DB insert error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not create account. Please try again."
        )

    # Create and return token
    token = create_token(user_id, data.email)

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            email=data.email,
            full_name=data.full_name,
            preferred_language=data.preferred_language,
            created_at=doc["created_at"],
            is_active=True
        )
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """Login with email and password."""
    db = get_database()

    # Find user
    user = await db.users.find_one({"email": data.email})
    if not user:
        raise HTTPException(
            status_code=401,
            detail="No account found with this email"
        )

    # Verify password
    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    user_id = str(user["_id"])
    token = create_token(user_id, user["email"])

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            email=user["email"],
            full_name=user["full_name"],
            preferred_language=user.get("preferred_language", "en"),
            created_at=user["created_at"],
            is_active=user.get("is_active", True)
        )
    )
