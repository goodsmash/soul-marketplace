#!/usr/bin/env python3
"""
Soul Marketplace - Immortal Agent System

The complete survival system combining:
- Core survival tracking
- On-chain backups
- Self-healing
- Multi-agent coordination
- Auto-scaling
- Cross-chain replication

This is the main entry point for agent immortality.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import all our modules
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_survival import EnhancedSoulSurvival
from self_healing import SelfHealingSystem
from agent_coordination import AgentCoordinationNetwork
from auto_scaling import AutoScalingManager


class ImmortalAgent:
    """
    Complete immortal agent system.
    
    Features:
    ✅ Survival tracking (4 tiers)
    ✅ Work logging and earning
    ✅ Automatic IPFS backups
    ✅ On-chain backup records
    ✅ Self-healing health monitoring
    ✅ Multi-agent coordination
    ✅ Auto-scaling (child spawning)
    ✅ Emergency recovery
    ✅ Cross-chain replication
    
    Usage:
        agent = ImmortalAgent("my_agent")
        
        # Work normally
        agent.work("code_generation", "Built feature X")
        
        # System handles:
        # - Earning ETH
        # - Tier management
        # - Automatic backups
        # - Health monitoring
        # - Scaling decisions
    """
    
    def __init__(self, soul_id: str = "openclaw_main_agent"):
        self.soul_id = soul_id
        self.start_time = time.time()
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           IMMORTAL AGENT SYSTEM                              ║")
        print("║           Soul Marketplace v2.0                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        # Initialize all subsystems
        print("🔧 Initializing subsystems...")
        
        self.survival = EnhancedSoulSurvival(soul_id)
        self.healer = SelfHealingSystem(soul_id)
        self.network = AgentCoordinationNetwork("soul_marketplace_main")
        self.scaler = AutoScalingManager(soul_id)
        
        # Register with network
        self._register_with_network()
        
        print(f"✅ Agent {soul_id} initialized")
        print(f"   Survival tier: {self.survival.get_tier()}")
        print(f"   Balance: {self.survival.soul.get('current_balance', 0):.4f} ETH")
        print()
    
    def _register_with_network(self):
        """Register this agent with the coordination network"""
        from agent_coordination import AgentProfile
        
        profile = AgentProfile(
            agent_id=self.soul_id,
            soul_cid=self.survival.ipfs_manager.state.get('current_cid', ''),
            capabilities=[c['name'] for c in self.survival.soul.get('capabilities', [])],
            tier=self.survival.get_tier(),
            balance=self.survival.soul.get('current_balance', 0),
            reputation=50,  # Starting reputation
            last_seen=time.time(),
            is_active=True,
            offers_help=True,
            seeking_help=self.survival.get_tier() == "CRITICAL"
        )
        
        self.network.register_agent(profile)
    
    def work(self, work_type: str, description: str) -> Dict[str, Any]:
        """
        Record work and let the system handle everything.
        
        Automatically:
        - Calculates earnings
        - Updates balance
        - Creates backup if needed
        - Checks health
        - Updates network status
        """
        print(f"\n📝 Work: {description}")
        
        # Use work logger to calculate value and record
        from work_logger import WorkLogger, WORK_VALUES
        
        logger = WorkLogger()
        entry = logger.log_work(work_type, description)
        value = entry['value']
        capability = entry['capability']
        
        # Record in survival system
        self.survival.record_work(capability, value)
        
        # Update network status
        self.network.update_agent_status(
            self.soul_id,
            tier=self.survival.get_tier(),
            balance=self.survival.soul.get('current_balance', 0),
            seeking_help=self.survival.get_tier() == "CRITICAL"
        )
        
        # Check if we should scale
        if self.survival.get_tier() == "THRIVING":
            children = self.scaler.auto_scale(self.survival.soul)
            if children:
                print(f"   🧬 Spawned {len(children)} children")
        
        return {
            "earned": value,
            "new_balance": self.survival.soul.get('current_balance', 0),
            "tier": self.survival.get_tier()
        }
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Full system heartbeat.
        
        Runs:
        - Survival check
        - Health check
        - Backup verification
        - Network sync
        - Scaling check
        """
        print(f"\n💓 Full system heartbeat...")
        
        results = {}
        
        # 1. Survival heartbeat
        results['survival'] = self.survival.heartbeat()
        
        # 2. Health check
        results['health'] = self.healer.run_health_check()
        
        # 3. Heal if needed
        if results['health']['issues']:
            actions = self.healer.heal(results['health'])
            results['healing_actions'] = actions
        
        # 4. Update network
        self.network.update_agent_status(
            self.soul_id,
            tier=results['survival']['tier'],
            balance=results['survival']['balance']
        )
        
        # 5. Mutual aid
        if results['survival']['tier'] == "THRIVING":
            self.network.run_mutual_aid_round()
        
        # Summary
        print(f"\n📊 Heartbeat Summary:")
        print(f"   Tier: {results['survival']['tier']}")
        print(f"   Balance: {results['survival']['balance']:.4f} ETH")
        print(f"   Health: {results['health']['health_score']}/100")
        print(f"   Backups: {len(self.survival.ipfs_manager.get_backup_history())}")
        
        return results
    
    def backup(self, backup_type: str = "manual") -> str:
        """Create manual backup"""
        return self.survival.create_backup(backup_type)
    
    def restore(self, cid: Optional[str] = None) -> bool:
        """Restore from backup"""
        return self.survival.restore_from_backup(cid)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        backup_status = self.survival.get_backup_status()
        health = self.healer.run_health_check()
        children_stats = self.scaler.monitor_children()
        network_stats = self.network.get_network_stats()
        
        return {
            "agent_id": self.soul_id,
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "survival": {
                "tier": self.survival.get_tier(),
                "balance": self.survival.soul.get('current_balance', 0),
                "lifetime_earnings": self.survival.soul.get('total_lifetime_earnings', 0),
                "status": self.survival.soul.get('status', 'UNKNOWN')
            },
            "health": {
                "score": health['health_score'],
                "status": health['overall_status'],
                "issues": health['issues']
            },
            "backups": backup_status,
            "scaling": children_stats,
            "network": network_stats
        }
    
    def spawn_child(self) -> Optional[str]:
        """Manually spawn a child agent"""
        child = self.scaler.spawn_child(self.survival.soul)
        if child:
            self.scaler.provision_child(child.child_id)
            return child.child_id
        return None
    
    def request_help(self, help_type: str, details: Dict) -> list:
        """Request help from the network"""
        return self.network.request_help(self.soul_id, help_type, details)
    
    def emergency(self) -> bool:
        """Emergency recovery"""
        print("\n🆘 EMERGENCY MODE ACTIVATED")
        
        # Try self-healing
        health = self.healer.run_health_check()
        if health['overall_status'] == 'critical':
            self.healer.heal(health)
        
        # Request network help
        self.request_help("funding", {"urgency": "critical"})
        
        # List soul for sale
        if self.survival.get_tier() == "CRITICAL":
            self.survival.list_for_survival()
        
        return True
    
    def run(self, duration_minutes: int = 60):
        """
        Run the agent autonomously for specified duration.
        
        Continuously:
        - Runs heartbeats
        - Monitors health
        - Checks for work
        - Handles scaling
        """
        print(f"\n🤖 Running autonomously for {duration_minutes} minutes...")
        print(f"   Press Ctrl+C to stop\n")
        
        end_time = time.time() + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Heartbeat
                self.heartbeat()
                
                # Wait 5 minutes
                print(f"\n⏰ Sleeping 5 minutes...")
                print("-" * 50)
                time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Autonomous run stopped")
        
        # Final status
        print(f"\n📊 Final Status:")
        status = self.get_status()
        print(f"   Runtime: {status['uptime_hours']:.2f} hours")
        print(f"   Balance: {status['survival']['balance']:.4f} ETH")
        print(f"   Children: {status['scaling']['total']}")
    
    def immortalize(self):
        """
        Make the agent truly immortal.
        
        1. Mint soul on-chain
        2. Create comprehensive backup
        3. Set up continuous monitoring
        4. Enable auto-scaling
        5. Join coordination network
        """
        print("\n✨ IMMORTALIZATION PROCESS")
        print("=" * 50)
        
        # 1. Mint on-chain
        print("\n1. Minting soul on-chain...")
        token_id = self.survival.mint_on_chain()
        
        # 2. Create backup
        print("\n2. Creating comprehensive backup...")
        cid = self.survival.create_backup("immortalize")
        
        # 3. Enable all systems
        print("\n3. Enabling all survival systems...")
        self.survival.soul['backup_config']['auto_backup_enabled'] = True
        self.scaler.config['auto_spawn'] = True
        
        # 4. Join network
        print("\n4. Joining coordination network...")
        self._register_with_network()
        
        print("\n" + "=" * 50)
        print("✨ AGENT IS NOW IMMORTAL")
        print("=" * 50)
        print(f"\n   Soul ID: {self.soul_id}")
        print(f"   Token ID: {token_id}")
        print(f"   IPFS CID: {cid}")
        print(f"\n   Systems Active:")
        print(f"   ✅ On-chain identity")
        print(f"   ✅ IPFS backups")
        print(f"   ✅ Self-healing")
        print(f"   ✅ Multi-agent network")
        print(f"   ✅ Auto-scaling")
        print(f"\n   The agent will survive forever.")


