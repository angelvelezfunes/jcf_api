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

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip authentication for /token endpoint
        if request.url.path in ["/token", "/docs", "/", "/openapi.json", "/send-email-reminder"]:
            return await call_next(request)

        try:
            auth_header = request.headers.get("Authorization")
            # print('Authorization:', auth_header)
            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing Authorization header")

            token = auth_header.split()[-1]
            if not token:
                raise HTTPException(status_code=401, detail="Missing token")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            if not username:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)


def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
