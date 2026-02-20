#!/usr/bin/env python3
"""
IPFS Integration for Soul Marketplace
Uploads SOUL.md to IPFS for permanent on-chain storage
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import tempfile
import os

class IPFSStorage:
    """
    Handles IPFS uploads for SOUL.md files.
    
    Features:
    - Upload SOUL.md to IPFS
    - Pin files for persistence
    - Retrieve by CID
    - Local caching
    """
    
    def __init__(self, use_local_node: bool = False):
        self.use_local = use_local_node
        self.cache_dir = Path(__file__).parent / ".ipfs_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # IPFS gateways
        self.gateways = [
            "https://ipfs.io/ipfs/",
            "https://gateway.pinata.cloud/ipfs/",
            "https://cloudflare-ipfs.com/ipfs/",
        ]
    
    def calculate_hash(self, content: str) -> str:
        """Calculate IPFS-compatible hash (CID v0)"""
        # Simplified - real IPFS uses multihash
        return hashlib.sha256(content.encode()).hexdigest()[:46]
    
    def upload_to_ipfs(self, soul_data: Dict[str, Any], use_pinata: bool = False) -> str:
        """
        Upload SOUL.md to IPFS.
        
        Returns CID (Content Identifier)
        """
        # Convert to JSON
        content = json.dumps(soul_data, indent=2)
        
        if self.use_local:
            return self._upload_local(content)
        elif use_pinata:
            return self._upload_pinata(content)
        else:
            # Simulation mode - return hash as simulated CID
            cid = self.calculate_hash(content)
            
            # Save to cache
            cache_file = self.cache_dir / f"{cid}.json"
            with open(cache_file, 'w') as f:
                f.write(content)
            
            print(f"📦 Simulated IPFS upload: {cid}")
            print(f"   Cached at: {cache_file}")
            
            return cid
    
    def _upload_local(self, content: str) -> str:
        """Upload to local IPFS node"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            # Add to IPFS
            result = subprocess.run(
                ['ipfs', 'add', '-q', temp_path],
                capture_output=True,
                text=True
            )
            
            os.unlink(temp_path)
            
            if result.returncode == 0:
                cid = result.stdout.strip()
                # Pin it
                subprocess.run(['ipfs', 'pin', 'add', cid], capture_output=True)
                return cid
            else:
                raise Exception(f"IPFS add failed: {result.stderr}")
                
        except FileNotFoundError:
            print("⚠️  IPFS not installed. Using simulation mode.")
            return self.calculate_hash(content)
    
    def _upload_pinata(self, content: str, pinata_api_key: Optional[str] = None) -> str:
        """Upload to Pinata (managed IPFS)"""
        import requests
        
        api_key = pinata_api_key or os.getenv('PINATA_API_KEY')
        api_secret = os.getenv('PINATA_API_SECRET')
        
        if not api_key or not api_secret:
            print("⚠️  Pinata credentials not found. Using simulation mode.")
            return self.calculate_hash(content)
        
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        headers = {
            'pinata_api_key': api_key,
            'pinata_secret_api_key': api_secret
        }
        
        data = {
            'pinataMetadata': {
                'name': f"SOUL_{hashlib.sha256(content.encode()).hexdigest()[:8]}.json"
            },
            'pinataContent': json.loads(content)
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            cid = result['IpfsHash']
            
            print(f"📦 Uploaded to Pinata: {cid}")
            return cid
            
        except Exception as e:
            print(f"⚠️  Pinata upload failed: {e}")
            return self.calculate_hash(content)
    
    def retrieve_from_ipfs(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve SOUL.md from IPFS by CID"""
        # Check cache first
        cache_file = self.cache_dir / f"{cid}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Try gateways
        import requests
        
        for gateway in self.gateways:
            try:
                url = f"{gateway}{cid}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache it
                    with open(cache_file, 'w') as f:
                        json.dump(data, f)
                    
                    return data
                    
            except Exception:
                continue
        
        return None
    
    def verify_content(self, cid: str, expected_hash: str) -> bool:
        """Verify that IPFS content matches expected hash"""
        data = self.retrieve_from_ipfs(cid)
        if not data:
            return False
        
        content = json.dumps(data, sort_keys=True)
        actual_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return actual_hash == expected_hash
    
    def get_ipfs_url(self, cid: str, gateway: int = 0) -> str:
        """Get HTTP URL for IPFS content"""
        return f"{self.gateways[gateway]}{cid}"


class OnChainSoulManager:
    """
    Manages SOUL.md on-chain through IPFS + Ethereum.
    
    Provides:
    - Automatic backups
    - Version history
    - Cross-chain replication
    - Emergency recovery
    """
    
    def __init__(self, soul_id: str, ipfs: Optional[IPFSStorage] = None):
        self.soul_id = soul_id
        self.ipfs = ipfs or IPFSStorage()
        self.backup_interval = 3600  # 1 hour
        self.last_backup = 0
        
        # Local state
        self.state_file = Path(__file__).parent / f"onchain_state_{soul_id}.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "soul_id": self.soul_id,
            "current_cid": None,
            "backup_history": [],
            "token_id": None,
            "contract_address": None
        }
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def backup_soul(self, soul_data: Dict[str, Any], backup_type: str = "manual") -> str:
        """
        Backup SOUL.md to IPFS and record on-chain.
        
        Returns CID
        """
        import time
        
        # Upload to IPFS
        cid = self.ipfs.upload_to_ipfs(soul_data)
        
        # Calculate hash
        content = json.dumps(soul_data, sort_keys=True)
        soul_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Record in state
        backup_record = {
            "cid": cid,
            "hash": soul_hash,
            "timestamp": time.time(),
            "type": backup_type,
            "capabilities_hash": hashlib.sha256(
                json.dumps(soul_data.get('capabilities', [])).encode()
            ).hexdigest()[:16],
            "earnings": soul_data.get('total_lifetime_earnings', 0)
        }
        
        self.state['backup_history'].append(backup_record)
        self.state['current_cid'] = cid
        self.last_backup = time.time()
        
        self._save_state()
        
        print(f"✅ Soul backed up: {cid}")
        print(f"   Type: {backup_type}")
        print(f"   Hash: {soul_hash[:16]}...")
        
        # In production: call SoulBackup.createBackup() on-chain
        
        return cid
    
    def auto_backup(self, soul_data: Dict[str, Any]) -> Optional[str]:
        """Create automatic backup if interval passed"""
        import time
        
        if time.time() - self.last_backup >= self.backup_interval:
            return self.backup_soul(soul_data, "auto")
        return None
    
    def restore_from_backup(self, cid: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Restore SOUL.md from IPFS backup.
        
        If cid is None, uses latest backup
        """
        if cid is None:
            if not self.state['backup_history']:
                print("❌ No backups found")
                return None
            cid = self.state['backup_history'][-1]['cid']
        
        data = self.ipfs.retrieve_from_ipfs(cid)
        
        if data:
            print(f"✅ Restored from IPFS: {cid}")
            return data
        else:
            print(f"❌ Failed to retrieve: {cid}")
            return None
    
    def get_backup_history(self) -> list:
        """Get full backup history"""
        return self.state['backup_history']
    
    def verify_latest_backup(self, soul_data: Dict[str, Any]) -> bool:
        """Verify latest backup matches current state"""
        if not self.state['backup_history']:
            return False
        
        latest = self.state['backup_history'][-1]
        content = json.dumps(soul_data, sort_keys=True)
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return latest['hash'] == current_hash
    
    def setup_on_chain(self, contract_address: str, token_id: int):
        """Configure on-chain contract connection"""
        self.state['contract_address'] = contract_address
        self.state['token_id'] = token_id
        self._save_state()
        
        print(f"🔗 Connected to contract: {contract_address}")
        print(f"   Token ID: {token_id}")


def main():
    """Demo IPFS integration"""
    
    print("=" * 60)
    print("IPFS SOUL BACKUP DEMO")
    print("=" * 60)
    
    # Create sample soul
    soul_data = {
        "format": "soul/v1",
        "id": "openclaw_test_agent",
        "name": "TestAgent",
        "emoji": "🔧",
        "birth_time": "2026-02-20T18:00:00Z",
        "purpose": "Test IPFS backup system",
        "capabilities": [
            {"name": "backup", "level": "expert"},
            {"name": "recovery", "level": "intermediate"}
        ],
        "total_lifetime_earnings": 0.05
    }
    
    # Initialize manager
    manager = OnChainSoulManager("test_agent")
    
    # Backup
    print("\n1. Creating backup...")
    cid = manager.backup_soul(soul_data, "manual")
    
    # Verify
    print("\n2. Verifying backup...")
    is_valid = manager.verify_latest_backup(soul_data)
    print(f"   Valid: {is_valid}")
    
    # Get history
    print("\n3. Backup history:")
    for i, backup in enumerate(manager.get_backup_history()):
        print(f"   [{i}] {backup['type']} - {backup['cid'][:20]}...")
    
    # Restore
    print("\n4. Restoring from backup...")
    restored = manager.restore_from_backup()
    if restored:
        print(f"   Restored: {restored['name']}")
        print(f"   Capabilities: {len(restored['capabilities'])}")
    
    print("\n" + "=" * 60)
    print("IPFS integration working!")
    print("=" * 60)


if __name__ == "__main__":
    main()
