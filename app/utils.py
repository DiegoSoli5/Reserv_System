from pwdlib import PasswordHash
from .config import settings
from datetime import datetime, timezone

password_hash = PasswordHash.recommended()

def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

def get_password(password):
    return password_hash.hash(password)

def get_current_time():
    return datetime.now(timezone.utc)