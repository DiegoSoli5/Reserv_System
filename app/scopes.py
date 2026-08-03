from typing import Dict, List
from app.schemas import ClientRole

ROLE_SCOPES: Dict[ClientRole, List[str]] = {
    ClientRole.USER: [
        "profile:read",
        "profile:write"
        "events:read"
    ],
    ClientRole.ADMIN: [
        "profile:read",
        "profile:write",
        "clients:read",
        "clients:write",
        "clients:delete",
        "events:read",
        "events:create",
        "events:write"
    ]
}