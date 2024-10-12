from fastapi import Security
from fastapi.security import HTTPBearer

AuthRequired = Security(HTTPBearer())
