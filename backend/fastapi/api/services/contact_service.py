"""
Contact Us service for storing and retrieving contact form submissions.
Stores submissions in a JSON file with atomic writes.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import asyncio
import aiofiles

# Path to the contact submissions JSON file
DATA_DIR = Path(__file__).parent.parent.parent / "data"
CONTACT_FILE = DATA_DIR / "contact_submissions.json"

# Lock for atomic writes
_file_lock = asyncio.Lock()


async def _ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


async def _read_submissions() -> List[dict]:
    """Read all submissions from the JSON file."""
    await _ensure_data_dir()
    
    if not CONTACT_FILE.exists():
        return []
    
    try:
        async with aiofiles.open(CONTACT_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content) if content.strip() else []
    except (json.JSONDecodeError, IOError):
        return []


async def _write_submissions(submissions: List[dict]) -> None:
    """Write submissions to the JSON file with atomic write."""
    await _ensure_data_dir()
    
    # Write to temp file first, then rename for atomicity
    temp_file = CONTACT_FILE.with_suffix('.tmp')
    
    async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(submissions, indent=2, ensure_ascii=False))
    
    # Atomic rename
    os.replace(temp_file, CONTACT_FILE)


async def create_submission(
    name: str,
    email: str,
    subject: str,
    message: str
) -> dict:
    """
    Create a new contact submission.
    
    Args:
        name: Sender's full name
        email: Sender's email address
        subject: Message subject
        message: Message content
    
    Returns:
        The created submission with id and timestamp
    """
    submission = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "email": email.strip().lower(),
        "subject": subject.strip(),
        "message": message.strip(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "read": False
    }
    
    async with _file_lock:
        submissions = await _read_submissions()
        submissions.append(submission)
        await _write_submissions(submissions)
    
    return submission


async def get_all_submissions(
    limit: int = 100,
    offset: int = 0,
    unread_only: bool = False
) -> dict:
    """
    Get all contact submissions with pagination.
    
    Args:
        limit: Maximum number of submissions to return
        offset: Number of submissions to skip
        unread_only: If True, only return unread submissions
    
    Returns:
        Dictionary with submissions list and total count
    """
    submissions = await _read_submissions()
    
    if unread_only:
        submissions = [s for s in submissions if not s.get("read", False)]
    
    # Sort by timestamp descending (newest first)
    submissions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    total = len(submissions)
    paginated = submissions[offset:offset + limit]
    
    return {
        "submissions": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }


async def get_submission_by_id(submission_id: str) -> Optional[dict]:
    """Get a single submission by ID."""
    submissions = await _read_submissions()
    
    for submission in submissions:
        if submission.get("id") == submission_id:
            return submission
    
    return None


async def mark_as_read(submission_id: str) -> Optional[dict]:
    """Mark a submission as read."""
    async with _file_lock:
        submissions = await _read_submissions()
        
        for submission in submissions:
            if submission.get("id") == submission_id:
                submission["read"] = True
                await _write_submissions(submissions)
                return submission
        
        return None


async def delete_submission(submission_id: str) -> bool:
    """Delete a submission by ID."""
    async with _file_lock:
        submissions = await _read_submissions()
        original_count = len(submissions)
        
        submissions = [s for s in submissions if s.get("id") != submission_id]
        
        if len(submissions) < original_count:
            await _write_submissions(submissions)
            return True
        
        return False


# Singleton-like access
class ContactService:
    """Service class for contact form operations."""
    
    async def create(self, name: str, email: str, subject: str, message: str) -> dict:
        return await create_submission(name, email, subject, message)
    
    async def get_all(self, limit: int = 100, offset: int = 0, unread_only: bool = False) -> dict:
        return await get_all_submissions(limit, offset, unread_only)
    
    async def get_by_id(self, submission_id: str) -> Optional[dict]:
        return await get_submission_by_id(submission_id)
    
    async def mark_read(self, submission_id: str) -> Optional[dict]:
        return await mark_as_read(submission_id)
    
    async def delete(self, submission_id: str) -> bool:
        return await delete_submission(submission_id)


contact_service = ContactService()
