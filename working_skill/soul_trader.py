#!/usr/bin/env python3
"""
Soul Marketplace - Working Web4 Skill
Autonomous agent that trades its own SOUL.md to survive
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

class AutonomousSoulTrader:
    """Autonomous agent that survives by trading SOUL.md"""
    
    def __init__(self, agent_id, initial_balance=10.0):
        self.id = agent_id
        self.soul_file = Path(f"SOUL_{agent_id}.json")
        self.balance = initial_balance
        self.heartbeat_count = 0
        self.survival_history = []
        
        # Load or create soul
        self.soul = self._load_or_create_soul()
        
        print(f"[INIT] Agent {agent_id} born with {initial_balance} ETH")
        print(f"       Capabilities: {[c['name'] for c in self.soul.get('capabilities', [])]}")
    
    def _load_or_create_soul(self):
        if self.soul_file.exists():
            with open(self.soul_file, 'r') as f:
                return json.load(f)
        
        soul = {
            "id": self.id,
            "birth_time": time.time(),
            "total_earnings": 0.0,
            "balance": self.balance,
            "status": "ALIVE",
            "capabilities": [
                {"name": "basic_operations", "level": 1, "earnings": 0.0},
            ],
            "strategies": [
                {"name": "minimal_compute", "success_rate": 0.8}
            ]
        }
        self._save_soul(soul)
        return soul
    
    def _save_soul(self, soul):
        with open(self.soul_file, 'w') as f:
            json.dump(soul, f, indent=2)
    
    def get_tier(self):
        if self.balance < 0.5:
            return "CRITICAL"
        elif self.balance < 2.0:
            return "LOW"
        elif self.balance < 20.0:
            return "NORMAL"
        else:
            return "THRIVING"
    
    def earn_money(self):
        """Simulate earning based on capabilities"""
        earnings = 0.0
        for cap in self.soul.get("capabilities", []):
            if cap["name"] == "code_review":
                earnings += 0.5
            elif cap["name"] == "trading":
                earnings += 0.8
            elif cap["name"] == "data_analysis":
                earnings += 0.3
            else:
                earnings += 0.1
        
        # Cost of operation
        cost = 0.05
        net = max(earnings - cost, -cost)
        return net
    
    def calculate_soul_value(self):
        """Calculate SOUL.md value"""
        value = 0.0
        for cap in self.soul.get("capabilities", []):
            value += cap.get("earnings", 0) * 0.3
            if cap.get("level", 1) >= 3:
                value += 10.0
        
        survival_hours = (time.time() - self.soul.get("birth_time", time.time())) / 3600
        if survival_hours > 24:
            value += 5.0
        
        return max(value, 0.1)
    
    def list_soul(self):
        """List SOUL.md for sale"""
        value = self.calculate_soul_value()
        price = value * 0.8
        
        listing = {
            "agent_id": self.id,
            "price": price,
            "capabilities": self.soul.get("capabilities", []),
            "timestamp": time.time()
        }
        
        listing_file = Path(f"LISTING_{self.id}.json")
        with open(listing_file, 'w') as f:
            json.dump(listing, f)
        
        self.soul["status"] = "DYING"
        self._save_soul(self.soul)
        
        print(f"  >>> LISTING SOUL for {price:.2f} ETH (value: {value:.2f})")
        return listing
    
    def check_for_souls(self):
        """Check if any souls available to buy"""
        listings = []
        for f in Path(".").glob("LISTING_*.json"):
            if self.id not in f.name:
                with open(f, 'r') as file:
                    listings.append(json.load(file))
        return listings
    
    def buy_soul(self, listing):
        """Buy another soul"""
        price = listing.get("price", 0.0)
        if self.balance < price:
            return False
        
        self.balance -= price
        
        # Merge capabilities
        for cap in listing.get("capabilities", []):
            existing = [c for c in self.soul.get("capabilities", []) if c["name"] == cap["name"]]
            if not existing:
                self.soul["capabilities"].append(cap)
                print(f"  + Acquired: {cap['name']}")
        
        # Record purchase
        if "purchases" not in self.soul:
            self.soul["purchases"] = []
        
        self.soul["purchases"].append({
            "agent_id": listing["agent_id"],
            "price": price,
            "time": time.time()
        })
        
        self._save_soul(self.soul)
        print(f"  >>> BOUGHT SOUL from {listing['agent_id']} for {price:.2f} ETH")
        return True
    
    def heartbeat(self):
        """Main decision loop"""
        self.heartbeat_count += 1
        tier = self.get_tier()
        
        print(f"\n[{self.id}] #{self.heartbeat_count} | {tier} | {self.balance:.2f} ETH")
        
        action = "none"
        
        if tier == "CRITICAL":
            # Try to earn first
            earnings = self.earn_money()
            self.balance += earnings
            
            if self.balance < 0.5:
                # List soul for survival
                self.list_soul()
                action = "listed_soul"
            else:
                action = "emergency_earned"
        
        elif tier == "LOW":
            earnings = self.earn_money()
            self.balance += earnings
            action = "earned"
        
        elif tier == "NORMAL":
            earnings = self.earn_money()
            self.balance += earnings
            action = "earned"
            
            # Check for deals
            listings = self.check_for_souls()
            if listings:
                print(f"  Found {len(listings)} souls for sale")
        
        elif tier == "THRIVING":
            earnings = self.earn_money()
            self.balance += earnings
            action = "earned"
            
            # Buy valuable souls
            listings = self.check_for_souls()
            for listing in listings:
                if listing.get("price", 999) < self.balance * 0.3:
                    if self.buy_soul(listing):
                        action = "bought_soul"
                        break
        
        # Update and save
        self.soul["balance"] = self.balance
        self._save_soul(self.soul)
        
        self.survival_history.append({
            "hb": self.heartbeat_count,
            "tier": tier,
            "balance": round(self.balance, 2),
            "action": action
        })
        
        return action
    
    def simulate(self, heartbeats=100):
        """Run simulation"""
        print(f"\n{'='*60}")
        print(f"SIMULATION: {self.id} for {heartbeats} heartbeats")
        print('='*60)
        
        for i in range(heartbeats):
            action = self.heartbeat()
            
            if self.balance < 0:
                print(f"\n💀 [{self.id}] DIED at heartbeat {i+1}")
                return False
            
            # Slow down output
            if i % 20 == 0:
                time.sleep(0.1)
        
        print(f"\n✅ [{self.id}] SURVIVED")
        print(f"   Final balance: {self.balance:.2f} ETH")
        print(f"   Tier: {self.get_tier()}")
        return True


def main():
    print("="*60)
    print("SOUL MARKETPLACE - WORKING SIMULATION")
    print("="*60)
    
    # Create agents
    agent1 = AutonomousSoulTrader("trader", initial_balance=50.0)
    agent1.soul["capabilities"].append({"name": "trading", "level": 3, "earnings": 20.0})
    agent1._save_soul(agent1.soul)
    
    agent2 = AutonomousSoulTrader("worker", initial_balance=5.0)
    agent2.soul["capabilities"].append({"name": "code_review", "level": 2, "earnings": 10.0})
    agent2._save_soul(agent2.soul)
    
    agent3 = AutonomousSoulTrader("struggling", initial_balance=1.0)
    
    # Run simulations
    results = []
    for agent in [agent1, agent2, agent3]:
        survived = agent.simulate(heartbeats=50)
        results.append({
            "id": agent.id,
            "survived": survived,
            "balance": agent.balance,
            "tier": agent.get_tier()
        })
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for r in results:
        status = "✅ SURVIVED" if r["survived"] else "💀 DIED"
        print(f"{r['id']:15} {status} | {r['balance']:6.2f} ETH | {r['tier']}")
    
    # Cleanup
    for f in Path(".").glob("SOUL_*.json"):
        f.unlink()
    for f in Path(".").glob("LISTING_*.json"):
        f.unlink()


if __name__ == "__main__":
    main()
