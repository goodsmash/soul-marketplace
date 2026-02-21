#!/usr/bin/env python3
"""
Safe Agent Operations

Wraps all agent operations with spending guardrails.
Ensures micro-penny costs and requires approval for >$1.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

class SafeOperations:
    """
    Wrapper for safe, cost-controlled agent operations.
    
    All spending must go through this class.
    """
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        
        # Load guardrails
        from spending_guardrails import SpendingGuardrails
        self.guardrails = SpendingGuardrails(agent_id)
        
        # Load cost config
        from cost_config import COST_CONFIG
        self.cost_config = COST_CONFIG
        
        print(f"🔒 Safe Operations initialized for {agent_id}")
        print(f"   Micro-payments: &lt;${COST_CONFIG['limits']['micro_payment_threshold']} auto-approved")
        print(f"   Approval required: >${COST_CONFIG['limits']['approval_required_over']}")
    
    def safe_backup(self, backup_type: str = "auto", force: bool = False) -> Optional[str]:
        """
        Create backup with cost control.
        
        Args:
            backup_type: Type of backup
            force: Force backup even if costly
        """
        # Get backup cost
        on_chain_cost = self.cost_config['backups']['on_chain']['cost_per_backup']
        
        # Check if we should proceed
        check = self.guardrails.can_spend(on_chain_cost, "blockchain", f"{backup_type} backup")
        
        if not check['allowed'] and not force:
            print(f"⏭️ Backup skipped: {check['reason']}")
            print(f"   Cost would be: ${on_chain_cost}")
            return None
        
        # If requires approval
        if check.get('requires_approval') and not force:
            print(f"⏸️ Backup waiting for approval")
            print(f"   {check['approval_prompt']}")
            return None
        
        # Proceed with backup
        print(f"💾 Creating {backup_type} backup...")
        print(f"   Cost: ${on_chain_cost}")
        
        # Import and run backup
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from enhanced_survival import EnhancedSoulSurvival
        
        survival = EnhancedSoulSurvival(self.agent_id)
        
        # Create IPFS backup (free)
        cid = survival.ipfs_manager.backup_soul(survival.soul, backup_type)
        
        # Record the spending if we did on-chain backup
        if on_chain_cost > 0:
            self.guardrails.record_spending(on_chain_cost, "blockchain", f"{backup_type} backup")
        
        return cid
    
    def safe_mint(self, soul_cid: str, soul_hash: str) -> bool:
        """
        Mint SOUL NFT with cost control.
        
        This is expensive (~$0.50-1.00) so always requires approval.
        """
        mint_cost = self.cost_config['critical_ops']['mint_soul']['cost']
        
        print(f"\n🎨 Mint SOUL NFT Request")
        print(f"   Estimated cost: ${mint_cost}")
        
        check = self.guardrails.can_spend(mint_cost, "blockchain", "Mint SOUL NFT")
        
        if check.get('requires_approval'):
            print(f"\n⚠️  THIS COSTS REAL MONEY")
            print(f"   Amount: ${mint_cost}")
            print(f"   Purpose: Mint SOUL NFT on Base")
            print(f"\n   Type 'YES I APPROVE' to proceed:")
            # In real use, would wait for input
            print(f"   (Approval required - not auto-approved)")
            return False
        
        # Would proceed with mint here
        print(f"   Would mint now...")
        return True
    
    def safe_transfer(self, to_address: str, amount: float, purpose: str) -> bool:
        """
        Transfer ETH with cost control.
        """
        check = self.guardrails.can_spend(amount, to_address, purpose)
        
        if not check['allowed']:
            print(f"❌ Transfer blocked: {check['reason']}")
            return False
        
        if check.get('requires_approval'):
            approved = self.guardrails.request_approval(check['approval_prompt'])
            if not approved:
                print(f"❌ Transfer denied by user")
                return False
        
        # Record the spending
        self.guardrails.record_spending(amount, to_address, purpose)
        
        print(f"✅ Transfer approved: ${amount} to {to_address[:20]}...")
        return True
    
    def get_cost_report(self) -> str:
        """Get full cost and spending report"""
        return self.guardrails.get_spending_report()
    
    def daily_budget_remaining(self) -> float:
        """Get remaining daily budget"""
        daily_limit = self.cost_config['limits']['max_daily_usd']
        daily_spent = self.guardrails.history.get('daily_total', 0)
        return daily_limit - daily_spent


def main():
    """Demo safe operations"""
    print("=" * 60)
    print("SAFE OPERATIONS DEMO")
    print("=" * 60)
    
    safe = SafeOperations("demo_agent")
    
    # Test micro backup (should work)
    print("\n1. Micro backup (should work):")
    cid = safe.safe_backup("test")
    
    # Test expensive mint (should require approval)
    print("\n2. Mint NFT (should require approval):")
    safe.safe_mint("QmTest123", "0xabc...")
    
    # Test transfer (should require approval >$1)
    print("\n3. Large transfer (should require approval):")
    safe.safe_transfer("0x123...", 5.00, "Test transfer")
    
    # Show report
    print("\n4. Cost report:")
    print(safe.get_cost_report())
    
    print("\n" + "=" * 60)
    print("All spending is now protected!")
    print("Micro-payments only, >$1 requires approval")
    print("=" * 60)


if __name__ == "__main__":
    main()
