"""
Secure encryption for API keys and secrets
Uses Fernet (symmetric encryption) from cryptography library
"""

import os
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecretManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, key_file: Path = Path("data/.secret_key")):
        """
        Initialize secret manager.
        
        Args:
            key_file: Path to store encryption key
        """
        self.key_file = key_file
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        self._cipher = None
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b"password"))
            
            # Save securely
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (Unix)
            try:
                os.chmod(self.key_file, 0o600)
            except:
                pass  # Windows doesn't support chmod
            
            return key
    
    @property
    def cipher(self) -> Fernet:
        """Get cipher instance"""
        if self._cipher is None:
            key = self._get_or_create_key()
            self._cipher = Fernet(key)
        return self._cipher
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data.
        
        Args:
            data: Plaintext string
            
        Returns:
            Base64-encoded encrypted string
        """
        if not data:
            return ""
        
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_data:
            return ""
        
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            # If decryption fails, return empty string
            # This can happen if key changed or data corrupted
            return ""
    
    def mask_secret(self, secret: Optional[str], show_chars: int = 4) -> str:
        """
        Mask secret for display (show only last N chars).
        
        Args:
            secret: Secret to mask
            show_chars: Number of characters to show
            
        Returns:
            Masked string like "****abcd"
        """
        if not secret or len(secret) == 0:
            return ""
        
        if len(secret) <= show_chars:
            return "*" * len(secret)
        
        visible = secret[-show_chars:]
        masked = "*" * (len(secret) - show_chars)
        return f"{masked}{visible}"
    
    def is_configured(self, secret: Optional[str]) -> bool:
        """Check if secret is configured (not None and not empty)"""
        return bool(secret and len(secret) > 0)


# Global instance
secret_manager = SecretManager()

