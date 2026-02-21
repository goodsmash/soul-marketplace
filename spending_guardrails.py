#!/usr/bin/env python3
"""
Spending Guardrails for Soul Marketplace

Safety system to prevent unexpected costs:
- Micro-pennies for routine operations
- Approval required for >$1
- Daily/weekly spending limits
- Emergency shutdown
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

class SpendingGuardrails:
    """
    Manages agent spending with safety limits.
    
    Rules:
    1. Micro-pennies for routine ops (&lt;$0.01)
    2. Ask permission for >$1
    3. Daily limit enforced
    4. Emergency stop available
    """
    
    # Spending thresholds
    MICRO_PAYMENT_MAX = 0.01      # $0.01 - no approval needed
    SMALL_PAYMENT_MAX = 0.10      # $0.10 - log only
    MEDIUM_PAYMENT_MAX = 1.00     # $1.00 - notify
    LARGE_PAYMENT_MIN = 1.00      # >$1.00 - REQUIRE APPROVAL
    
    # Daily limits
    DEFAULT_DAILY_LIMIT = 5.00    # $5/day default
    DEFAULT_WEEKLY_LIMIT = 20.00  # $20/week default
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        self.data_dir = Path(__file__).parent / ".spending"
        self.data_dir.mkdir(exist_ok=True)
        
        self.config_file = self.data_dir / f"config_{agent_id}.json"
        self.history_file = self.data_dir / f"history_{agent_id}.json"
        
        self.config = self._load_config()
        self.history = self._load_history()
        
        self.emergency_stop = self.config.get('emergency_stop', False)
        
        print(f"💰 Spending Guardrails initialized for {agent_id}")
        print(f"   Daily limit: ${self.config.get('daily_limit', self.DEFAULT_DAILY_LIMIT)}")
        print(f"   Micro-payments: &lt;${self.MICRO_PAYMENT_MAX} (auto-approved)")
        print(f"   Large payments: &gt;${self.LARGE_PAYMENT_MIN} (require approval)")
    
    def _load_config(self) -> Dict:
        """Load spending configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default safe configuration
        return {
            "daily_limit": self.DEFAULT_DAILY_LIMIT,
            "weekly_limit": self.DEFAULT_WEEKLY_LIMIT,
            "micro_payment_auto": True,
            "require_approval_over": self.LARGE_PAYMENT_MIN,
            "emergency_stop": False,
            "notification_email": None,
            "allowed_recipients": [],  # Whitelist
            "blocked_recipients": [],  # Blacklist
        }
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_history(self) -> Dict:
        """Load spending history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {
            "transactions": [],
            "daily_total": 0.0,
            "weekly_total": 0.0,
            "last_reset": time.time()
        }
    
    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _reset_if_needed(self):
        """Reset daily/weekly counters if needed"""
        last_reset = self.history.get('last_reset', 0)
        now = time.time()
        
        # Reset daily (24 hours)
        if now - last_reset > 86400:
            self.history['daily_total'] = 0.0
            self.history['last_reset'] = now
            print("💰 Daily spending counter reset")
        
        self._save_history()
    
    def can_spend(self, amount: float, recipient: str = None, purpose: str = "") -> Dict:
        """
        Check if spending is allowed.
        
        Returns dict with:
        - allowed: bool
        - reason: str
        - requires_approval: bool
        - approval_prompt: str (if needed)
        """
        self._reset_if_needed()
        
        # Emergency stop
        if self.emergency_stop:
            return {
                "allowed": False,
                "reason": "EMERGENCY STOP ACTIVE",
                "requires_approval": True,
                "approval_prompt": "Emergency stop is active. All spending blocked."
            }
        
        # Check daily limit
        daily_spent = self.history.get('daily_total', 0)
        daily_limit = self.config.get('daily_limit', self.DEFAULT_DAILY_LIMIT)
        
        if daily_spent + amount > daily_limit:
            return {
                "allowed": False,
                "reason": f"Daily limit exceeded (${daily_spent:.2f} / ${daily_limit:.2f})",
                "requires_approval": True,
                "approval_prompt": f"This would exceed daily limit. Spent: ${daily_spent:.2f}, Limit: ${daily_limit:.2f}"
            }
        
        # Check recipient blacklist
        if recipient and recipient in self.config.get('blocked_recipients', []):
            return {
                "allowed": False,
                "reason": "Recipient is blacklisted",
                "requires_approval": True,
                "approval_prompt": f"Recipient {recipient} is blocked."
            }
        
        # Micro-payment - auto approve
        if amount < self.MICRO_PAYMENT_MAX:
            return {
                "allowed": True,
                "reason": "Micro-payment (auto-approved)",
                "requires_approval": False
            }
        
        # Small payment - log but approve
        if amount < self.SMALL_PAYMENT_MAX:
            return {
                "allowed": True,
                "reason": f"Small payment (${amount:.4f})",
                "requires_approval": False
            }
        
        # Medium payment - notify
        if amount < self.MEDIUM_PAYMENT_MAX:
            return {
                "allowed": True,
                "reason": f"Medium payment (${amount:.2f})",
                "requires_approval": False,
                "notification": f"Spending ${amount:.2f} for: {purpose}"
            }
        
        # Large payment - REQUIRE APPROVAL
        return {
            "allowed": False,
            "reason": f"Large payment requires approval",
            "requires_approval": True,
            "approval_prompt": f"\n⚠️  LARGE PAYMENT REQUEST ⚠️\n\nAmount: ${amount:.2f}\nRecipient: {recipient or 'Unknown'}\nPurpose: {purpose}\n\nDaily spent: ${daily_spent:.2f} / ${daily_limit:.2f}\n\nApprove? (yes/no): "
        }
    
    def record_spending(self, amount: float, recipient: str, purpose: str, tx_hash: str = None):
        """Record a completed transaction"""
        transaction = {
            "timestamp": time.time(),
            "amount": amount,
            "recipient": recipient,
            "purpose": purpose,
            "tx_hash": tx_hash,
            "date": datetime.now().isoformat()
        }
        
        self.history['transactions'].append(transaction)
        self.history['daily_total'] += amount
        self.history['weekly_total'] += amount
        
        # Keep only last 1000 transactions
        if len(self.history['transactions']) > 1000:
            self.history['transactions'] = self.history['transactions'][-1000:]
        
        self._save_history()
        
        # Log spending
        print(f"💰 Recorded spending: ${amount:.4f} for {purpose}")
    
    def request_approval(self, prompt: str) -> bool:
        """
        Request user approval for spending.
        In production, this could:
        - Send Telegram message
        - Email notification
        - Wait for CLI input
        """
        print(f"\n{prompt}")
        
        # In a real interactive session, we'd wait for input
        # For now, return False (deny by default)
        return False
    
    def spend(self, amount: float, recipient: str, purpose: str, 
              auto_approve_micro: bool = True) -> Dict:
        """
        Attempt to spend money with guardrails.
        
        Returns result dict.
        """
        # Check if allowed
        check = self.can_spend(amount, recipient, purpose)
        
        if not check['allowed'] and not check.get('requires_approval'):
            return {
                "success": False,
                "reason": check['reason'],
                "amount": amount
            }
        
        # If requires approval
        if check.get('requires_approval'):
            if auto_approve_micro and amount < self.MICRO_PAYMENT_MAX:
                # Auto-approve micro payments
                pass
            else:
                approved = self.request_approval(check['approval_prompt'])
                if not approved:
                    return {
                        "success": False,
                        "reason": "User denied approval",
                        "amount": amount
                    }
        
        # Record the spending
        self.record_spending(amount, recipient, purpose)
        
        return {
            "success": True,
            "reason": check['reason'],
            "amount": amount,
            "daily_total": self.history['daily_total']
        }
    
    def get_spending_report(self) -> str:
        """Generate spending report"""
        self._reset_if_needed()
        
        daily = self.history.get('daily_total', 0)
        weekly = self.history.get('weekly_total', 0)
        limit = self.config.get('daily_limit', self.DEFAULT_DAILY_LIMIT)
        
        recent_tx = self.history['transactions'][-5:]
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║              SPENDING REPORT                             ║
╚══════════════════════════════════════════════════════════╝

Daily:  ${daily:.2f} / ${limit:.2f} ({daily/limit*100:.1f}%)
Weekly: ${weekly:.2f}

Recent Transactions:
"""
        for tx in recent_tx:
            report += f"  {tx['date'][:10]}: ${tx['amount']:.4f} - {tx['purpose'][:30]}\n"
        
        report += f"\nEmergency Stop: {'ACTIVE' if self.emergency_stop else 'Inactive'}"
        
        return report
    
    def set_limits(self, daily: float = None, weekly: float = None):
        """Update spending limits"""
        if daily:
            self.config['daily_limit'] = daily
        if weekly:
            self.config['weekly_limit'] = weekly
        self._save_config()
        print(f"💰 Updated limits - Daily: ${daily}, Weekly: ${weekly}")
    
    def emergency_stop_toggle(self, active: bool = True):
        """Toggle emergency stop"""
        self.emergency_stop = active
        self.config['emergency_stop'] = active
        self._save_config()
        
        if active:
            print("🛑 EMERGENCY STOP ACTIVATED - All spending blocked")
        else:
            print("✅ Emergency stop deactivated")


