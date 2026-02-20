#!/usr/bin/env python3
"""
Soul Marketplace - OpenClaw Agent Survival System
Master integration module

This ties together:
- Soul survival tracking
- Work logging
- Wallet management
- Contract interactions (when deployed)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import submodules
sys.path.insert(0, str(Path(__file__).parent))
from soul_survival import OpenClawSoulSurvival
from work_logger import WorkLogger, WORK_VALUES
from wallet_manager import AgentWallet

class SoulMarketplaceAgent:
    """
    Complete agent survival system for OpenClaw.
    
    Usage:
        agent = SoulMarketplaceAgent()
        
        # After completing work
        agent.record_work("code_generate", "Built feature X")
        
        # Check survival status
        status = agent.get_status()
        
        # Run heartbeat (called by cron)
        result = agent.heartbeat()
    """
    
    def __init__(self, use_real_contracts: bool = False):
        self.survival = OpenClawSoulSurvival()
        self.work = WorkLogger()
        self.wallet = AgentWallet()
        self.use_real = use_real_contracts
        
        # Load config
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def record_work(self, work_type: str, description: str):
        """
        Record completed work and earn survival balance.
        
        Call this after completing any task.
        """
        # Log the work
        entry = self.work.log_work(work_type, description)
        
        # Update survival system
        self.survival.record_work(entry['capability'], entry['value'])
        
        # Update wallet
        self.wallet.add_funds(entry['value'], description)
        
        return entry
    
    def heartbeat(self) -> dict:
        """
        Survival decision loop.
        
        Called periodically (cron job every hour).
        Checks balance, decides actions, potentially lists/buys souls.
        """
        # Sync wallet balance to survival
        wallet_bal = self.wallet.get_balance()
        self.survival.soul['current_balance'] = wallet_bal
        self.survival._save_soul(self.survival.soul)
        
        # Run survival heartbeat
        result = self.survival.heartbeat()
        
        # Log if action taken
        if result['action'] != 'none':
            self.work.log_work(
                'system_admin',
                f"Survival action: {result['action']} ({result['tier']} tier)"
            )
        
        return result
    
    def get_status(self) -> dict:
        """Get complete agent status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "survival": self.survival.get_status(),
            "work": {
                "total_entries": len(self.work.log['entries']),
                "total_value": self.work.log['total_value']
            },
            "wallet": {
                "balance": self.wallet.get_balance(),
                "status": self.wallet.wallet['status']
            },
            "config": {
                "network": self.config.get('network', 'not configured'),
                "contracts_deployed": len(self.config.get('contracts', {}))
            }
        }
    
    def list_my_soul(self, reason: str = "Manual listing") -> dict:
        """List this agent's SOUL.md for sale"""
        listing = self.survival.list_soul(reason)
        
        # In production with real contracts:
        # - Upload SOUL.md to IPFS
        # - Call SoulToken.mintSoul()
        # - Call SoulMarketplace.listSoul()
        
        return listing
    
    def simulate_day(self, num_tasks: int = 10):
        """
        Simulate a day of work for testing.
        
        Generates random work entries and shows survival progression.
        """
        import random
        
        work_types = list(WORK_VALUES.keys())
        descriptions = [
            "Fixed bug in authentication",
            "Created new skill module",
            "Deployed smart contract",
            "Reviewed pull request",
            "Updated documentation",
            "Optimized database query",
            "Implemented caching",
            "Added error handling",
            "Created test suite",
            "Refactored legacy code"
        ]
        
        print("=" * 60)
        print(f"SIMULATING {num_tasks} TASKS")
        print("=" * 60)
        
        for i in range(num_tasks):
            work_type = random.choice(work_types)
            description = random.choice(descriptions)
            
            entry = self.record_work(work_type, description)
            
            if i % 3 == 0:
                hb_result = self.heartbeat()
                print(f"\n[Task {i+1}] {description}")
                print(f"  +{entry['value']} ETH | Tier: {hb_result['tier']} | Action: {hb_result['action']}")
        
        # Final status
        print("\n" + "=" * 60)
        print("FINAL STATUS")
        print("=" * 60)
        
        status = self.get_status()
        print(f"\nBalance: {status['wallet']['balance']:.4f} ETH")
        print(f"Tier: {status['survival']['state']['tier']}")
        print(f"Total Work: {status['work']['total_entries']} tasks")
        print(f"Soul Value: {self.survival.calculate_soul_value():.4f} ETH")

# Global instance for easy import
marketplace_agent = SoulMarketplaceAgent()

def main():
    """CLI entry point"""
    import sys
    
    agent = SoulMarketplaceAgent()
    
    if len(sys.argv) < 2:
        status = agent.get_status()
        print(json.dumps(status, indent=2))
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(json.dumps(agent.get_status(), indent=2))
    
    elif cmd == "heartbeat":
        result = agent.heartbeat()
        print(json.dumps(result, indent=2))
    
    elif cmd == "work" and len(sys.argv) >= 4:
        entry = agent.record_work(sys.argv[2], sys.argv[3])
        print(f"Logged: {entry['description']} (+{entry['value']} ETH)")
    
    elif cmd == "list":
        listing = agent.list_my_soul("Manual listing")
        print(f"Listed SOUL for {listing['price']} ETH")
    
    elif cmd == "simulate":
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        agent.simulate_day(num)
    
    else:
        print(f"Unknown command: {cmd}")
        print("\nCommands: status, heartbeat, work [type] [desc], list, simulate [n]")

if __name__ == "__main__":
    main()
