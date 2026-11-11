from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from backend.app.api.deps import get_current_user, require_roles

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Auth & Users"],
    summary="User Login & Token Generation",
    description="Authenticates staff credentials (email & password) and returns a signed JWT bearer token.",
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "email": "admin@clinic.com",
                            "full_name": "Clinic Administrator",
                            "role": "admin",
                            "is_active": True,
                            "created_at": "2026-11-11T20:00:00Z"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password"}
                }
            }
        }
    }
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token = create_access_token({
        "sub": user.email,
        "role": user.role,
        "user_id": user.id,
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["Auth & Users"],
    summary="Get Current User Profile",
    description="Retrieves the profile of the currently authenticated staff user.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth & Users"],
    summary="Admin User Creation",
    description="Allows clinic administrators to register new staff accounts (Doctors, Receptionists, Admins).",
    responses={
        201: {"description": "User created successfully"},
        403: {"description": "Forbidden: Requires Admin role"},
        409: {"description": "Conflict: Email address already registered"},
    }
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
):
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role.value if isinstance(user_in.role, UserRole) else user_in.role,
        is_active=user_in.is_active,
    )
    created_user = user_repo.create(new_user)
    return UserResponse.model_validate(created_user)


@router.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Auth & Users"],
    summary="List Staff Users",
    description="Retrieves all staff accounts. Restricted to administrators.",
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
):
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]
