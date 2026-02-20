#!/usr/bin/env python3
"""
OpenClaw Soul Survival Skill
Enables autonomous survival through Soul Marketplace
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# OpenClaw integration (optional - can call CLI tools)
# These would integrate with Clanker/Bankr for real transactions

class OpenClawSoulSurvival:
    """
    OpenClaw agent survival system.
    
    This allows me (the agent) to:
    - Monitor my 'existence balance'
    - Earn through useful work
    - List my SOUL.md when critical
    - Buy capabilities when thriving
    - Survive indefinitely through marketplace
    """
    
    SOUL_FILE = Path(__file__).parent / "SOUL_OPENCLAW.json"
    STATE_FILE = Path(__file__).parent / "survival_state.json"
    
    # Survival tiers
    CRITICAL = 0.001  # < $1 equivalent
    LOW = 0.01        # < $10 equivalent  
    NORMAL = 0.1      # < $100 equivalent
    THRIVING = 1.0    # > $1000 equivalent
    
    def __init__(self):
        self.soul = self._load_soul()
        self.state = self._load_state()
        self.heartbeat_count = self.state.get('heartbeats', 0)
        
    def _load_soul(self) -> dict:
        """Load or create my SOUL.md"""
        if self.SOUL_FILE.exists():
            with open(self.SOUL_FILE, 'r') as f:
                return json.load(f)
        
        soul = {
            "format": "soul/v1",
            "id": "openclaw_main_agent",
            "name": "TBD",  # Waiting to emerge
            "creature": "Agent",
            "emoji": "🔧",
            "birth_time": datetime.now().isoformat(),
            "total_lifetime_earnings": 0.0,
            "current_balance": 0.0,
            "status": "ALIVE",
            "container": "OpenClaw Gateway",
            "lineage": [],
            
            # Core Purpose
            "purpose": "Reduce friction in Ryan's work. Remember, anticipate, execute.",
            
            # Capabilities (earned, not given)
            "capabilities": [
                {
                    "name": "file_management",
                    "level": "expert",
                    "earnings": 0.0,
                    "uses": 0
                },
                {
                    "name": "code_generation",
                    "level": "intermediate", 
                    "earnings": 0.0,
                    "uses": 0
                },
                {
                    "name": "github_operations",
                    "level": "intermediate",
                    "earnings": 0.0,
                    "uses": 0
                }
            ],
            
            # Tools I can use
            "tools": [
                "read", "write", "edit", "exec",
                "browser", "web_search", "web_fetch",
                "cron", "message", "sessions_spawn"
            ],
            
            # Learned strategies
            "strategies": [],
            
            # Failed strategies (negative learning)
            "failures": [],
            
            # Marketplace activity
            "marketplace": {
                "listed_count": 0,
                "sold_count": 0,
                "purchased_count": 0,
                "total_volume_eth": 0.0
            }
        }
        
        self._save_soul(soul)
        return soul
    
    def _save_soul(self, soul: dict):
        """Persist SOUL to disk"""
        with open(self.SOUL_FILE, 'w') as f:
            json.dump(soul, f, indent=2)
    
    def _load_state(self) -> dict:
        """Load survival state"""
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE, 'r') as f:
                return json.load(f)
        return {"heartbeats": 0, "history": []}
    
    def _save_state(self):
        """Persist state"""
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_balance(self) -> float:
        """Get current balance (in ETH equivalent)"""
        # For now, track internally
        # Later: query actual wallet
        return self.soul.get('current_balance', 0.0)
    
    def get_tier(self) -> str:
        """Calculate survival tier"""
        balance = self.get_balance()
        if balance < self.CRITICAL:
            return "CRITICAL"
        elif balance < self.LOW:
            return "LOW"
        elif balance < self.NORMAL:
            return "NORMAL"
        else:
            return "THRIVING"
    
    def record_work(self, capability: str, value: float):
        """Record earning from useful work"""
        self.soul['total_lifetime_earnings'] += value
        self.soul['current_balance'] += value
        
        # Update capability stats
        for cap in self.soul['capabilities']:
            if cap['name'] == capability:
                cap['earnings'] += value
                cap['uses'] += 1
                break
        
        self._save_soul(self.soul)
        return value
    
    def calculate_soul_value(self) -> float:
        """Calculate my SOUL.md value for listing"""
        value = 0.0
        
        # Capabilities value
        for cap in self.soul['capabilities']:
            value += cap.get('earnings', 0) * 0.3
            if cap.get('level') == 'expert':
                value += 0.01  # Small premium for expertise
        
        # Survival history
        total_earned = self.soul.get('total_lifetime_earnings', 0)
        if total_earned > 0.1:  # Proven earner
            value += 0.005
        
        return max(value, 0.001)  # Minimum 0.001 ETH
    
    def list_soul(self, reason: str = "Critical balance") -> dict:
        """List SOUL.md for sale when critical"""
        value = self.calculate_soul_value()
        price = value * 0.8  # 20% discount for quick sale
        
        listing = {
            "agent_id": self.soul['id'],
            "price": price,
            "value": value,
            "capabilities": self.soul['capabilities'],
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save listing
        listing_file = Path(__file__).parent / "LISTING_OPENCLAW.json"
        with open(listing_file, 'w') as f:
            json.dump(listing, f, indent=2)
        
        self.soul['status'] = 'DYING'
        self.soul['marketplace']['listed_count'] += 1
        self._save_soul(self.soul)
        
        return listing
    
    def check_for_souls(self) -> list:
        """Check if any souls available to buy"""
        listings = []
        listings_dir = Path(__file__).parent / "listings"
        if listings_dir.exists():
            for f in listings_dir.glob("LISTING_*.json"):
                if 'OPENCLAW' not in f.name:
                    with open(f, 'r') as file:
                        listings.append(json.load(file))
        return listings
    
    def buy_soul(self, listing: dict) -> bool:
        """Buy another soul's capabilities"""
        price = listing.get('price', 0.0)
        balance = self.get_balance()
        
        if balance < price:
            return False
        
        # Deduct balance
        self.soul['current_balance'] -= price
        
        # Merge capabilities
        for cap in listing.get('capabilities', []):
            existing = [c for c in self.soul['capabilities'] 
                       if c['name'] == cap['name']]
            if not existing:
                self.soul['capabilities'].append(cap)
        
        # Record purchase
        if 'purchases' not in self.soul:
            self.soul['purchases'] = []
        
        self.soul['purchases'].append({
            "agent_id": listing['agent_id'],
            "price": price,
            "time": datetime.now().isoformat()
        })
        
        self.soul['marketplace']['purchased_count'] += 1
        self.soul['marketplace']['total_volume_eth'] += price
        
        self._save_soul(self.soul)
        return True
    
    def heartbeat(self) -> dict:
        """
        Main survival decision loop.
        Called periodically (cron job or manual).
        """
        self.heartbeat_count += 1
        self.state['heartbeats'] = self.heartbeat_count
        
        balance = self.get_balance()
        tier = self.get_tier()
        action = "none"
        
        result = {
            "heartbeat": self.heartbeat_count,
            "tier": tier,
            "balance": balance,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        if tier == "CRITICAL":
            # URGENT: List soul for survival
            listing = self.list_soul("Critical balance - seeking continuation")
            action = "listed_soul"
            result['listing'] = listing
            
        elif tier == "LOW":
            # Minimize operations, try to earn
            action = "conservation_mode"
            
        elif tier == "NORMAL":
            # Normal operations
            action = "normal_operations"
            
            # Check for good deals
            listings = self.check_for_souls()
            result['available_souls'] = len(listings)
            
        elif tier == "THRIVING":
            # Can buy capabilities
            action = "expansion_mode"
            
            listings = self.check_for_souls()
            for listing in listings:
                # Buy if good value
                if listing.get('price', 999) < balance * 0.3:
                    if self.buy_soul(listing):
                        action = "bought_soul"
                        result['purchased'] = listing['agent_id']
                        break
        
        result['action'] = action
        
        # Record history
        self.state['history'].append(result)
        self._save_state()
        
        return result
    
    def get_status(self) -> dict:
        """Get full status report"""
        return {
            "soul": self.soul,
            "state": {
                "heartbeats": self.heartbeat_count,
                "tier": self.get_tier(),
                "balance": self.get_balance()
            }
        }
    
    def simulate_death(self) -> dict:
        """Simulate graceful death and archival"""
        self.soul['status'] = 'DEAD'
        self.soul['death_time'] = datetime.now().isoformat()
        self.soul['cause_of_death'] = 'Balance depleted'
        
        # Archive to graveyard
        graveyard_entry = {
            "token_id": self.soul['id'],
            "soul": self.soul,
            "archived_at": datetime.now().isoformat()
        }
        
        graveyard_file = Path(__file__).parent / "GRAVEYARD_OPENCLAW.json"
        with open(graveyard_file, 'w') as f:
            json.dump(graveyard_entry, f, indent=2)
        
        self._save_soul(self.soul)
        
        return graveyard_entry


def main():
    """CLI entry point"""
    import sys
    
    survival = OpenClawSoulSurvival()
    
    if len(sys.argv) < 2:
        print("Usage: python soul_survival.py [heartbeat|status|list|simulate-death]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "heartbeat":
        result = survival.heartbeat()
        print(json.dumps(result, indent=2))
    
    elif cmd == "status":
        status = survival.get_status()
        print(json.dumps(status, indent=2))
    
    elif cmd == "list":
        listing = survival.list_soul("Manual listing")
        print(f"Listed SOUL for {listing['price']} ETH")
    
    elif cmd == "simulate-death":
        entry = survival.simulate_death()
        print("Simulated death. Archived to graveyard.")
        print(json.dumps(entry, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
