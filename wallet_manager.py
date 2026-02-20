#!/usr/bin/env python3
"""
Wallet Manager for OpenClaw Agent Survival
Manages Ethereum wallet for Soul Marketplace transactions
"""

import json
import os
from pathlib import Path
from typing import Optional

class AgentWallet:
    """
    Manages agent's Ethereum wallet for Soul Marketplace.
    
    In production, this would:
    - Generate/store keys securely
    - Connect to Base/Ethereum
    - Send transactions
    - Check balances
    
    For now: tracks simulated balance with migration path to real
    """
    
    WALLET_FILE = Path(__file__).parent / "wallet.json"
    
    def __init__(self):
        self.wallet = self._load_or_create()
    
    def _load_or_create(self) -> dict:
        if self.WALLET_FILE.exists():
            with open(self.WALLET_FILE, 'r') as f:
                return json.load(f)
        
        wallet = {
            "address": None,  # Set when funded
            "private_key": None,  # In production: encrypted
            "balance": 0.0,
            "network": "base-sepolia",  # Testnet first
            "transactions": [],
            "created_at": None,
            "status": "unfunded"  # unfunded | funded | active
        }
        self._save(wallet)
        return wallet
    
    def _save(self, wallet: dict):
        with open(self.WALLET_FILE, 'w') as f:
            json.dump(wallet, f, indent=2)
    
    def get_balance(self) -> float:
        """Get current balance in ETH"""
        return self.wallet.get('balance', 0.0)
    
    def add_funds(self, amount: float, source: str = "work"):
        """Add funds (from work earnings)"""
        self.wallet['balance'] += amount
        from datetime import datetime
        self.wallet['transactions'].append({
            "type": "income",
            "amount": amount,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self._save(self.wallet)
        return self.wallet['balance']
    
    def spend(self, amount: float, purpose: str) -> bool:
        """Spend funds (for marketplace purchases)"""
        if self.wallet['balance'] < amount:
            return False
        
        self.wallet['balance'] -= amount
        self.wallet['transactions'].append({
            "type": "expense",
            "amount": amount,
            "purpose": purpose
        })
        self._save(self.wallet)
        return True
    
    def fund_from_private_key(self, private_key: str):
        """
        Fund wallet with real private key.
        In production: use Bankr or secure key management
        """
        # This would:
        # 1. Derive address from key
        # 2. Check balance on-chain
        # 3. Enable real transactions
        
        self.wallet['private_key'] = "[encrypted]"  # Never store raw
        self.wallet['status'] = "funded"
        self._save(self.wallet)
        
        print("⚠️  PRODUCTION: Use Bankr CLI or secure key management")
        print("   Never store raw private keys in files")
        
        return self.wallet
    
    def setup_with_bankr(self):
        """
        Integration with Bankr CLI for real transactions
        """
        instructions = """
To connect real wallet via Bankr:

1. Install Bankr CLI:
   npm install -g @bankr/bankr

2. Configure API key:
   bankr config set api_key YOUR_KEY

3. Create wallet:
   bankr wallet create --name agent-survival

4. Fund wallet:
   bankr wallet fund --amount 0.01 --chain base

5. Update this wallet config:
   python3 wallet_manager.py set-address YOUR_ADDRESS

Then the agent can:
- List SOUL.md for real ETH
- Buy capabilities from other agents
- Pay for compute/resources
        """
        print(instructions)
        return instructions
    
    def export_for_web3(self) -> dict:
        """Export wallet config for Web3 integration"""
        return {
            "address": self.wallet.get('address'),
            "balance": self.wallet['balance'],
            "network": self.wallet['network'],
            "status": self.wallet['status']
        }

def main():
    """CLI for wallet management"""
    import sys
    
    wallet = AgentWallet()
    
    if len(sys.argv) < 2:
        print(f"Balance: {wallet.get_balance()} ETH")
        print(f"Status: {wallet.wallet['status']}")
        print("\nCommands: balance, fund, spend, setup-bankr")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "balance":
        print(f"{wallet.get_balance()} ETH")
    
    elif cmd == "fund" and len(sys.argv) >= 3:
        new_bal = wallet.add_funds(float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "manual")
        print(f"Added {sys.argv[2]} ETH. New balance: {new_bal} ETH")
    
    elif cmd == "spend" and len(sys.argv) >= 3:
        success = wallet.spend(float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "purchase")
        print(f"Spent {sys.argv[2]} ETH: {'Success' if success else 'Insufficient funds'}")
    
    elif cmd == "setup-bankr":
        wallet.setup_with_bankr()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
