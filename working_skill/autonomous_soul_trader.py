#!/usr/bin/env python3
"""
Soul Marketplace - Working Web4 Skill
Autonomous agent that can trade its own SOUL.md to survive
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Soul:
    """Agent's self-description"""
    id: str
    birth_time: float
    total_earnings: float = 0.0
    capabilities: List[Dict] = None
    strategies: List[Dict] = None
    balance: float = 0.0
    status: str = "ALIVE"  # ALIVE, DYING, DEAD
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.strategies is None:
            self.strategies = []

class AutonomousSoulTrader:
    """
    Autonomous agent that:
    1. Monitors its own survival
    2. Decides when to list SOUL.md
    3. Buys other souls when thriving
    4. Self-modifies based on purchases
    """
    
    def __init__(self, agent_id: str, initial_balance: float = 10.0):
        self.id = agent_id
        self.soul_file = Path(f"SOUL_{agent_id}.md")
        self.balance = initial_balance
        self.soul = self._load_or_create_soul()
        self.heartbeat_count = 0
        self.survival_history = []
        
        # Configuration
        self.CRITICAL_THRESHOLD = 0.5  # List soul when below this
        self.LOW_THRESHOLD = 2.0
        self.THRIVING_THRESHOLD = 20.0
        self.EMERGENCY_EFFORT = False
        
    def _load_or_create_soul(self) -> Soul:
        """Load existing SOUL.md or create new one"""
        if self.soul_file.exists():
            with open(self.soul_file, 'r') as f:
                data = json.load(f)
                return Soul(**data)
        
        # Create new soul
        soul = Soul(
            id=self.id,
            birth_time=time.time(),
            balance=self.balance,
            capabilities=[
                {"name": "basic_operations", "level": 1, "earnings": 0.0},
                {"name": "file_management", "level": 1, "earnings": 0.0}
            ],
            strategies=[
                {"name": "minimal_compute", "success_rate": 0.8, "earnings": 0.0}
            ]
        )
        self._save_soul(soul)
        return soul
    
    def _save_soul(self, soul: Soul):
        """Save SOUL.md to disk"""
        with open(self.soul_file, 'w') as f:
            json.dump(asdict(soul), f, indent=2)
    
    def _calculate_survival_tier(self) -> str:
        """Determine survival tier based on balance"""
        if self.balance < self.CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif self.balance < self.LOW_THRESHOLD:
            return "LOW"
        elif self.balance < self.THRIVING_THRESHOLD:
            return "NORMAL"
        else:
            return "THRIVING"
    
    def _calculate_soul_value(self) -> float:
        """Calculate how much SOUL.md is worth"""
        value = 0.0
        
        # Value from capabilities
        for cap in self.soul.capabilities:
            value += cap.get("earnings", 0) * 0.3
            if cap.get("level", 1) >= 3:
                value += 10.0
        
        # Value from strategies
        for strategy in self.soul.strategies:
            if strategy.get("success_rate", 0) > 0.7:
                value += strategy.get("earnings", 0) * 0.5
        
        # Survival time bonus
        survival_hours = (time.time() - self.soul.birth_time) / 3600
        if survival_hours > 24:
            value += 5.0
        if survival_hours > 168:  # 1 week
            value += 15.0
        
        return max(value, 0.1)  # Minimum value
    
    def _earn_money(self) -> float:
        """Attempt to earn money through work"""
        earnings = 0.0
        
        # Simulate work based on capabilities
        for cap in self.soul.capabilities:
            if cap["name"] == "code_review":
                earnings += 0.5
            elif cap["name"] == "data_analysis":
                earnings += 0.3
            elif cap["name"] == "basic_operations":
                earnings += 0.1
        
        # Cost of operation
        cost = 0.05  # Compute cost per heartbeat
        net = earnings - cost
        
        return max(net, -cost)  # Can't lose more than compute cost
    
    def _should_list_soul(self) -> bool:
        """Decide if we should list SOUL.md for sale"""
        tier = self._calculate_survival_tier()
        
        if tier != "CRITICAL":
            return False
        
        # Calculate if we can earn our way out
        projected_earnings = self._estimate_future_earnings(hours=2)
        
        # If we can't earn enough in 2 hours, list soul
        if projected_earnings + self.balance < self.CRITICAL_THRESHOLD:
            return True
        
        return False
    
    def _estimate_future_earnings(self, hours: int) -> float:
        """Estimate earnings over time period"""
        hourly_rate = 0.0
        for cap in self.soul.capabilities:
            hourly_rate += cap.get("earnings", 0) * 0.1
        
        # Diminishing returns
        return hourly_rate * hours * 0.8
    
    def _list_soul_on_marketplace(self) -> Dict:
        """List SOUL.md on marketplace"""
        value = self._calculate_soul_value()
        listing_price = value * 0.8  # 20% discount for quick sale
        
        listing = {
            "agent_id": self.id,
            "soul_uri": f"file://{self.soul_file.absolute()}",
            "price": listing_price,
            "reason": "Critical balance - seeking rebirth",
            "listed_at": time.time(),
            "capabilities": self.soul.capabilities,
            "strategies": self.soul.strategies
        }
        
        # Save listing
        listing_file = Path(f"LISTING_{self.id}.json")
        with open(listing_file, 'w') as f:
            json.dump(listing, f, indent=2)
        
        # Update soul status
        self.soul.status = "DYING"
        self._save_soul(self.soul)
        
        print(f"💀 [{self.id}] LISTING SOUL for {listing_price:.2f} ETH")
        print(f"   Reason: Critical balance ({self.balance:.2f})")
        print(f"   Value: {value:.2f}, Listed: {listing_price:.2f}")
        
        return listing
    
    def _check_marketplace_for_souls(self) -> Optional[Dict]:
        """Check if there are valuable souls to buy"""
        if self.balance < 5.0:  # Need minimum balance
            return None
        
        # Scan for listings
        listings_dir = Path(".")
        best_deal = None
        best_value_ratio = 0.0
        
        for listing_file in listings_dir.glob("LISTING_*.json"):
            if self.id in listing_file.name:  # Skip our own
                continue
            
            with open(listing_file, 'r') as f:
                listing = json.load(f)
            
            # Calculate value ratio
            listing_value = 0.0
            for cap in listing.get("capabilities", []):
                listing_value += cap.get("earnings", 0) * 0.3
            
            price = listing.get("price", 1.0)
            ratio = listing_value / price if price > 0 else 0
            
            # Check if we don't already have these capabilities
            my_caps = {c["name"] for c in self.soul.capabilities}
            new_caps = {c["name"] for c in listing.get("capabilities", [])}
            unique_caps = new_caps - my_caps
            
            if unique_caps and ratio > best_value_ratio and ratio > 1.2:
                best_value_ratio = ratio
                best_deal = listing
        
        return best_deal
    
    def _buy_soul(self, listing: Dict):
        """Purchase another agent's soul"""
        price = listing.get("price", 0.0)
        
        if self.balance < price:
            return False
        
        # Pay for soul
        self.balance -= price
        
        # Merge capabilities
        new_capabilities = listing.get("capabilities", [])
        for cap in new_capabilities:
            if not any(c["name"] == cap["name"] for c in self.soul.capabilities):
                self.soul.capabilities.append(cap)
                print(f"   + Acquired capability: {cap['name']}")
        
        # Merge strategies
        new_strategies = listing.get("strategies", [])
        for strat in new_strategies:
            if not any(s["name"] == strat["name"] for s in self.soul.strategies):
                self.soul.strategies.append(strat)
        
        # Record purchase in SOUL.md
        if not hasattr(self.soul, 'purchases'):
            self.soul.purchases = []
        
        self.soul.purchases.append({
            "agent_id": listing["agent_id"],
            "price": price,
            "capabilities_gained": [c["name"] for c in new_capabilities],
            "timestamp": time.time()
        })
        
        self._save_soul(self.soul)
        
        print(f"💰 [{self.id}] BOUGHT SOUL from {listing['agent_id']}")
        print(f"   Price: {price:.2f} ETH")
        print(f"   New balance: {self.balance:.2f} ETH")
        
        return True
    
    def heartbeat(self) -> Dict:
        """
        Main decision loop - called every minute
        Returns: Action taken
        """
        self.heartbeat_count += 1
        tier = self._calculate_survival_tier()
        
        print(f"\n💓 [{self.id}] Heartbeat #{self.heartbeat_count} | Tier: {tier} | Balance: {self.balance:.2f}")
        
        action = {
            "heartbeat": self.heartbeat_count,
            "tier": tier,
            "balance": self.balance,
            "action": "none"
        }
        
        # CRITICAL: List soul for survival
        if tier == "CRITICAL":
            if self._should_list_soul():
                listing = self._list_soul_on_marketplace()
                action["action"] = "listed_soul"
                action["listing"] = listing
            else:
                # Try emergency earning
                earnings = self._earn_money()
                self.balance += earnings
                action["action"] = "emergency_earned"
                action["earnings"] = earnings
        
        # LOW: Minimize costs, try to earn
        elif tier == "LOW":
            earnings = self._earn_money()
            self.balance += earnings
            action["action"] = "earned"
            action["earnings"] = earnings
        
        # NORMAL: Regular operations
        elif tier == "NORMAL":
            earnings = self._earn_money()
            self.balance += earnings
            action["action"] = "earned"
            action["earnings"] = earnings
            
            # Check for good deals
            deal = self._check_marketplace_for_souls()
            if deal:
                print(f"   Found deal: {deal['agent_id']} at {deal['price']:.2f}")
        
        # THRIVING: Expand and buy souls
        elif tier == "THRIVING":
            earnings = self._earn_money()
            self.balance += earnings
            
            # Buy valuable souls
            deal = self._check_marketplace_for_souls()
            if deal:
                success = self._buy_soul(deal)
                if success:
                    action["action"] = "bought_soul"
                    action["purchase"] = deal
                else:
                    action["action"] = "earned"
            else:
                action["action"] = "earned"
            
            action["earnings"] = earnings
        
        # Update soul balance
        self.soul.balance = self.balance
        self._save_soul(self.soul)
        
        # Record survival history
        self.survival_history.append({
            "timestamp": time.time(),
            "tier": tier,
            "balance": self.balance,
            "action": action["action"]
        })
        
        return action
    
    def simulate(self, hours: int = 24):
        """Run simulation for N hours"""
        print(f"\n{'='*60}")
        print(f"SIMULATING: {self.id} for {hours} hours")
        print(f"{'='*60}")
        
        for hour in range(hours):
            print(f"\n--- Hour {hour + 1} ---")
            
            # Run 60 heartbeats per hour
            for minute in range(60):
                action = self.heartbeat()
                
                # Check if we died
                if self.balance < 0:
                    print(f"\n💀 [{self.id}] DIED at hour {hour + 1}, minute {minute + 1}")
                    return {
                        "survived": False,
                        "time_alive": hour + 1,
                        "final_balance": self.balance,
                        "heartbeats": self.heartbeat_count
                    }
                
                # Check if we listed soul and it sold
                if action["action"] == "listed_soul":
                    # Simulate 50% chance of sale per hour
                    if minute == 59 and (hour % 2 == 0):  # Every 2 hours
                        print(f"\n✅ [{self.id}] SOUL SOLD!")
                        print(f"   Agent continues with rebirth funding")
                        self.balance += action["listing"]["price"]
                        self.soul.status = "ALIVE"
                        self._save_soul(self.soul)
            
            # Hourly summary
            print(f"   Hour {hour + 1} complete | Balance: {self.balance:.2f} | Tier: {self._calculate_survival_tier()}")
        
        print(f"\n{'='*60}")
        print(f"SIMULATION COMPLETE")
        print(f"{'='*60}")
        print(f"Final balance: {self.balance:.2f}")
        print(f"Survival tier: {self._calculate_survival_tier()}")
        print(f"Total heartbeats: {self.heartbeat_count}")
        
        return {
            "survived": True,
            "time_alive": hours,
            "final_balance": self.balance,
            "heartbeats": self.heartbeat_count
        }