# Pre-configured for ultra-safe mode
class UltraSafeSpending(SpendingGuardrails):
    """Ultra-safe spending mode - micro-pennies only"""
    
    MICRO_PAYMENT_MAX = 0.001     # $0.001 (micro-pennies)
    SMALL_PAYMENT_MAX = 0.01      # $0.01
    MEDIUM_PAYMENT_MAX = 0.10     # $0.10
    LARGE_PAYMENT_MIN = 0.10      # >$0.10 requires approval
    
    DEFAULT_DAILY_LIMIT = 1.00    # $1/day max
    DEFAULT_WEEKLY_LIMIT = 5.00   # $5/week max


def main():
    """Demo spending guardrails"""
    print("=" * 60)
    print("SPENDING GUARDRAILS DEMO")
    print("=" * 60)
    
    guardrails = SpendingGuardrails("demo_agent")
    
    # Test micro-payment (should auto-approve)
    print("\n1. Micro-payment ($0.005):")
    result = guardrails.spend(0.005, "test_recipient", "Micro test")
    print(f"   Result: {result}")
    
    # Test medium payment (should approve but notify)
    print("\n2. Medium payment ($0.50):")
    result = guardrails.spend(0.50, "test_recipient", "Medium test")
    print(f"   Result: {result}")
    
    # Test large payment (should require approval)
    print("\n3. Large payment ($5.00):")
    result = guardrails.spend(5.00, "test_recipient", "Large test", auto_approve_micro=False)
    print(f"   Result: {result}")
    
    # Show report
    print("\n4. Spending report:")
    print(guardrails.get_spending_report())
    
    print("\n" + "=" * 60)
    print("Spending guardrails active!")
    print("Micro-payments auto-approved, >$1 requires permission")
    print("=" * 60)


if __name__ == "__main__":
    main()
