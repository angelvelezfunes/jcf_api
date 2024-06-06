from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp
import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, db: Session, secret_key: str, algorithm: str):
        super().__init__(app)
        self.db = db
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for /token endpoint
        if request.url.path in ["/token", "/docs", "/", "/openapi.json"]:
            return await call_next(request)

        # Validate token for other endpoints
        if "Authorization" not in request.headers:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = request.headers["Authorization"].split()[-1]
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            request.state.user = get_user(self.db, username)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        return await call_next(request)


def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
