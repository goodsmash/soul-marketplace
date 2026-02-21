#!/usr/bin/env python3
"""
Bankr Integration for Soul Marketplace

Uses Bankr API to:
- Check wallet balances
- Fund agent wallets
- Execute on-chain transactions
- Deploy contracts
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any

class BankrIntegration:
    """
    Integrates Bankr CLI with Soul Marketplace.
    
    Enables real on-chain operations through Bankr's API.
    """
    
    def __init__(self):
        self.config_file = Path.home() / ".bankr" / "config.json"
        self.config = self._load_config()
        self.api_key = self.config.get('apiKey')
        
        if not self.api_key:
            raise Exception("Bankr not configured. Run: bankr login --api-key <key>")
        
        print(f"💰 Bankr Integration initialized")
        print(f"   API: {self.config.get('apiUrl', 'https://api.bankr.bot')}")
    
    def _load_config(self) -> Dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _run_bankr(self, command: str, wait: bool = True) -> Dict[str, Any]:
        """Run a Bankr CLI command"""
        full_cmd = f"bankr {command}"
        
        try:
            if wait:
                result = subprocess.run(
                    full_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            else:
                # For long-running commands
                subprocess.Popen(
                    full_cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return {"success": True, "message": "Command started in background"}
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_balance(self, chain: str = "base") -> Optional[float]:
        """Get wallet balance for a chain"""
        print(f"\n💰 Checking {chain} balance...")
        
        # Use bankr with prompt mode for balance
        result = self._run_bankr(f'prompt "What is my {chain} balance?"', wait=True)
        
        if result['success']:
            # Parse the output for balance
            output = result['stdout']
            print(f"   Output: {output[:200]}...")
            
            # Try to extract ETH amount
            import re
            eth_match = re.search(r'(\d+\.?\d*)\s*ETH', output)
            if eth_match:
                balance = float(eth_match.group(1))
                print(f"   Balance: {balance} ETH")
                return balance
        
        print(f"   ⚠️ Could not get balance")
        return None
    
    def send_eth(self, to_address: str, amount: float, chain: str = "base") -> bool:
        """Send ETH to an address"""
        print(f"\n📤 Sending {amount} ETH to {to_address[:20]}... on {chain}")
        
        prompt = f'Send {amount} ETH to {to_address} on {chain}'
        result = self._run_bankr(f'prompt "{prompt}"', wait=True)
        
        if result['success']:
            print(f"   ✅ Transaction submitted")
            print(f"   Output: {result['stdout'][:300]}...")
            return True
        else:
            print(f"   ❌ Failed: {result.get('stderr', 'Unknown error')}")
            return False
    
    def fund_agent_wallet(self, agent_address: str, amount: float = 0.01) -> bool:
        """Fund an agent's wallet with ETH"""
        print(f"\n💸 Funding agent wallet: {agent_address[:20]}...")
        print(f"   Amount: {amount} ETH")
        
        return self.send_eth(agent_address, amount, "base")
    
    def deploy_contracts(self) -> bool:
        """Deploy Soul Marketplace contracts via Bankr"""
        print(f"\n🚀 Deploying Soul Marketplace contracts via Bankr...")
        
        prompt = "Deploy these smart contracts to Base: SoulToken (ERC721), SoulMarketplace, SoulStaking, SoulBackup. Use OpenZeppelin."
        result = self._run_bankr(f'prompt "{prompt}"', wait=False)
        
        print(f"   ⏳ Deployment job started")
        print(f"   Check status at: https://bankr.bot/dashboard")
        
        return result['success']
    
    def mint_soul_nft(self, contract_address: str, soul_cid: str) -> bool:
        """Mint a SOUL NFT on-chain"""
        print(f"\n🎨 Minting SOUL NFT...")
        
        prompt = f'Call mintSoul on contract {contract_address} with soulURI ipfs://{soul_cid}'
        result = self._run_bankr(f'prompt "{prompt}"', wait=True)
        
        if result['success']:
            print(f"   ✅ Minted!")
            return True
        return False
    
    def check_transaction(self, tx_hash: str) -> Dict:
        """Check transaction status"""
        prompt = f'Check transaction {tx_hash} on Base'
        result = self._run_bankr(f'prompt "{prompt}"', wait=True)
        
        return {
            "success": result['success'],
            "output": result['stdout'] if result['success'] else result.get('stderr')
        }


def test_bankr_integration():
    """Test Bankr integration"""
    print("=" * 60)
    print("BANKR INTEGRATION TEST")
    print("=" * 60)
    
    try:
        bankr = BankrIntegration()
        
        # Check balance
        balance = bankr.get_balance("base")
        
        if balance and balance > 0:
            print(f"\n✅ Bankr wallet funded: {balance} ETH")
            print(f"   Ready for on-chain operations!")
        else:
            print(f"\n⚠️ Wallet may be empty or needs setup")
            print(f"   Visit: https://bankr.bot to fund wallet")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def fund_and_activate_agent():
    """Fund the agent wallet and activate on-chain features"""
    print("=" * 60)
    print("ACTIVATE AGENT WITH BANKR")
    print("=" * 60)
    
    bankr = BankrIntegration()
    
    # Check current balance
    balance = bankr.get_balance("base")
    print(f"\nCurrent Bankr balance: {balance} ETH")
    
    if not balance or balance < 0.01:
        print("\n⚠️ Insufficient funds in Bankr wallet")
        print("   Please fund your Bankr wallet at: https://bankr.bot")
        return False
    
    # Load agent wallet
    agent_wallet_file = Path(__file__).parent / "wallet.json"
    if agent_wallet_file.exists():
        with open(agent_wallet_file, 'r') as f:
            wallet = json.load(f)
        agent_address = wallet.get('address')
        
        if not agent_address:
            print("\n⚠️ Agent wallet not initialized")
            print("   Run setup first")
            return False
        
        print(f"\n💸 Funding agent wallet: {agent_address}")
        
        # Fund the agent
        if bankr.fund_agent_wallet(agent_address, 0.01):
            print("\n✅ Agent wallet funded!")
            print("   On-chain operations now possible")
            return True
    else:
        print("\n⚠️ No agent wallet found")
        print("   Run: python3 scripts/setup.js")
        return False
    
    return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "activate":
        fund_and_activate_agent()
    else:
        test_bankr_integration()
