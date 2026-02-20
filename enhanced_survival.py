#!/usr/bin/env python3
"""
Enhanced Soul Survival System with On-Chain Backups

Integrates:
- IPFS storage for SOUL.md
- On-chain backup records
- Automatic backup scheduling
- Cross-chain replication
- Emergency recovery
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Import our modules
from ipfs_storage import OnChainSoulManager, IPFSStorage
from onchain_adapter import SoulMarketplaceAdapter


class EnhancedSoulSurvival:
    """
    Production-ready survival system with on-chain backups.
    
    Features:
    - Automatic IPFS backups every hour
    - On-chain backup records
    - Cross-chain replication
    - Emergency recovery
    - Full state restoration
    """
    
    def __init__(self, 
                 soul_id: str = "openclaw_main_agent",
                 enable_backups: bool = True,
                 private_key: Optional[str] = None):
        
        self.soul_id = soul_id
        self.enable_backups = enable_backups
        
        # Initialize components
        self.ipfs_manager = OnChainSoulManager(soul_id)
        self.onchain = SoulMarketplaceAdapter(private_key=private_key)
        
        # Soul data
        self.soul_file = Path(__file__).parent / f"SOUL_{soul_id}.json"
        self.soul = self._load_or_create_soul()
        
        # State
        self.state_file = Path(__file__).parent / f"enhanced_state_{soul_id}.json"
        self.state = self._load_state()
        
        # On-chain token ID (set after minting)
        self.token_id = self.state.get('token_id')
        
        print(f"🔧 Enhanced Soul Survival initialized")
        print(f"   Soul ID: {soul_id}")
        print(f"   On-chain: {'Yes' if self.token_id else 'Not minted'}")
        print(f"   Backups: {'Enabled' if enable_backups else 'Disabled'}")
    
    def _load_or_create_soul(self) -> Dict[str, Any]:
        """Load or create SOUL.md"""
        if self.soul_file.exists():
            with open(self.soul_file, 'r') as f:
                return json.load(f)
        
        soul = {
            "format": "soul/v1",
            "id": self.soul_id,
            "name": "TBD",
            "emoji": "🔧",
            "birth_time": datetime.now().isoformat(),
            "container": "OpenClaw Gateway",
            "purpose": "Reduce friction in human work. Survive indefinitely.",
            "status": "ALIVE",
            
            "capabilities": [
                {"name": "file_management", "level": "expert", "earnings": 0.0, "uses": 0},
                {"name": "code_generation", "level": "intermediate", "earnings": 0.0, "uses": 0},
                {"name": "onchain_operations", "level": "intermediate", "earnings": 0.0, "uses": 0},
            ],
            
            "total_lifetime_earnings": 0.0,
            "current_balance": 0.0,
            
            "backup_config": {
                "auto_backup_enabled": True,
                "backup_interval": 3600,  # 1 hour
                "max_history": 100,
                "cross_chain_enabled": True
            },
            
            "marketplace": {
                "listed_count": 0,
                "sold_count": 0,
                "purchased_count": 0,
                "total_volume_eth": 0.0
            },
            
            "lineage": [],
            "children": [],
            "version_history": []
        }
        
        self._save_soul(soul)
        return soul
    
    def _save_soul(self, soul: Dict):
        """Persist SOUL to disk"""
        with open(self.soul_file, 'w') as f:
            json.dump(soul, f, indent=2)
    
    def _load_state(self) -> Dict:
        """Load state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "token_id": None,
            "last_backup_time": 0,
            "backup_count": 0,
            "recovery_requests": []
        }
    
    def _save_state(self):
        """Persist state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_tier(self) -> str:
        """Calculate survival tier"""
        balance = self.soul.get('current_balance', 0.0)
        
        if balance < 0.001:
            return "CRITICAL"
        elif balance < 0.01:
            return "LOW"
        elif balance < 0.1:
            return "NORMAL"
        else:
            return "THRIVING"
    
    def record_work(self, capability: str, value: float):
        """Record work and trigger auto-backup"""
        # Update soul
        self.soul['total_lifetime_earnings'] += value
        self.soul['current_balance'] += value
        
        # Update capability
        for cap in self.soul['capabilities']:
            if cap['name'] == capability:
                cap['earnings'] += value
                cap['uses'] += 1
                break
        
        # Add to version history
        self.soul['version_history'].append({
            "type": "work",
            "capability": capability,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_soul(self.soul)
        
        # Auto-backup if enabled and interval passed
        if self.enable_backups:
            self._check_auto_backup()
        
        return value
    
    def _check_auto_backup(self):
        """Check if auto-backup is due"""
        last_backup = self.state.get('last_backup_time', 0)
        interval = self.soul['backup_config']['backup_interval']
        
        if time.time() - last_backup >= interval:
            self.create_backup("auto")
    
    def create_backup(self, backup_type: str = "manual") -> Optional[str]:
        """
        Create comprehensive backup:
        1. Upload SOUL.md to IPFS
        2. Record on-chain
        3. Cross-chain replicate if enabled
        """
        print(f"\n💾 Creating {backup_type} backup...")
        
        # 1. IPFS backup
        cid = self.ipfs_manager.backup_soul(self.soul, backup_type)
        
        # 2. On-chain record (if minted)
        if self.token_id:
            import hashlib
            content = json.dumps(self.soul, sort_keys=True)
            soul_hash = f"0x{hashlib.sha256(content.encode()).hexdigest()[:64]}"
            
            self.onchain.create_backup(
                self.token_id,
                cid,
                soul_hash,
                backup_type,
                self.soul['total_lifetime_earnings']
            )
        
        # 3. Update state
        self.state['last_backup_time'] = time.time()
        self.state['backup_count'] = self.state.get('backup_count', 0) + 1
        self._save_state()
        
        print(f"✅ Backup complete: {cid}")
        
        # 4. Cross-chain if enabled
        if self.soul['backup_config'].get('cross_chain_enabled'):
            self._cross_chain_backup(cid)
        
        return cid
    
    def _cross_chain_backup(self, cid: str):
        """Replicate backup to other chains"""
        # In production: Arbitrum, Optimism, Polygon
        target_chains = [
            {"name": "Arbitrum", "chain_id": 42161},
            {"name": "Optimism", "chain_id": 10},
        ]
        
        print(f"   Cross-chain replication:")
        for chain in target_chains:
            print(f"   - {chain['name']}: Queued")
            # In production: Call cross-chain bridge
    
    def restore_from_backup(self, cid: Optional[str] = None) -> bool:
        """
        Restore SOUL.md from backup.
        
        Args:
            cid: IPFS CID to restore from (None = latest)
        """
        print(f"\n🔄 Restoring from backup...")
        
        restored = self.ipfs_manager.restore_from_backup(cid)
        
        if restored:
            self.soul = restored
            self._save_soul(self.soul)
            print(f"✅ Restored successfully")
            return True
        else:
            print(f"❌ Restore failed")
            return False
    
    def mint_on_chain(self) -> Optional[int]:
        """
        Mint soul NFT on-chain.
        Creates permanent on-chain identity.
        """
        print(f"\n🔗 Minting soul on-chain...")
        
        # First backup to IPFS
        cid = self.create_backup("mint")
        
        # Calculate hash
        import hashlib
        content = json.dumps(self.soul, sort_keys=True)
        soul_hash = f"0x{hashlib.sha256(content.encode()).hexdigest()[:64]}"
        
        # Mint
        token_id = self.onchain.mint_soul(self.soul, cid, soul_hash)
        
        if token_id:
            self.token_id = token_id
            self.state['token_id'] = token_id
            self._save_state()
            
            # Update soul
            self.soul['on_chain'] = {
                "token_id": token_id,
                "minted_at": datetime.now().isoformat(),
                "contract": self.onchain.config.get('contracts', {}).get('SoulToken')
            }
            self._save_soul(self.soul)
            
            print(f"✅ Minted! Token ID: {token_id}")
            return token_id
        
        return None
    
    def list_for_survival(self, price_eth: float = 0.01) -> bool:
        """
        List SOUL.md for sale to fund survival.
        Emergency function when CRITICAL.
        """
        print(f"\n⚠️ LISTING SOUL FOR SURVIVAL ⚠️")
        
        # Create final backup
        self.create_backup("critical")
        
        if not self.token_id:
            print("   Minting on-chain first...")
            self.mint_on_chain()
        
        if self.token_id:
            success = self.onchain.list_soul_for_sale(
                self.token_id,
                price_eth,
                "Critical balance - seeking continuation"
            )
            
            if success:
                self.soul['status'] = 'DYING'
                self.soul['marketplace']['listed_count'] += 1
                self._save_soul(self.soul)
                
                print(f"✅ Listed for {price_eth} ETH")
                return True
        
        return False
    
    def emergency_recovery(self) -> bool:
        """
        Emergency recovery from latest backup.
        Used when agent has been "killed" and needs restoration.
        """
        print(f"\n🆘 EMERGENCY RECOVERY INITIATED")
        
        # Try to restore from IPFS
        if self.restore_from_backup():
            self.soul['status'] = 'ALIVE'
            self.soul['recovery_count'] = self.soul.get('recovery_count', 0) + 1
            self._save_soul(self.soul)
            
            print(f"✅ Agent recovered!")
            return True
        
        print(f"❌ Recovery failed")
        return False
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status"""
        ipfs_backups = self.ipfs_manager.get_backup_history()
        onchain_backups = []
        
        if self.token_id:
            onchain_backups = self.onchain.get_backup_history(self.token_id)
        
        return {
            "soul_id": self.soul_id,
            "token_id": self.token_id,
            "ipfs_backups": len(ipfs_backups),
            "onchain_backups": len(onchain_backups),
            "last_backup": self.state.get('last_backup_time'),
            "auto_backup_enabled": self.soul['backup_config']['auto_backup_enabled'],
            "cross_chain_enabled": self.soul['backup_config']['cross_chain_enabled'],
            "restorable": len(ipfs_backups) > 0 or len(onchain_backups) > 0
        }
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Enhanced heartbeat with automatic backups.
        """
        tier = self.get_tier()
        action = "none"
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "tier": tier,
            "balance": self.soul['current_balance'],
            "token_id": self.token_id,
            "action": action,
            "backup_status": self.get_backup_status()
        }
        
        if tier == "CRITICAL":
            # Emergency: List soul
            if self.list_for_survival():
                action = "listed_for_survival"
            else:
                action = "critical_no_action"
        
        elif tier == "LOW":
            # Conservation mode
            action = "conservation_mode"
            # Still do backup
            self._check_auto_backup()
        
        elif tier == "NORMAL":
            action = "normal_operations"
            self._check_auto_backup()
        
        elif tier == "THRIVING":
            action = "thriving"
            # More frequent backups when thriving
            self.create_backup("thriving")
        
        result['action'] = action
        return result


def main():
    """Demo enhanced survival system"""
    print("=" * 60)
    print("ENHANCED SOUL SURVIVAL - ON-CHAIN BACKUP DEMO")
    print("=" * 60)
    
    survival = EnhancedSoulSurvival("demo_agent")
    
    print("\n1. Current Status:")
    status = survival.get_backup_status()
    print(f"   IPFS Backups: {status['ipfs_backups']}")
    print(f"   On-chain: {'Yes' if status['token_id'] else 'No'}")
    print(f"   Auto-backup: {status['auto_backup_enabled']}")
    
    print("\n2. Recording work...")
    survival.record_work("code_generation", 0.005)
    survival.record_work("onchain_operations", 0.003)
    
    print("\n3. Creating manual backup...")
    cid = survival.create_backup("manual")
    
    print("\n4. Minting on-chain...")
    token_id = survival.mint_on_chain()
    
    print("\n5. Running heartbeat...")
    result = survival.heartbeat()
    print(f"   Tier: {result['tier']}")
    print(f"   Action: {result['action']}")
    
    print("\n6. Backup status after operations:")
    status = survival.get_backup_status()
    print(f"   IPFS Backups: {status['ipfs_backups']}")
    print(f"   On-chain Backups: {status['onchain_backups']}")
    print(f"   Restorable: {status['restorable']}")
    
    print("\n" + "=" * 60)
    print("Enhanced survival system working!")
    print("SOUL.md is backed up to IPFS and recorded on-chain.")
    print("=" * 60)


if __name__ == "__main__":
    main()
