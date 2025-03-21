from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.db.deps import get_supabase
from app.models.auth import UserLogin, UserRegister, Token
from app.utils.auth import create_access_token
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: Client = Depends(get_supabase)) -> Token:
    """
    Register a new user.
    """
    try:
        # Check if user already exists
        existing = db.table("users").select("id").eq("email", user_in.email).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user in Supabase Auth
        auth_response = db.auth.sign_up(
            {
                "email": user_in.email,
                "password": user_in.password,
                "options": {"data": {"name": user_in.name}},
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
            )

        # Create user in database
        result = (
            db.table("users")
            .insert(
                {
                    "id": auth_response.user.id,
                    "email": user_in.email,
                    "name": user_in.name,
                    "hashed_password": get_password_hash(user_in.password),
                }
            )
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile",
            )

        # Create access token
        access_token = create_access_token(auth_response.user.id)

        return Token(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: Client = Depends(get_supabase)) -> Token:
    """
    Login user and return access token.
    """
    try:
        # Authenticate with Supabase
        auth_response = db.auth.sign_in_with_password(
            {"email": user_in.email, "password": user_in.password}
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Create access token
        access_token = create_access_token(auth_response.user.id)

        return Token(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
