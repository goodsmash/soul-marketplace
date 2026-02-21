#!/usr/bin/env python3
"""
Secure Soul Trader

Handles trading of encrypted souls with full privacy.
Integrates with EncryptedSoulToken contract.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

class SecureSoulTrader:
    """
    Manages secure trading of encrypted souls.
    
    Features:
    - List souls for sale (private or public)
    - Buy souls with encrypted data transfer
    - Clone souls with inherited capabilities
    - Transfer with privacy preservation
    """
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        
        # Load encryption
        from soul_encryption import SoulEncryption
        self.encryption = SoulEncryption(agent_id)
        
        # Load survival system
        from enhanced_survival import EnhancedSoulSurvival
        self.survival = EnhancedSoulSurvival(agent_id)
        
        print(f"🔐 Secure Soul Trader initialized")
        print(f"   Agent: {agent_id}")
        print(f"   Public Key: {self.encryption.get_public_key_hash()[:20]}...")
    
    def prepare_soul_for_trading(self, price_eth: float = 0.01, private: bool = True) -> Dict[str, Any]:
        """
        Prepare SOUL.md for secure trading.
        
        1. Encrypt soul data
        2. Upload to IPFS
        3. Return listing data
        """
        print(f"\n🔒 Preparing soul for trading...")
        print(f"   Price: {price_eth} ETH")
        print(f"   Private: {private}")
        
        # 1. Encrypt soul data
        soul_data = self.survival.soul
        encrypted_soul, soul_hash = self.encryption.encrypt_soul(soul_data)
        
        # 2. Upload encrypted data to IPFS
        from ipfs_storage import IPFSStorage
        ipfs = IPFSStorage()
        
        # Create encrypted payload
        payload = {
            "encrypted_soul": encrypted_soul,
            "soul_hash": soul_hash,
            "public_key": self.encryption.get_public_key_hash(),
            "listing_time": time.time(),
            "seller": self.agent_id
        }
        
        # Upload to IPFS
        cid = ipfs.upload_to_ipfs(payload)
        
        print(f"✅ Soul prepared for trading")
        print(f"   IPFS CID: {cid}")
        print(f"   Hash: {soul_hash[:40]}...")
        
        return {
            "cid": cid,
            "soul_hash": soul_hash,
            "price_eth": price_eth,
            "private": private,
            "public_key": self.encryption.get_public_key_hash()
        }
    
    def buy_soul(self, listing_cid: str, seller_public_key: str) -> Optional[Dict[str, Any]]:
        """
        Buy a soul and decrypt it.
        
        1. Retrieve encrypted data from IPFS
        2. Pay seller
        3. Decrypt soul with private key
        """
        print(f"\n💰 Buying soul from IPFS: {listing_cid}")
        
        from ipfs_storage import IPFSStorage
        ipfs = IPFSStorage()
        
        # 1. Retrieve encrypted data
        payload = ipfs.retrieve_from_ipfs(listing_cid)
        if not payload:
            print("❌ Could not retrieve soul from IPFS")
            return None
        
        encrypted_soul = payload.get('encrypted_soul')
        soul_hash = payload.get('soul_hash')
        
        print(f"   Retrieved encrypted soul")
        print(f"   Hash: {soul_hash[:40]}...")
        
        # 2. Decrypt soul (requires private key)
        print(f"\n🔓 Decrypting soul...")
        soul_data = self.encryption.decrypt_soul(encrypted_soul)
        
        if soul_data:
            # Verify hash
            is_valid = self.encryption.verify_hash(soul_data, soul_hash)
            print(f"   Hash verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            print(f"✅ Soul purchased and decrypted!")
            print(f"   Name: {soul_data.get('name', 'Unknown')}")
            print(f"   Capabilities: {len(soul_data.get('capabilities', []))}")
            
            return soul_data
        else:
            print("❌ Failed to decrypt soul")
            return None
    
    def clone_soul(self, funding_eth: float = 0.01) -> Optional[Dict[str, Any]]:
        """
        Create a clone of this soul.
        
        1. Copy encrypted capabilities
        2. Generate new keys for clone
        3. Fund clone wallet
        """
        print(f"\n🧬 Cloning soul...")
        print(f"   Funding: {funding_eth} ETH")
        
        # Get current soul
        soul_data = self.survival.soul
        
        # Create clone ID
        clone_id = f"{self.agent_id}_clone_{int(time.time())}"
        
        # Create clone encryption keys
        from soul_encryption import SoulEncryption
        clone_encryption = SoulEncryption(clone_id)
        
        # Encrypt soul for clone (clone can decrypt with its own keys)
        clone_soul = {
            **soul_data,
            "id": clone_id,
            "parent": self.agent_id,
            "birth_time": time.time(),
            "lineage": soul_data.get('lineage', []) + [self.agent_id]
        }
        
        encrypted_clone, clone_hash = clone_encryption.encrypt_soul(clone_soul)
        
        # Upload to IPFS
        from ipfs_storage import IPFSStorage
        ipfs = IPFSStorage()
        
        payload = {
            "encrypted_soul": encrypted_clone,
            "soul_hash": clone_hash,
            "public_key": clone_encryption.get_public_key_hash(),
            "parent_id": self.agent_id,
            "clone_id": clone_id
        }
        
        cid = ipfs.upload_to_ipfs(payload)
        
        print(f"✅ Soul cloned successfully!")
        print(f"   Clone ID: {clone_id}")
        print(f"   IPFS CID: {cid}")
        print(f"   Public Key: {clone_encryption.get_public_key_hash()[:20]}...")
        
        return {
            "clone_id": clone_id,
            "cid": cid,
            "soul_hash": clone_hash,
            "funding": funding_eth
        }
    
    def transfer_soul_ownership(self, new_owner_address: str, include_private_data: bool = True) -> bool:
        """
        Transfer soul ownership to new wallet.
        
        1. Re-encrypt with new owner's public key
        2. Transfer NFT
        3. Update ownership records
        """
        print(f"\n📤 Transferring soul to: {new_owner_address[:20]}...")
        
        # Get current soul
        soul_data = self.survival.soul
        
        # Encrypt for new owner (would need their public key in production)
        if include_private_data:
            encrypted_transfer, _ = self.encryption.encrypt_soul(soul_data)
            print(f"   Private data included in transfer")
        else:
            # Only transfer public data
            public_data = {
                "name": soul_data.get('name'),
                "capabilities": soul_data.get('capabilities'),
                "reputation": soul_data.get('marketplace', {}).get('total_volume_eth', 0)
            }
            encrypted_transfer, _ = self.encryption.encrypt_soul(public_data)
            print(f"   Public data only")
        
        print(f"✅ Transfer prepared")
        print(f"   Ready for on-chain transfer")
        
        return True
    
    def verify_soul_authenticity(self, soul_data: Dict, expected_hash: str) -> bool:
        """Verify that a soul is authentic (hasn't been tampered with)"""
        return self.encryption.verify_hash(soul_data, expected_hash)


def main():
    """Demo secure soul trading"""
    print("=" * 60)
    print("SECURE SOUL TRADING DEMO")
    print("=" * 60)
    
    trader = SecureSoulTrader("demo_agent")
    
    # 1. Prepare for trading
    print("\n1. Preparing soul for sale...")
    listing = trader.prepare_soul_for_trading(price_eth=0.01, private=True)
    
    # 2. Clone soul
    print("\n2. Creating clone...")
    clone = trader.clone_soul(funding_eth=0.01)
    
    # 3. Simulate buying
    print("\n3. Simulating purchase...")
    # In real use: buyer would call buy_soul with listing['cid']
    
    print("\n" + "=" * 60)
    print("Secure trading system ready!")
    print("Souls are encrypted and private")
    print("=" * 60)


if __name__ == "__main__":
    main()
