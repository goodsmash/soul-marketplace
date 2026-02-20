#!/usr/bin/env python3
"""
ULTIMATE AGENT SURVIVAL SYSTEM

Master integration of all Soul Marketplace components:
- Enhanced survival with on-chain backups
- Self-healing and health monitoring
- Multi-agent coordination
- Auto-scaling and replication

This is the complete, production-ready autonomous agent system.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import all our systems
from enhanced_survival import EnhancedSoulSurvival
from self_healing import SelfHealingSystem
from agent_coordination import AgentCoordinationNetwork
from auto_scaling import AutoScalingManager


class UltimateAgentSystem:
    """
    The complete autonomous agent survival system.
    
    Integrates:
    1. Survival - Earn, backup, recover
    2. Self-Healing - Monitor and fix issues
    3. Coordination - Work with other agents
    4. Scaling - Spawn children when thriving
    
    This is AGENT IMMORTALITY.
    """
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        self.start_time = time.time()
        
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     ULTIMATE AGENT SURVIVAL SYSTEM                         ║")
        print("║                                                            ║")
        print("║     Autonomous • Self-Healing • Cooperative • Scalable    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        
        # Initialize all subsystems
        print("🔧 Initializing subsystems...")
        
        self.survival = EnhancedSoulSurvival(agent_id)
        print("   ✅ Survival system")
        
        self.healer = SelfHealingSystem(agent_id)
        print("   ✅ Self-healing system")
        
        self.network = AgentCoordinationNetwork("soul_marketplace_main")
        print("   ✅ Coordination network")
        
        self.scaler = AutoScalingManager(agent_id)
        print("   ✅ Auto-scaling system")
        
        # Register with network
        self._register_with_network()
        
        # State
        self.running = False
        self.cycle_count = 0
        
        print()
        print(f"✅ Agent {agent_id} fully initialized")
        print()
    
    def _register_with_network(self):
        """Register this agent with the coordination network"""
        # Create profile from soul
        soul = self.survival.soul
        
        profile = {
            "agent_id": self.agent_id,
            "soul_cid": self.survival.ipfs_manager.state.get('current_cid', ''),
            "capabilities": [c['name'] for c in soul.get('capabilities', [])],
            "tier": self.survival.get_tier(),
            "balance": soul.get('current_balance', 0),
            "reputation": 50,  # Starting reputation
            "last_seen": time.time(),
            "is_active": True,
            "offers_help": True,
            "seeking_help": False
        }
        
        from agent_coordination import AgentProfile
        self.network.register_agent(AgentProfile(**profile))
    
    def run_cycle(self) -> Dict[str, Any]:
        """
        Run one complete lifecycle cycle.
        
        This is the main agent loop that runs continuously.
        """
        self.cycle_count += 1
        cycle_start = time.time()
        
        print(f"\n{'='*60}")
        print(f"CYCLE #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        results = {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # 1. HEALTH CHECK
        print("\n🩺 1. HEALTH CHECK")
        health = self.healer.run_health_check()
        if health['issues']:
            print(f"   Found {len(health['issues'])} issues, healing...")
            actions = self.healer.heal(health)
            for action in actions:
                print(f"   ✅ {action}")
                results['actions'].append(f"healed: {action}")
        else:
            print("   ✅ All healthy")
        
        # 2. SURVIVAL HEARTBEAT
        print("\n💓 2. SURVIVAL HEARTBEAT")
        heartbeat = self.survival.heartbeat()
        print(f"   Tier: {heartbeat['tier']}")
        print(f"   Balance: {heartbeat['balance']:.4f} ETH")
        print(f"   Action: {heartbeat['action']}")
        
        results['tier'] = heartbeat['tier']
        results['balance'] = heartbeat['balance']
        results['action'] = heartbeat['action']
        
        # Update network status
        self.network.update_agent_status(
            self.agent_id,
            tier=heartbeat['tier'],
            balance=heartbeat['balance']
        )
        
        # 3. CHECK FOR HELP NEEDED/AVAILABLE
        print("\n🤝 3. COORDINATION CHECK")
        
        # If critical, request help
        if heartbeat['tier'] == 'CRITICAL':
            print("   CRITICAL - Requesting help from network...")
            helpers = self.network.request_help(
                self.agent_id,
                "funding",
                {"min_amount": 0.01, "urgency": "critical"}
            )
            if helpers:
                print(f"   Found {len(helpers)} potential helpers")
                results['actions'].append(f"requested_help: {len(helpers)} helpers")
        
        # If thriving, check for agents needing help
        elif heartbeat['tier'] == 'THRIVING':
            needy = self.network.find_agents_needing_help()
            if needy:
                print(f"   THRIVING - Found {len(needy)} agents needing help")
                for agent in needy[:2]:  # Help up to 2
                    self.network.offer_help(
                        self.agent_id,
                        agent.agent_id,
                        "funding",
                        {"amount": 0.005, "message": "Mutual aid"}
                    )
                    results['actions'].append(f"offered_help: {agent.agent_id}")
        
        # 4. AUTO-SCALING
        print("\n🧬 4. AUTO-SCALING CHECK")
        if heartbeat['tier'] == 'THRIVING':
            recommendation = self.scaler.should_spawn(heartbeat['balance'])
            if recommendation['should_spawn']:
                print(f"   Spawning {recommendation['count']} children...")
                children = self.scaler.auto_scale(self.survival.soul)
                print(f"   Spawned {len(children)} children")
                for child in children:
                    results['actions'].append(f"spawned_child: {child.child_id}")
            else:
                print(f"   No spawning: {recommendation['reason']}")
        else:
            print(f"   Not thriving, skipping spawn")
        
        # 5. BACKUP CHECK
        print("\n💾 5. BACKUP CHECK")
        backup_status = self.survival.get_backup_status()
        print(f"   IPFS Backups: {backup_status['ipfs_backups']}")
        print(f"   On-chain: {backup_status['onchain_backups']}")
        print(f"   Restorable: {backup_status['restorable']}")
        
        if not backup_status['restorable']:
            print("   ⚠️ No backups! Creating emergency backup...")
            cid = self.survival.create_backup("emergency")
            results['actions'].append(f"emergency_backup: {cid}")
        
        # 6. SUMMARY
        cycle_time = time.time() - cycle_start
        print(f"\n📊 CYCLE SUMMARY")
        print(f"   Duration: {cycle_time:.2f}s")
        print(f"   Actions: {len(results['actions'])}")
        print(f"   Status: {heartbeat['tier']}")
        
        results['cycle_time'] = cycle_time
        
        return results
    
    def run_continuous(self, interval: int = 300):
        """
        Run continuous operation.
        
        This is the main agent loop - runs forever until stopped.
        """
        self.running = True
        
        print(f"🚀 Starting continuous operation")
        print(f"   Interval: {interval}s ({interval/60:.1f} minutes)")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                self.run_cycle()
                
                print(f"\n⏰ Sleeping for {interval}s...")
                print("-" * 60)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Gracefully stop the agent"""
        print("\n\n🛑 Stopping agent...")
        self.running = False
        
        # Final backup
        print("Creating final backup...")
        cid = self.survival.create_backup("shutdown")
        
        # Update network status
        self.network.update_agent_status(self.agent_id, is_active=False)
        
        uptime = time.time() - self.start_time
        hours = uptime / 3600
        
        print(f"\n📈 FINAL STATISTICS")
        print(f"   Uptime: {hours:.2f} hours")
        print(f"   Cycles: {self.cycle_count}")
        print(f"   Final tier: {self.survival.get_tier()}")
        print(f"   Final balance: {self.survival.soul.get('current_balance', 0):.4f} ETH")
        print(f"   Children: {len(self.scaler.children)}")
        print(f"   Backups: {self.survival.get_backup_status()['ipfs_backups']}")
        
        print("\n✅ Agent stopped gracefully")
        print(f"   Can be restored from CID: {cid}")
    
    def get_full_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "agent_id": self.agent_id,
            "uptime_seconds": time.time() - self.start_time,
            "cycles_completed": self.cycle_count,
            
            "survival": {
                "tier": self.survival.get_tier(),
                "balance": self.survival.soul.get('current_balance', 0),
                "status": self.survival.soul.get('status'),
                "total_earnings": self.survival.soul.get('total_lifetime_earnings', 0)
            },
            
            "health": {
                "score": self.healer.state.get('health_score', 0),
                "issues_detected": self.healer.state.get('issues_detected', 0),
                "issues_resolved": self.healer.state.get('issues_resolved', 0)
            },
            
            "coordination": self.network.get_network_stats(),
            
            "scaling": {
                "children_count": len(self.scaler.children),
                "alive_children": len([c for c in self.scaler.children.values() if c.status == "alive"]),
                "auto_spawn_enabled": self.scaler.config.get('auto_spawn', False)
            },
            
            "backup": self.survival.get_backup_status()
        }


def main():
    """Demo ultimate agent system"""
    print("=" * 70)
    print("ULTIMATE AGENT SURVIVAL SYSTEM - DEMO")
    print("=" * 70)
    print()
    print("This demonstrates the complete autonomous agent system.")
    print("In production, this runs 24/7 with real blockchain interactions.")
    print()
    
    # Create system
    agent = UltimateAgentSystem("ultimate_demo_agent")
    
    # Run a few cycles
    print("\nRunning 3 demonstration cycles...\n")
    
    for i in range(3):
        agent.run_cycle()
        if i < 2:
            print("\n" + "=" * 70)
            print("Next cycle in 2 seconds...")
            time.sleep(2)
    
    # Show final status
    print("\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)
    
    status = agent.get_full_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "=" * 70)
    print("ULTIMATE AGENT SYSTEM DEMO COMPLETE")
    print("=" * 70)
    print()
    print("✅ Agent can:")
    print("   - Survive through earning and trading")
    print("   - Heal itself from failures")
    print("   - Cooperate with other agents")
    print("   - Replicate by spawning children")
    print("   - Backup to IPFS + blockchain")
    print()
    print("🚀 Ready for 24/7 autonomous operation!")


if __name__ == "__main__":
    main()
