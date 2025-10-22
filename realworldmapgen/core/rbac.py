"""
Role-Based Access Control (RBAC) System
Enterprise-grade permission management
"""

from enum import Enum
from typing import List, Optional, Set
from datetime import datetime
from pydantic import BaseModel


class Permission(str, Enum):
    # Terrain permissions
    TERRAIN_VIEW = "terrain:view"
    TERRAIN_CREATE = "terrain:create"
    TERRAIN_EDIT = "terrain:edit"
    TERRAIN_DELETE = "terrain:delete"
    TERRAIN_EXPORT = "terrain:export"
    
    # Project permissions
    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"
    PROJECT_SHARE = "project:share"
    
    # User permissions
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    
    # Admin permissions
    ADMIN_FULL = "admin:full"
    ANALYTICS_VIEW = "analytics:view"
    SETTINGS_EDIT = "settings:edit"


class Role(str, Enum):
    VIEWER = "viewer"
    CREATOR = "creator"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


class RoleDefinition(BaseModel):
    name: Role
    permissions: Set[Permission]
    description: str


# Role definitions
ROLE_PERMISSIONS = {
    Role.VIEWER: RoleDefinition(
        name=Role.VIEWER,
        permissions={
            Permission.TERRAIN_VIEW,
            Permission.PROJECT_VIEW,
        },
        description="Can view terrains and projects"
    ),
    Role.CREATOR: RoleDefinition(
        name=Role.CREATOR,
        permissions={
            Permission.TERRAIN_VIEW,
            Permission.TERRAIN_CREATE,
            Permission.TERRAIN_EXPORT,
            Permission.PROJECT_VIEW,
            Permission.PROJECT_CREATE,
        },
        description="Can create and export terrains"
    ),
    Role.EDITOR: RoleDefinition(
        name=Role.EDITOR,
        permissions={
            Permission.TERRAIN_VIEW,
            Permission.TERRAIN_CREATE,
            Permission.TERRAIN_EDIT,
            Permission.TERRAIN_EXPORT,
            Permission.PROJECT_VIEW,
            Permission.PROJECT_CREATE,
            Permission.PROJECT_EDIT,
            Permission.PROJECT_SHARE,
        },
        description="Can create and edit terrains and projects"
    ),
    Role.ADMIN: RoleDefinition(
        name=Role.ADMIN,
        permissions={
            Permission.TERRAIN_VIEW,
            Permission.TERRAIN_CREATE,
            Permission.TERRAIN_EDIT,
            Permission.TERRAIN_DELETE,
            Permission.TERRAIN_EXPORT,
            Permission.PROJECT_VIEW,
            Permission.PROJECT_CREATE,
            Permission.PROJECT_EDIT,
            Permission.PROJECT_DELETE,
            Permission.PROJECT_SHARE,
            Permission.USER_VIEW,
            Permission.USER_CREATE,
            Permission.USER_EDIT,
            Permission.ANALYTICS_VIEW,
            Permission.SETTINGS_EDIT,
        },
        description="Full access except ownership transfer"
    ),
    Role.OWNER: RoleDefinition(
        name=Role.OWNER,
        permissions=set(Permission),
        description="Full system access including ownership"
    ),
}


class UserRole(BaseModel):
    user_id: str
    role: Role
    scope: Optional[str] = None  # project_id, organization_id, etc.
    granted_by: Optional[str] = None
    granted_at: datetime = datetime.now()
    expires_at: Optional[datetime] = None


class RBACManager:
    """Manages role-based access control"""
    
    def __init__(self):
        self.user_roles: dict[str, List[UserRole]] = {}
        self.custom_permissions: dict[str, Set[Permission]] = {}
    
    def assign_role(
        self,
        user_id: str,
        role: Role,
        scope: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign a role to a user"""
        user_role = UserRole(
            user_id=user_id,
            role=role,
            scope=scope,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        self.user_roles[user_id].append(user_role)
        return user_role
    
    def revoke_role(
        self,
        user_id: str,
        role: Role,
        scope: Optional[str] = None
    ) -> bool:
        """Revoke a role from a user"""
        if user_id not in self.user_roles:
            return False
        
        initial_len = len(self.user_roles[user_id])
        self.user_roles[user_id] = [
            ur for ur in self.user_roles[user_id]
            if not (ur.role == role and ur.scope == scope)
        ]
        
        return len(self.user_roles[user_id]) < initial_len
    
    def get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get all roles for a user"""
        return self.user_roles.get(user_id, [])
    
    def get_user_permissions(
        self,
        user_id: str,
        scope: Optional[str] = None
    ) -> Set[Permission]:
        """Get all permissions for a user in a given scope"""
        permissions: Set[Permission] = set()
        
        for user_role in self.get_user_roles(user_id):
            # Check if role is expired
            if user_role.expires_at and user_role.expires_at < datetime.now():
                continue
            
            # Check scope match
            if scope and user_role.scope and user_role.scope != scope:
                continue
            
            # Add role permissions
            role_def = ROLE_PERMISSIONS[user_role.role]
            permissions.update(role_def.permissions)
        
        # Add custom permissions
        if user_id in self.custom_permissions:
            permissions.update(self.custom_permissions[user_id])
        
        return permissions
    
    def has_permission(
        self,
        user_id: str,
        permission: Permission,
        scope: Optional[str] = None
    ) -> bool:
        """Check if user has a specific permission"""
        permissions = self.get_user_permissions(user_id, scope)
        return permission in permissions or Permission.ADMIN_FULL in permissions
    
    def grant_custom_permission(
        self,
        user_id: str,
        permission: Permission
    ):
        """Grant a custom permission to a user"""
        if user_id not in self.custom_permissions:
            self.custom_permissions[user_id] = set()
        self.custom_permissions[user_id].add(permission)
    
    def revoke_custom_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> bool:
        """Revoke a custom permission from a user"""
        if user_id in self.custom_permissions:
            self.custom_permissions[user_id].discard(permission)
            return True
        return False


# Global RBAC manager instance
rbac_manager = RBACManager()


def require_permission(permission: Permission):
    """Decorator to require a specific permission"""
    def decorator(func):
        async def wrapper(*args, user_id: str = None, scope: str = None, **kwargs):
            if not user_id:
                raise PermissionError("User ID required")
            
            if not rbac_manager.has_permission(user_id, permission, scope):
                raise PermissionError(
                    f"User {user_id} does not have permission {permission}"
                )
            
            return await func(*args, user_id=user_id, scope=scope, **kwargs)
        return wrapper
    return decorator
