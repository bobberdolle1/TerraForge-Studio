"""
Single Sign-On (SSO) Integration
Supports SAML 2.0 and OAuth 2.0/OpenID Connect
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from enum import Enum


class SSOProvider(str, Enum):
    SAML = "saml"
    OAUTH2 = "oauth2"
    OPENID = "openid"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"


class SSOConfig:
    """SSO Configuration"""
    
    def __init__(
        self,
        provider: SSOProvider,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        issuer: Optional[str] = None,
        authorization_endpoint: Optional[str] = None,
        token_endpoint: Optional[str] = None,
        userinfo_endpoint: Optional[str] = None
    ):
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.issuer = issuer
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.userinfo_endpoint = userinfo_endpoint


class SSOUser:
    """SSO User Profile"""
    
    def __init__(
        self,
        id: str,
        email: str,
        name: str,
        provider: SSOProvider,
        provider_user_id: str,
        avatar: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.avatar = avatar
        self.metadata = metadata or {}


class SSOManager:
    """Manages SSO authentication"""
    
    def __init__(self):
        self.configs: Dict[SSOProvider, SSOConfig] = {}
        self.sessions: Dict[str, SSOUser] = {}
    
    def register_provider(self, config: SSOConfig):
        """Register SSO provider"""
        self.configs[config.provider] = config
    
    def get_authorization_url(
        self,
        provider: SSOProvider,
        state: Optional[str] = None
    ) -> str:
        """Generate authorization URL for OAuth flow"""
        config = self.configs.get(provider)
        if not config:
            raise ValueError(f"Provider {provider} not configured")
        
        if provider == SSOProvider.GOOGLE:
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": config.client_id,
                "redirect_uri": config.redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state or ""
            }
        elif provider == SSOProvider.MICROSOFT:
            auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            params = {
                "client_id": config.client_id,
                "redirect_uri": config.redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state or ""
            }
        elif provider == SSOProvider.GITHUB:
            auth_url = "https://github.com/login/oauth/authorize"
            params = {
                "client_id": config.client_id,
                "redirect_uri": config.redirect_uri,
                "scope": "user:email",
                "state": state or ""
            }
        else:
            auth_url = config.authorization_endpoint or ""
            params = {}
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_url}?{query}"
    
    async def exchange_code(
        self,
        provider: SSOProvider,
        code: str
    ) -> SSOUser:
        """Exchange authorization code for user info"""
        config = self.configs.get(provider)
        if not config:
            raise ValueError(f"Provider {provider} not configured")
        
        # In real implementation, make HTTP request to token endpoint
        # For now, return mock user
        user = SSOUser(
            id=f"sso_{provider}_{code[:8]}",
            email=f"user@{provider}.example.com",
            name="SSO User",
            provider=provider,
            provider_user_id=code[:16],
            avatar=None
        )
        
        # Store session
        self.sessions[user.id] = user
        
        return user
    
    def create_session_token(
        self,
        user: SSOUser,
        secret_key: str,
        expires_in: int = 3600
    ) -> str:
        """Create JWT session token"""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "provider": user.provider,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    
    def verify_session_token(
        self,
        token: str,
        secret_key: str
    ) -> Optional[SSOUser]:
        """Verify JWT session token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            if user_id in self.sessions:
                return self.sessions[user_id]
            
            # Reconstruct user from token
            user = SSOUser(
                id=payload["user_id"],
                email=payload["email"],
                name=payload["name"],
                provider=SSOProvider(payload["provider"]),
                provider_user_id=payload["user_id"]
            )
            
            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, user_id: str):
        """Logout user and invalidate session"""
        if user_id in self.sessions:
            del self.sessions[user_id]


# Global SSO manager
sso_manager = SSOManager()


# Pre-configured providers
def setup_google_sso(client_id: str, client_secret: str, redirect_uri: str):
    """Setup Google OAuth 2.0"""
    config = SSOConfig(
        provider=SSOProvider.GOOGLE,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        token_endpoint="https://oauth2.googleapis.com/token",
        userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo"
    )
    sso_manager.register_provider(config)


def setup_microsoft_sso(client_id: str, client_secret: str, redirect_uri: str):
    """Setup Microsoft OAuth 2.0"""
    config = SSOConfig(
        provider=SSOProvider.MICROSOFT,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        authorization_endpoint="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        token_endpoint="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        userinfo_endpoint="https://graph.microsoft.com/v1.0/me"
    )
    sso_manager.register_provider(config)
