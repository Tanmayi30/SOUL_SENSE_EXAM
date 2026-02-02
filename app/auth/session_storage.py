"""
Session Storage Utilities for Remember Me Feature
=================================================
Manages persistent session storage for auto-login functionality.
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Session file location in app_data directory
SESSION_FILE = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "app_data" / "session.json"
SESSION_MAX_AGE_DAYS = 30  # Sessions expire after 30 days


def _ensure_session_dir():
    """Ensure the session directory exists."""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)


def save_session(username: str, remember_me: bool = False) -> bool:
    """
    Save session data to file.
    
    Args:
        username: The logged-in username
        remember_me: If True, session persists across app restarts
        
    Returns:
        True if session was saved successfully
    """
    if not remember_me:
        # Don't save session if remember_me is not checked
        clear_session()
        return True
    
    try:
        _ensure_session_dir()
        session_data = {
            "username": username,
            "login_time": time.time(),
            "expires_at": time.time() + (SESSION_MAX_AGE_DAYS * 24 * 60 * 60)
        }
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logging.info(f"Session saved for user: {username}")
        return True
    except Exception as e:
        logging.error(f"Failed to save session: {e}")
        return False


def get_session() -> Optional[Dict[str, Any]]:
    """
    Retrieve saved session data.
    
    Returns:
        Session data dict if valid session exists, None otherwise
    """
    try:
        if not SESSION_FILE.exists():
            return None
        
        with open(SESSION_FILE, 'r') as f:
            session_data = json.load(f)
        
        # Validate session structure
        if not all(k in session_data for k in ["username", "login_time", "expires_at"]):
            clear_session()
            return None
        
        return session_data
    except Exception as e:
        logging.error(f"Failed to read session: {e}")
        return None


def is_session_valid() -> bool:
    """
    Check if a valid, non-expired session exists.
    
    Returns:
        True if valid session exists
    """
    session = get_session()
    if not session:
        return False
    
    # Check if session has expired
    if time.time() > session.get("expires_at", 0):
        clear_session()
        return False
    
    return True


def get_saved_username() -> Optional[str]:
    """
    Get the username from a valid saved session.
    
    Returns:
        Username if valid session exists, None otherwise
    """
    if is_session_valid():
        session = get_session()
        return session.get("username") if session else None
    return None


def clear_session() -> bool:
    """
    Clear saved session data.
    
    Returns:
        True if session was cleared (or didn't exist)
    """
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
            logging.info("Session cleared")
        return True
    except Exception as e:
        logging.error(f"Failed to clear session: {e}")
        return False
