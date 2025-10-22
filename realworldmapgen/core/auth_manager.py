"""
Authentication and User Management
Multi-user support infrastructure
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import json
import hashlib

logger = logging.getLogger(__name__)


class User:
    """User model"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str = "user",
        created_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role  # 'admin', 'user', 'viewer'
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login: Optional[str] = None
        self.is_active = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create from dictionary"""
        user = cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            role=data.get("role", "user"),
            created_at=data.get("created_at")
        )
        user.last_login = data.get("last_login")
        user.is_active = data.get("is_active", True)
        return user


class Session:
    """User session"""
    
    def __init__(self, session_id: str, user_id: str, expires_at: datetime):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.now()
        self.expires_at = expires_at
        self.last_activity = datetime.now()
    
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        return datetime.now() < self.expires_at
    
    def refresh(self, duration: timedelta = timedelta(hours=24)):
        """Refresh session expiry"""
        self.expires_at = datetime.now() + duration
        self.last_activity = datetime.now()


class AuthManager:
    """
    Authentication and session management
    """
    
    def __init__(self, storage_file: Path = Path("./cache/users.json")):
        """
        Initialize auth manager
        
        Args:
            storage_file: File to store user data
        """
        self.storage_file = storage_file
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from storage"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        user_id: User.from_dict(user_data)
                        for user_id, user_data in data.get("users", {}).items()
                    }
                logger.info(f"Loaded {len(self.users)} users")
            except Exception as e:
                logger.error(f"Failed to load users: {e}")
    
    def _save_users(self):
        """Save users to storage"""
        try:
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "users": {
                    user_id: user.to_dict()
                    for user_id, user in self.users.items()
                }
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user"
    ) -> Optional[User]:
        """
        Create a new user
        
        Args:
            username: Username
            email: Email address
            password: Plain password (will be hashed)
            role: User role
            
        Returns:
            Created user or None if failed
        """
        try:
            # Check if username exists
            if any(u.username == username for u in self.users.values()):
                logger.warning(f"Username already exists: {username}")
                return None
            
            # Generate user ID
            user_id = secrets.token_urlsafe(16)
            
            # Create user
            user = User(user_id, username, email, role)
            
            # Store password hash (in production, use proper password hashing like bcrypt)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user._password_hash = password_hash
            
            self.users[user_id] = user
            self._save_users()
            
            logger.info(f"Created user: {username} ({user_id})")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def authenticate(self, username: str, password: str) -> Optional[Session]:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Session if authenticated, None otherwise
        """
        try:
            # Find user
            user = next(
                (u for u in self.users.values() if u.username == username),
                None
            )
            
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"User inactive: {username}")
                return None
            
            # Verify password (in production, use proper comparison)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if getattr(user, '_password_hash', None) != password_hash:
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            session = Session(session_id, user.user_id, expires_at)
            self.sessions[session_id] = session
            
            # Update last login
            user.last_login = datetime.now().isoformat()
            self._save_users()
            
            logger.info(f"User authenticated: {username}")
            return session
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """
        Validate session and return user
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            User if session is valid, None otherwise
        """
        session = self.sessions.get(session_id)
        
        if not session or not session.is_valid():
            if session:
                del self.sessions[session_id]
            return None
        
        # Refresh session
        session.refresh()
        
        # Get user
        user = self.users.get(session.user_id)
        return user if user and user.is_active else None
    
    def logout(self, session_id: str) -> bool:
        """
        Logout user by removing session
        
        Args:
            session_id: Session ID to remove
            
        Returns:
            True if logged out
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"User logged out: {session_id}")
            return True
        return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def list_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._save_users()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            
            # Remove user sessions
            to_remove = [
                sid for sid, session in self.sessions.items()
                if session.user_id == user_id
            ]
            for sid in to_remove:
                del self.sessions[sid]
            
            logger.info(f"Deleted user: {user_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired = [
            sid for sid, session in self.sessions.items()
            if not session.is_valid()
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


# Global instance
_auth_manager = None


def get_auth_manager() -> AuthManager:
    """Get or create global auth manager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager

