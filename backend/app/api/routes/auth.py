import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers a Freelancer or Client account with Argon2 password hashing.",
)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new user with unique email validation and Argon2 hashing."""
    normalized_email = req.email.lower().strip()

    # Check for existing user with identical email
    existing_user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password securely with Argon2id
    hashed_pwd = hash_password(req.password)

    new_user = User(
        full_name=req.full_name.strip(),
        email=normalized_email,
        password_hash=hashed_pwd,
        account_type=req.account_type,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("Successfully registered user %s (%s)", new_user.email, new_user.account_type)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT token",
    description="Authenticates credentials and returns a signed JWT access token.",
)
def login(req: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate user credentials and return a signed JWT token."""
    normalized_email = req.email.lower().strip()

    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support.",
        )

    # Generate JWT access token
    expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "account_type": user.account_type.value,
        },
        expires_delta=timedelta(minutes=expires_minutes),
    )

    logger.info("User %s logged in successfully", user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_minutes * 60,
        user=user,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieves the authenticated user's profile details.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return profile for the currently authenticated user."""
    return current_user

