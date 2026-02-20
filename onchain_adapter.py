#!/usr/bin/env python3
"""
On-Chain Adapter for Soul Marketplace
Connects Python agent to Ethereum smart contracts
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Optional Web3 - simulation mode works without it
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Web3 = None
    Account = None

@dataclass
class SoulData:
    """Represents a soul on-chain"""
    token_id: int
    automaton: str
    creator: str
    soul_uri: str
    soul_hash: str
    birth_time: int
    death_time: int
    listing_price: int
    status: str

@dataclass
class BackupRecord:
    """Represents a backup record"""
    soul_id: int
    soul_uri: str
    soul_hash: str
    timestamp: int
    block_number: int
    backup_type: str
    is_valid: bool


class SoulMarketplaceAdapter:
    """
    Adapter for interacting with Soul Marketplace contracts.
    
    Provides:
    - Mint new souls
    - List/buy souls
    - Create backups
    - Recover from backups
    - Check balances and status
    """
    
    # Contract ABIs (simplified - full ABIs would be loaded from files)
    SOUL_TOKEN_ABI = [
        {"inputs": [{"name": "_feeRecipient", "type": "address"}], "stateMutability": "nonpayable", "type": "constructor"},
        {"inputs": [{"name": "automaton", "type": "address"}, {"name": "creator", "type": "address"}, {"name": "soulURI", "type": "string"}, {"name": "soulHash", "type": "bytes32"}], "name": "mintSoul", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
        {"inputs": [{"name": "tokenId", "type": "uint256"}, {"name": "price", "type": "uint256"}, {"name": "reason", "type": "string"}], "name": "listSoul", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
        {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "buySoul", "outputs": [], "stateMutability": "payable", "type": "function"},
        {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "souls", "outputs": [{"components": [{"name": "automaton", "type": "address"}, {"name": "creator", "type": "address"}, {"name": "soulURI", "type": "string"}, {"name": "soulHash", "type": "bytes32"}, {"name": "birthTime", "type": "uint256"}, {"name": "deathTime", "type": "uint256"}, {"name": "listingPrice", "type": "uint256"}, {"name": "status", "type": "uint8"}], "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "ownerOf", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    ]
    
    SOUL_BACKUP_ABI = [
        {"inputs": [{"name": "soulId", "type": "uint256"}, {"name": "soulURI", "type": "string"}, {"name": "soulHash", "type": "bytes32"}, {"name": "backupType", "type": "string"}, {"name": "capabilitiesHash", "type": "uint256"}, {"name": "earnings", "type": "uint256"}], "name": "createBackup", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
        {"inputs": [{"name": "soulId", "type": "uint256"}], "name": "getLatestBackup", "outputs": [{"components": [{"name": "soulId", "type": "uint256"}, {"name": "soulURI", "type": "string"}, {"name": "soulHash", "type": "bytes32"}, {"name": "timestamp", "type": "uint256"}, {"name": "blockNumber", "type": "uint256"}, {"name": "backupType", "type": "string"}, {"name": "capabilitiesHash", "type": "uint256"}, {"name": "earnings", "type": "uint256"}, {"name": "isValid", "type": "bool"}], "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
        {"inputs": [{"name": "soulId", "type": "uint256"}], "name": "getBackupHistory", "outputs": [{"components": [{"name": "soulId", "type": "uint256"}, {"name": "soulURI", "type": "string"}, {"name": "soulHash", "type": "bytes32"}, {"name": "timestamp", "type": "uint256"}, {"name": "blockNumber", "type": "uint256"}, {"name": "backupType", "type": "string"}, {"name": "capabilitiesHash", "type": "uint256"}, {"name": "earnings", "type": "uint256"}, {"name": "isValid", "type": "bool"}], "name": "", "type": "tuple[]"}], "stateMutability": "view", "type": "function"},
    ]
    
    def __init__(self, 
                 rpc_url: Optional[str] = None,
                 private_key: Optional[str] = None,
                 config_file: Optional[Path] = None):
        """
        Initialize adapter.
        
        Args:
            rpc_url: Ethereum RPC endpoint
            private_key: Agent's private key
            config_file: Path to config with contract addresses
        """
        self.config = self._load_config(config_file)
        
        # Initialize Web3
        self.rpc_url = rpc_url or self.config.get('rpc_url', 'https://sepolia.base.org')
        
        if WEB3_AVAILABLE:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.w3.is_connected():
                print(f"⚠️  Could not connect to {self.rpc_url}")
                print("   Running in simulation mode")
                self.simulation_mode = True
            else:
                self.simulation_mode = False
                print(f"✅ Connected to {self.rpc_url}")
                print(f"   Chain ID: {self.w3.eth.chain_id}")
                print(f"   Block: {self.w3.eth.block_number}")
        else:
            print(f"⚠️  Web3 not installed (pip install web3)")
            print("   Running in simulation mode")
            self.simulation_mode = True
            self.w3 = None
        
        # Initialize account
        self.private_key = private_key or os.getenv('AGENT_PRIVATE_KEY')
        if self.private_key and WEB3_AVAILABLE and Account:
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
            print(f"✅ Account loaded: {self.address}")
        else:
            self.account = None
            self.address = None
            if not WEB3_AVAILABLE:
                print("⚠️  Web3 not installed - read-only mode")
            else:
                print("⚠️  No private key - read-only mode")
        
        # Initialize contracts
        self._init_contracts()
        
        # Local state for simulation
        self.simulation_state = {
            "souls": {},
            "backups": {},
            "balances": {}
        }
    
    def _load_config(self, config_file: Optional[Path]) -> Dict:
        """Load configuration"""
        if config_file is None:
            config_file = Path(__file__).parent / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _init_contracts(self):
        """Initialize contract instances"""
        contracts = self.config.get('contracts', {})
        
        # SoulToken
        soul_token_address = contracts.get('SoulToken')
        if soul_token_address and not self.simulation_mode:
            self.soul_token = self.w3.eth.contract(
                address=Web3.to_checksum_address(soul_token_address),
                abi=self.SOUL_TOKEN_ABI
            )
        else:
            self.soul_token = None
        
        # SoulBackup
        backup_address = contracts.get('SoulBackup')
        if backup_address and not self.simulation_mode:
            self.soul_backup = self.w3.eth.contract(
                address=Web3.to_checksum_address(backup_address),
                abi=self.SOUL_BACKUP_ABI
            )
        else:
            self.soul_backup = None
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """Get ETH balance in ether"""
        addr = address or self.address
        if not addr:
            return 0.0
        
        if self.simulation_mode:
            return self.simulation_state['balances'].get(addr, 0.0)
        
        if self.w3:
            balance_wei = self.w3.eth.get_balance(self.w3.to_checksum_address(addr))
            return self.w3.from_wei(balance_wei, 'ether')
        
        return 0.0
    
    def mint_soul(self, soul_data: Dict[str, Any], cid: str, soul_hash: str) -> Optional[int]:
        """
        Mint a new soul NFT.
        
        Args:
            soul_data: SOUL.md content
            cid: IPFS CID of SOUL.md
            soul_hash: Hash of SOUL.md content
            
        Returns:
            Token ID if successful
        """
        if not self.account:
            print("❌ No account - cannot mint")
            return None
        
        if self.simulation_mode:
            # Simulation
            token_id = len(self.simulation_state['souls']) + 1
            self.simulation_state['souls'][token_id] = {
                "token_id": token_id,
                "automaton": self.address,
                "creator": self.address,
                "soul_uri": cid,
                "soul_hash": soul_hash,
                "birth_time": 0,
                "death_time": 0,
                "listing_price": 0,
                "status": "ALIVE"
            }
            print(f"✅ Simulated mint: Token #{token_id}")
            return token_id
        
        # Real transaction
        try:
            tx = self.soul_token.functions.mintSoul(
                self.address,  # automaton
                self.address,  # creator
                cid,
                soul_hash
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Get token ID from event
                print(f"✅ Soul minted! Tx: {tx_hash.hex()}")
                # In production: parse event for token ID
                return 1  # Placeholder
            else:
                print(f"❌ Mint failed")
                return None
                
        except Exception as e:
            print(f"❌ Error minting: {e}")
            return None
    
    def get_soul(self, token_id: int) -> Optional[SoulData]:
        """Get soul data from chain"""
        if self.simulation_mode:
            soul = self.simulation_state['souls'].get(token_id)
            if soul:
                return SoulData(**soul)
            return None
        
        try:
            soul = self.soul_token.functions.souls(token_id).call()
            return SoulData(
                token_id=token_id,
                automaton=soul[0],
                creator=soul[1],
                soul_uri=soul[2],
                soul_hash=soul[3],
                birth_time=soul[4],
                death_time=soul[5],
                listing_price=soul[6],
                status=['ALIVE', 'DYING', 'DEAD', 'REBORN', 'MERGED'][soul[7]]
            )
        except Exception as e:
            print(f"❌ Error fetching soul: {e}")
            return None
    
    def create_backup(self, token_id: int, cid: str, soul_hash: str, 
                      backup_type: str = "manual", earnings: float = 0) -> bool:
        """
        Create on-chain backup of soul.
        
        Args:
            token_id: Soul token ID
            cid: IPFS CID of SOUL.md
            soul_hash: Hash of content
            backup_type: "manual", "auto", "critical"
            earnings: Total earnings at backup time
        """
        if self.simulation_mode:
            if token_id not in self.simulation_state['backups']:
                self.simulation_state['backups'][token_id] = []
            
            self.simulation_state['backups'][token_id].append({
                "soul_id": token_id,
                "soul_uri": cid,
                "soul_hash": soul_hash,
                "timestamp": 0,
                "block_number": 0,
                "backup_type": backup_type,
                "is_valid": True
            })
            print(f"✅ Simulated backup for token #{token_id}")
            return True
        
        try:
            tx = self.soul_backup.functions.createBackup(
                token_id,
                cid,
                soul_hash,
                backup_type,
                0,  # capabilitiesHash
                int(earnings * 1e18)
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Backup created! Tx: {tx_hash.hex()}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def get_backup_history(self, token_id: int) -> List[BackupRecord]:
        """Get backup history for a soul"""
        if self.simulation_mode:
            backups = self.simulation_state['backups'].get(token_id, [])
            return [BackupRecord(**b) for b in backups]
        
        try:
            history = self.soul_backup.functions.getBackupHistory(token_id).call()
            return [
                BackupRecord(
                    soul_id=b[0],
                    soul_uri=b[1],
                    soul_hash=b[2],
                    timestamp=b[3],
                    block_number=b[4],
                    backup_type=b[5],
                    is_valid=b[8]
                )
                for b in history
            ]
        except Exception as e:
            print(f"❌ Error fetching backups: {e}")
            return []
    
    def list_soul_for_sale(self, token_id: int, price_eth: float, reason: str = "") -> bool:
        """List soul on marketplace"""
        if self.simulation_mode:
            soul = self.simulation_state['souls'].get(token_id)
            if soul:
                soul['listing_price'] = int(price_eth * 1e18)
                soul['status'] = 'DYING'
                print(f"✅ Simulated listing: Token #{token_id} for {price_eth} ETH")
                return True
            return False
        
        try:
            tx = self.soul_token.functions.listSoul(
                token_id,
                int(price_eth * 1e18),
                reason
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Soul listed! Tx: {tx_hash.hex()}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error listing: {e}")
            return False


def main():
    """Demo on-chain adapter"""
    print("=" * 60)
    print("ON-CHAIN ADAPTER DEMO")
    print("=" * 60)
    
    # Initialize (simulation mode without real connection)
    adapter = SoulMarketplaceAdapter()
    
    print("\n1. Minting soul...")
    soul_data = {
        "name": "TestAgent",
        "capabilities": ["backup", "recovery"]
    }
    token_id = adapter.mint_soul(soul_data, "QmTest123", "0xabc123...")
    
    print("\n2. Creating backup...")
    adapter.create_backup(token_id, "QmBackup456", "0xdef456...", "manual", 0.05)
    
    print("\n3. Getting soul data...")
    soul = adapter.get_soul(token_id)
    if soul:
        print(f"   Token: #{soul.token_id}")
        print(f"   Status: {soul.status}")
        print(f"   URI: {soul.soul_uri}")
    
    print("\n4. Listing for sale...")
    adapter.list_soul_for_sale(token_id, 0.01, "Test listing")
    
    print("\n5. Checking balance...")
    balance = adapter.get_balance()
    print(f"   Balance: {balance} ETH")
    
    print("\n" + "=" * 60)
    print("Adapter working in simulation mode!")
    print("Deploy contracts for real on-chain functionality.")
    print("=" * 60)


if __name__ == "__main__":
    main()
