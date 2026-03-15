from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.config import Settings
from app.models import User
from app.security import SESSION_COOKIE_NAME, decode_access_token


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session(request: Request):
    with Session(request.app.state.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_current_user(
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME) if request else None
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_id = decode_access_token(token, settings)
    except Exception as exc:  # pragma: no cover - auth failure path
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
