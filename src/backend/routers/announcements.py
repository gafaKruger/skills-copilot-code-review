"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    expires_at: datetime
    starts_at: Optional[datetime] = None


class AnnouncementUpdate(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    expires_at: datetime
    starts_at: Optional[datetime] = None


def _require_logged_in_teacher(username: Optional[str]) -> Dict[str, Any]:
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _serialize_announcement(document: Dict[str, Any]) -> Dict[str, Any]:
    starts_at = document.get("starts_at")
    expires_at = document.get("expires_at")

    return {
        "id": str(document["_id"]),
        "message": document.get("message", ""),
        "starts_at": starts_at.isoformat() if starts_at else None,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def _validate_dates(starts_at: Optional[datetime], expires_at: datetime) -> None:
    if starts_at and starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if starts_at and expires_at <= starts_at:
        raise HTTPException(
            status_code=400,
            detail="Expiration date must be later than start date"
        )


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return all currently active announcements for public display."""
    now = datetime.now(timezone.utc)
    query = {
        "expires_at": {"$gte": now},
        "$or": [
            {"starts_at": {"$exists": False}},
            {"starts_at": None},
            {"starts_at": {"$lte": now}}
        ]
    }

    announcements = announcements_collection.find(query).sort("expires_at", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Return all announcements for logged-in teachers and admins."""
    _require_logged_in_teacher(username)

    announcements = announcements_collection.find({}).sort("expires_at", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.post("/manage", response_model=Dict[str, Any])
def create_announcement(payload: AnnouncementCreate, username: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Create a new announcement. Requires logged-in teacher/admin."""
    _require_logged_in_teacher(username)
    _validate_dates(payload.starts_at, payload.expires_at)

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = announcements_collection.insert_one(
        {
            "message": message,
            "starts_at": payload.starts_at,
            "expires_at": payload.expires_at,
        }
    )

    created = announcements_collection.find_one({"_id": result.inserted_id})
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create announcement")

    return _serialize_announcement(created)


@router.put("/manage/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: AnnouncementUpdate,
    username: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Update an existing announcement. Requires logged-in teacher/admin."""
    _require_logged_in_teacher(username)
    _validate_dates(payload.starts_at, payload.expires_at)

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        object_id = ObjectId(announcement_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid announcement id") from exc

    result = announcements_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "message": message,
                "starts_at": payload.starts_at,
                "expires_at": payload.expires_at,
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated = announcements_collection.find_one({"_id": object_id})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to load updated announcement")

    return _serialize_announcement(updated)


@router.delete("/manage/{announcement_id}", response_model=Dict[str, str])
def delete_announcement(announcement_id: str, username: Optional[str] = Query(None)) -> Dict[str, str]:
    """Delete an announcement. Requires logged-in teacher/admin."""
    _require_logged_in_teacher(username)

    try:
        object_id = ObjectId(announcement_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid announcement id") from exc

    result = announcements_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
