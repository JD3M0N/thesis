from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlmodel import select

from app.deps import CurrentUserDep, SessionDep, SettingsDep
from app.logging_utils import get_audit_logger
from app.models import User
from app.schemas import AuthResponse, UserCreate, UserLogin, UserRead
from app.security import SESSION_COOKIE_NAME, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
audit_logger = get_audit_logger()


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    response: Response,
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
):
    existing_user = session.exec(select(User).where(User.email == payload.email)).first()
    if existing_user:
        audit_logger.warning(
            "auth.register_conflict email=%s ip=%s",
            payload.email,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(user.id, settings)
    _set_session_cookie(response, token)
    audit_logger.info(
        "auth.register_success user_id=%s email=%s ip=%s",
        user.id,
        user.email,
        request.client.host if request.client else "unknown",
    )
    return AuthResponse(user=UserRead.from_orm(user))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLogin,
    response: Response,
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        audit_logger.warning(
            "auth.login_failed email=%s ip=%s",
            payload.email,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id, settings)
    _set_session_cookie(response, token)
    audit_logger.info(
        "auth.login_success user_id=%s email=%s ip=%s",
        user.id,
        user.email,
        request.client.host if request.client else "unknown",
    )
    return AuthResponse(user=UserRead.from_orm(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, request: Request):
    audit_logger.info(
        "auth.logout ip=%s",
        request.client.host if request.client else "unknown",
    )
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@router.get("/me", response_model=AuthResponse)
def me(user: CurrentUserDep):
    return AuthResponse(user=UserRead.from_orm(user))
