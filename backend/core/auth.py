from datetime import datetime, timedelta, timezone
from hmac import compare_digest

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from core.config import JWT_SECRET
from core.roles import Role

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
class Credentials(BaseModel):
    email: str
    password: str

@router.post('/auth/login')
def login(credentials: Credentials):
    try:
        role = Role(credentials.email.removesuffix('@demo.test'))
    except ValueError:
        raise HTTPException(401, detail='账号或密码错误')
    if credentials.email != f'{role}@demo.test' or not compare_digest(credentials.password.encode(), b'DemoC0de!2026'):
        raise HTTPException(401, detail='账号或密码错误')
    expires = datetime.now(timezone.utc) + timedelta(hours=4)
    return {'token': jwt.encode({'sub': credentials.email, 'role': role, 'exp': expires}, JWT_SECRET,
                                 algorithm='HS256'), 'role': role}

def actor(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials:
        raise HTTPException(401, detail='请先登录')
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'],
                          options={'require': ['exp', 'sub', 'role']})
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='会话已失效，请重新登录')

def allow(user, roles):
    if user['role'] not in roles:
        raise HTTPException(403, detail='当前角色无权提交此操作')
