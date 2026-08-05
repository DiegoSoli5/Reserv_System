from typing import Dict, List
from app.schemas import ClientRole

ROLE_SCOPES: Dict[ClientRole, List[str]] = {
    ClientRole.USER: [
        "profile:read",
        "profile:write",
        "bookings:read",
        "bookings:create",
        "bookings:delete",
        "bookings:write"
    ],
    ClientRole.ADMIN: [
        "profile:read",
        "profile:write",
        "clients:read",
        "clients:write",
        "clients:delete",
        "events:create",
        "events:delete",
        "events:write",
        "bookings:read",
        "bookings:read-all",
        "bookings:create",
        "bookings:delete",
        "bookings:write"
    ]
}