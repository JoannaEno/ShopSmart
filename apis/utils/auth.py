from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import jwt

from core.config import settings

jwtSecret = settings.jwt_secret


def signJWT(user_id: str) -> Dict[str, str]:
    EXPIRES = datetime.now(tz=timezone.utc) + timedelta(days=365)

    payload = {
        "exp": EXPIRES,
        "userId": user_id,
    }
    token = jwt.encode(payload, jwtSecret, algorithm="HS256")

    return token


def decodeJWT(token: str) -> dict:
    try:
        decoded = jwt.decode(token, jwtSecret, algorithms=["HS256"])
        return decoded if decoded["expires"] else None
    except jwt.ExpiredSignatureError:
        print("Token expired. Get new one")
        return None
    except:
        return None


def encryptPassword(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def validatePassword(password: str, encrypted: str) -> str:
    return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtToken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtToken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
    
    
    async def get_user_id(token: str = Depends(JWTBearer())) -> Optional[int]:
    decoded = decodeJWT(token)
    return decoded.get("userId")