#!/usr/bin/env python3
"""
Soul Encryption System

Encrypts SOUL.md so only the wallet owner can read it.
Uses hybrid encryption (RSA + AES) for security.
"""

import json
import base64
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Try to import cryptography
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ cryptography not installed - using simulation mode")
    print("   Install: pip install cryptography")


class SoulEncryption:
    """
    Encrypts and decrypts SOUL.md data.
    
    Features:
    - Generate wallet-specific keys
    - Encrypt SOUL.md for on-chain storage
    - Decrypt with private key
    - Share encrypted data with authorized viewers
    """
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        self.keys_dir = Path(__file__).parent / ".encryption_keys"
        self.keys_dir.mkdir(exist_ok=True)
        
        self.private_key_file = self.keys_dir / f"{agent_id}_private.pem"
        self.public_key_file = self.keys_dir / f"{agent_id}_public.pem"
        
        # Generate or load keys
        if CRYPTO_AVAILABLE:
            self.private_key, self.public_key = self._get_or_create_keys()
        else:
            self.private_key = None
            self.public_key = None
        
        print(f"🔐 Soul Encryption initialized for {agent_id}")
        if self.public_key:
            print(f"   Public key: {self.get_public_key_hash()[:20]}...")
    
    def _get_or_create_keys(self) -> Tuple[Any, Any]:
        """Generate or load RSA key pair"""
        if self.private_key_file.exists() and self.public_key_file.exists():
            # Load existing keys
            with open(self.private_key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(self.public_key_file, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            print("   Loaded existing keys")
        else:
            # Generate new keys
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Save keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(self.private_key_file, 'wb') as f:
                f.write(private_pem)
            with open(self.public_key_file, 'wb') as f:
                f.write(public_pem)
            
            # Secure private key file
            self.private_key_file.chmod(0o600)
            
            print("   Generated new RSA key pair")
        
        return private_key, public_key
    
    def get_public_key_hash(self) -> str:
        """Get hash of public key for on-chain storage"""
        if not self.public_key:
            # Simulation mode
            return hashlib.sha256(f"simulated_{self.agent_id}".encode()).hexdigest()
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(public_bytes).hexdigest()
    
    def encrypt_soul(self, soul_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Encrypt SOUL.md data.
        
        Returns:
            (encrypted_data, data_hash)
        """
        if not CRYPTO_AVAILABLE or not self.public_key:
            # Simulation mode
            soul_json = json.dumps(soul_data, sort_keys=True)
            fake_encrypted = base64.b64encode(soul_json.encode()).decode()
            data_hash = hashlib.sha256(soul_json.encode()).hexdigest()
            print(f"🔒 Simulated encryption (real encryption available with 'pip install cryptography')")
            return fake_encrypted, data_hash
        
        # Convert to JSON
        soul_json = json.dumps(soul_data, sort_keys=True)
        soul_bytes = soul_json.encode('utf-8')
        
        # Generate AES key
        aes_key = hashlib.sha256(f"{self.agent_id}_{time.time()}".encode()).digest()[:32]
        iv = hashlib.sha256(f"{self.agent_id}_iv".encode()).digest()[:16]
        
        # Encrypt with AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(soul_bytes) + encryptor.finalize()
        
        # Encrypt AES key with RSA
        encrypted_key = self.public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine: encrypted_key + iv + encrypted_data
        combined = encrypted_key + iv + encrypted_data
        encrypted_b64 = base64.b64encode(combined).decode('utf-8')
        
        # Calculate hash
        data_hash = hashlib.sha256(soul_json.encode()).hexdigest()
        
        print(f"🔒 Soul encrypted successfully")
        print(f"   Size: {len(encrypted_b64)} bytes (base64)")
        print(f"   Hash: {data_hash[:40]}...")
        
        return encrypted_b64, data_hash
    
    def decrypt_soul(self, encrypted_b64: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt SOUL.md data (owner only).
        """
        if not CRYPTO_AVAILABLE or not self.private_key:
            # Simulation mode
            try:
                soul_json = base64.b64decode(encrypted_b64).decode()
                return json.loads(soul_json)
            except:
                print("❌ Decryption failed")
                return None
        
        try:
            # Decode base64
            combined = base64.b64decode(encrypted_b64.encode('utf-8'))
            
            # Split components (RSA encrypted key is 256 bytes for 2048-bit key)
            encrypted_key = combined[:256]
            iv = combined[256:272]
            encrypted_data = combined[272:]
            
            # Decrypt AES key with RSA
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_bytes = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Parse JSON
            soul_data = json.loads(decrypted_bytes.decode('utf-8'))
            
            print(f"🔓 Soul decrypted successfully")
            return soul_data
            
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return None
    
    def encrypt_capabilities(self, capabilities: list) -> Tuple[str, str]:
        """Encrypt capabilities data"""
        return self.encrypt_soul({"capabilities": capabilities})
    
    def verify_hash(self, soul_data: Dict[str, Any], expected_hash: str) -> bool:
        """Verify that soul data matches expected hash"""
        soul_json = json.dumps(soul_data, sort_keys=True)
        actual_hash = hashlib.sha256(soul_json.encode()).hexdigest()
        return actual_hash == expected_hash
    
    def export_public_key(self) -> str:
        """Export public key for sharing"""
        if not self.public_key:
            return "simulated_public_key"
        
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_bytes.decode('utf-8')
    
    def import_public_key(self, key_pem: str) -> Any:
        """Import someone else's public key to encrypt for them"""
        if not CRYPTO_AVAILABLE:
            return None
        
        return serialization.load_pem_public_key(
            key_pem.encode(),
            backend=default_backend()
        )
    
    def encrypt_for_recipient(self, soul_data: Dict[str, Any], recipient_public_key: Any) -> str:
        """Encrypt soul data for a specific recipient (for trading)"""
        if not CRYPTO_AVAILABLE or not recipient_public_key:
            # Simulation
            return base64.b64encode(json.dumps(soul_data).encode()).decode()
        
        soul_json = json.dumps(soul_data, sort_keys=True)
        soul_bytes = soul_json.encode('utf-8')
        
        # Generate AES key
        aes_key = hashlib.sha256(f"{self.agent_id}_{time.time()}".encode()).digest()[:32]
        iv = hashlib.sha256(f"{self.agent_id}_iv".encode()).digest()[:16]
        
        # Encrypt with AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(soul_bytes) + encryptor.finalize()
        
        # Encrypt AES key with recipient's RSA key
        encrypted_key = recipient_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine
        combined = encrypted_key + iv + encrypted_data
        return base64.b64encode(combined).decode('utf-8')


def main():
    """Demo encryption system"""
    import time
    
    print("=" * 60)
    print("SOUL ENCRYPTION DEMO")
    print("=" * 60)
    
    enc = SoulEncryption("demo_agent")
    
    # Sample soul data
    soul_data = {
        "name": "TestAgent",
        "purpose": "Demonstrate encryption",
        "secrets": ["private_key_123", "api_key_456"],  # Sensitive!
        "capabilities": ["coding", "trading"]
    }
    
    print("\n1. Original soul data:")
    print(f"   Contains secrets: {bool(soul_data.get('secrets'))}")
    
    print("\n2. Encrypting...")
    encrypted, soul_hash = enc.encrypt_soul(soul_data)
    print(f"   Encrypted length: {len(encrypted)} chars")
    
    print("\n3. Verifying hash...")
    is_valid = enc.verify_hash(soul_data, soul_hash)
    print(f"   Hash valid: {is_valid}")
    
    print("\n4. Decrypting...")
    decrypted = enc.decrypt_soul(encrypted)
    if decrypted:
        print(f"   Decrypted successfully!")
        print(f"   Secrets recovered: {decrypted.get('secrets', [])}")
    
    print("\n" + "=" * 60)
    print("Encryption working!")
    print("Your SOUL.md is now protected")
    print("=" * 60)


if __name__ == "__main__":
    main()
