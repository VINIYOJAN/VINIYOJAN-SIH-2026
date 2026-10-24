from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

passwords = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def create_token(user: User):
    return jwt.encode({'sub':user.id,'exp':datetime.now(timezone.utc)+timedelta(hours=2)}, settings.jwt_secret, algorithm='HS256')

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(401, 'Authentication required')
    try: user_id = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=['HS256'])['sub']
    except (jwt.PyJWTError, KeyError): raise HTTPException(401, 'Invalid or expired token')
    user = db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(401, 'Inactive user')
    return user

def require_roles(*roles):
    def checker(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, 'Insufficient permissions')
        return user
    return checker