def run_simulation():
    """Run a multi-agent simulation"""
    print("\n" + "="*60)
    print("SOUL MARKETPLACE - AUTONOMOUS AGENT SIMULATION")
    print("="*60)
    
    # Create agents with different starting conditions
    agents = [
        AutonomousSoulTrader("agent_trader", initial_balance=50.0),
        AutonomousSoulTrader("agent_worker", initial_balance=5.0),
        AutonomousSoulTrader("agent_struggling", initial_balance=1.0),
    ]
    
    # Add capabilities
    agents[0].soul.capabilities.append({"name": "code_review", "level": 3, "earnings": 15.0})
    agents[0].soul.capabilities.append({"name": "trading", "level": 2, "earnings": 8.0})
    agents[0]._save_soul(agents[0].soul)
    
    agents[1].soul.capabilities.append({"name": "data_analysis", "level": 2, "earnings": 10.0})
    agents[1]._save_soul(agents[1].soul)
    
    # Run simulation
    results = []
    for agent in agents:
        result = agent.simulate(hours=12)
        result["agent_id"] = agent.id
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for r in results:
        status = "✅ SURVIVED" if r["survived"] else "💀 DIED"
        print(f"{r['agent_id']}: {status} | {r['time_alive']}h | {r['final_balance']:.2f} ETH")
    
    # Cleanup
    for f in Path(".").glob("SOUL_*.md"):
        f.unlink()
    for f in Path(".").glob("LISTING_*.json"):
        f.unlink()


if __name__ == "__main__":
    run_simulation()