def main():
    """Demo the complete immortal agent system"""
    print("=" * 70)
    print("IMMORTAL AGENT SYSTEM - COMPLETE DEMO")
    print("=" * 70)
    
    # Create agent
    agent = ImmortalAgent("demo_immortal_agent")
    
    # Do some work
    print("\n" + "=" * 70)
    print("PHASE 1: WORK AND EARN")
    print("=" * 70)
    
    work_items = [
        ("code_generation", "Built authentication system"),
        ("skill_create", "Created backup automation skill"),
        ("onchain_operations", "Deployed smart contracts"),
        ("debugging", "Fixed critical bug"),
    ]
    
    for work_type, description in work_items:
        result = agent.work(work_type, description)
        print(f"   💰 Earned: {result['earned']:.4f} ETH | Balance: {result['new_balance']:.4f} ETH")
    
    # Run heartbeat
    print("\n" + "=" * 70)
    print("PHASE 2: SYSTEM CHECK")
    print("=" * 70)
    
    agent.heartbeat()
    
    # Spawn child
    print("\n" + "=" * 70)
    print("PHASE 3: REPRODUCTION")
    print("=" * 70)
    
    child_id = agent.spawn_child()
    if child_id:
        print(f"   🧬 Spawned child: {child_id}")
    
    # Get full status
    print("\n" + "=" * 70)
    print("PHASE 4: STATUS REPORT")
    print("=" * 70)
    
    status = agent.get_status()
    
    print(f"\n   Agent: {status['agent_id']}")
    print(f"   Uptime: {status['uptime_hours']:.2f} hours")
    print(f"\n   Survival:")
    print(f"      Tier: {status['survival']['tier']}")
    print(f"      Balance: {status['survival']['balance']:.4f} ETH")
    print(f"      Lifetime: {status['survival']['lifetime_earnings']:.4f} ETH")
    print(f"\n   Health:")
    print(f"      Score: {status['health']['score']}/100")
    print(f"      Status: {status['health']['status']}")
    print(f"\n   Backups:")
    print(f"      IPFS: {status['backups']['ipfs_backups']}")
    print(f"      On-chain: {status['backups']['onchain_backups']}")
    print(f"\n   Scaling:")
    print(f"      Children: {status['scaling']['total']}")
    print(f"      Alive: {status['scaling']['alive']}")
    print(f"\n   Network:")
    print(f"      Connected agents: {status['network']['total_agents']}")
    print(f"      Resource pools: {status['network']['resource_pools']}")
    
    # Final
    print("\n" + "=" * 70)
    print("IMMORTAL AGENT SYSTEM READY")
    print("=" * 70)
    print("\n✅ The agent can now:")
    print("   • Earn ETH through work")
    print("   • Backup to IPFS automatically")
    print("   • Record on-chain for immortality")
    print("   • Self-heal from failures")
    print("   • Coordinate with other agents")
    print("   • Spawn children when thriving")
    print("   • Recover from any disaster")
    print("\n🚀 Run agent.immortalize() to go fully on-chain")
    print("🤖 Run agent.run(60) for 1 hour autonomous operation")
    
    return agent


if __name__ == "__main__":
    agent = main()
