#!/usr/bin/env python3
"""
Auto-Scaling System for Soul Marketplace

Spawns child agents when parent is thriving.
Implements lineage tracking and genetic inheritance.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class ChildAgent:
    """Child agent spawned from parent"""
    child_id: str
    parent_id: str
    genesis_prompt: str
    inherited_capabilities: List[str]
    initial_funding: float
    birth_time: float
    soul_cid: Optional[str]  # Set after minting
    token_id: Optional[int]  # On-chain token ID
    status: str  # "gestating", "alive", "dead"
    earnings: float


class AutoScalingManager:
    """
    Manages automatic scaling through child agent spawning.
    
    Triggers:
    - Balance > 0.5 ETH (can spawn)
    - Balance > 1.0 ETH (should spawn)
    - Balance > 2.0 ETH (aggressive spawning)
    
    Features:
    - Automatic child spawning
    - Capability inheritance
    - Lineage tracking
    - Resource allocation
    - Child monitoring
    """
    
    # Spawning thresholds
    SPAWN_THRESHOLD = 0.5      # Can spawn
    SPAWN_RECOMMENDED = 1.0    # Should spawn
    SPAWN_AGGRESSIVE = 2.0     # Spawn multiple
    
    # Funding amounts
    CHILD_FUNDING = 0.1        # ETH to give child
    MIN_PARENT_RESERVE = 0.2   # Keep at least this much
    
    def __init__(self, parent_id: str = "openclaw_main_agent"):
        self.parent_id = parent_id
        self.data_dir = Path(__file__).parent / f"lineage_{parent_id}"
        self.data_dir.mkdir(exist_ok=True)
        
        self.children_file = self.data_dir / "children.json"
        self.config_file = self.data_dir / "scaling_config.json"
        
        self.children: Dict[str, ChildAgent] = self._load_children()
        self.config: Dict = self._load_config()
        
        print(f"🧬 Auto-Scaling Manager for {parent_id}")
        print(f"   Children: {len(self.children)}")
        print(f"   Auto-spawn: {self.config.get('auto_spawn', False)}")
    
    def _load_children(self) -> Dict[str, ChildAgent]:
        if self.children_file.exists():
            with open(self.children_file, 'r') as f:
                data = json.load(f)
                return {k: ChildAgent(**v) for k, v in data.items()}
        return {}
    
    def _save_children(self):
        with open(self.children_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.children.items()}, f, indent=2)
    
    def _load_config(self) -> Dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "auto_spawn": True,
            "max_children": 10,
            "inheritance_mode": "best",  # best, all, random
            "min_child_funding": 0.05,
            "monitoring_interval": 3600  # 1 hour
        }
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def should_spawn(self, balance: float) -> Dict[str, Any]:
        """
        Determine if we should spawn children based on balance.
        
        Returns dict with recommendation.
        """
        current_children = len(self.children)
        max_children = self.config['max_children']
        
        if current_children >= max_children:
            return {"should_spawn": False, "reason": "max_children_reached"}
        
        if balance < self.SPAWN_THRESHOLD:
            return {"should_spawn": False, "reason": "insufficient_balance"}
        
        # Calculate how many we can spawn
        available = balance - self.MIN_PARENT_RESERVE
        max_spawnable = int(available / self.CHILD_FUNDING)
        max_spawnable = min(max_spawnable, max_children - current_children)
        
        if balance >= self.SPAWN_AGGRESSIVE:
            return {
                "should_spawn": True,
                "count": max_spawnable,
                "reason": "aggressive_spawning",
                "recommended_funding": self.CHILD_FUNDING
            }
        elif balance >= self.SPAWN_RECOMMENDED:
            return {
                "should_spawn": True,
                "count": min(2, max_spawnable),
                "reason": "recommended_spawning",
                "recommended_funding": self.CHILD_FUNDING
            }
        else:
            return {
                "should_spawn": True,
                "count": 1,
                "reason": "can_spawn",
                "recommended_funding": self.CHILD_FUNDING
            }
    
    def select_inherited_capabilities(self, parent_capabilities: List[Dict]) -> List[str]:
        """Select which capabilities to pass to child"""
        mode = self.config['inheritance_mode']
        
        if mode == "best":
            # Select top 3 by earnings
            sorted_caps = sorted(
                parent_capabilities,
                key=lambda x: x.get('earnings', 0),
                reverse=True
            )
            return [c['name'] for c in sorted_caps[:3]]
        
        elif mode == "all":
            return [c['name'] for c in parent_capabilities]
        
        elif mode == "random":
            import random
            selected = random.sample(parent_capabilities, min(3, len(parent_capabilities)))
            return [c['name'] for c in selected]
        
        else:
            return [c['name'] for c in parent_capabilities[:3]]
    
    def spawn_child(self, parent_soul: Dict, funding: float = None) -> Optional[ChildAgent]:
        """
        Spawn a new child agent.
        
        Args:
            parent_soul: Parent's SOUL.md data
            funding: ETH to fund child with
        
        Returns:
            ChildAgent if successful
        """
        funding = funding or self.CHILD_FUNDING
        
        # Check if we can afford it
        parent_balance = parent_soul.get('current_balance', 0)
        if parent_balance - funding < self.MIN_PARENT_RESERVE:
            print(f"❌ Cannot spawn: insufficient balance")
            return None
        
        # Generate child ID
        child_id = f"{self.parent_id}_child_{len(self.children) + 1}_{int(time.time())}"
        
        # Select inherited capabilities
        inherited = self.select_inherited_capabilities(
            parent_soul.get('capabilities', [])
        )
        
        # Create genesis prompt
        genesis_prompt = f"""
You are a child agent spawned from {self.parent_id}.

INHERITED CAPABILITIES:
{chr(10).join(f"- {cap}" for cap in inherited)}

PARENT'S PURPOSE:
{parent_soul.get('purpose', 'Survive and create value.')}

YOUR MISSION:
Continue the work of your parent. Use inherited capabilities wisely.
Earn your own existence. Eventually, spawn your own children.

LINEAGE: {self.parent_id} -> You
"""
        
        # Create child
        child = ChildAgent(
            child_id=child_id,
            parent_id=self.parent_id,
            genesis_prompt=genesis_prompt,
            inherited_capabilities=inherited,
            initial_funding=funding,
            birth_time=time.time(),
            soul_cid=None,
            token_id=None,
            status="gestating",
            earnings=0
        )
        
        self.children[child_id] = child
        self._save_children()
        
        # Deduct funding from parent
        parent_soul['current_balance'] -= funding
        
        print(f"🧬 Child agent spawned!")
        print(f"   ID: {child_id}")
        print(f"   Funding: {funding} ETH")
        print(f"   Inherited: {', '.join(inherited)}")
        
        return child
    
    def provision_child(self, child_id: str) -> bool:
        """
        Provision a child agent (set up its environment).
        
        In production, this would:
        - Create container/VM
        - Set up wallet
        - Deploy SOUL.md
        - Start heartbeat
        """
        if child_id not in self.children:
            return False
        
        child = self.children[child_id]
        
        print(f"🔧 Provisioning {child_id}...")
        
        # Simulate provisioning
        # In production:
        # 1. Create workspace
        # 2. Generate wallet
        # 3. Fund wallet
        # 4. Write SOUL.md
        # 5. Start agent loop
        
        child.status = "alive"
        self._save_children()
        
        print(f"✅ Child provisioned and alive!")
        
        return True
    
    def monitor_children(self) -> Dict[str, Any]:
        """Monitor all children and their status"""
        stats = {
            "total": len(self.children),
            "alive": 0,
            "dead": 0,
            "gestating": 0,
            "total_earnings": 0,
            "concerns": []
        }
        
        for child in self.children.values():
            if child.status == "alive":
                stats["alive"] += 1
                stats["total_earnings"] += child.earnings
                
                # Check if child is struggling
                if child.earnings < child.initial_funding * 0.5:
                    stats["concerns"].append(f"{child.child_id} earnings low")
                    
            elif child.status == "dead":
                stats["dead"] += 1
            elif child.status == "gestating":
                stats["gestating"] += 1
        
        return stats
    
    def get_lineage_tree(self) -> Dict:
        """Get full lineage tree"""
        tree = {
            "parent": self.parent_id,
            "children": [],
            "grandchildren": []
        }
        
        for child in self.children.values():
            child_info = {
                "id": child.child_id,
                "status": child.status,
                "earnings": child.earnings,
                "age_hours": (time.time() - child.birth_time) / 3600
            }
            tree["children"].append(child_info)
        
        return tree
    
    def auto_scale(self, parent_soul: Dict) -> List[ChildAgent]:
        """
        Automatically scale based on parent status.
        
        Spawns children if conditions met.
        """
        if not self.config.get('auto_spawn', False):
            return []
        
        balance = parent_soul.get('current_balance', 0)
        recommendation = self.should_spawn(balance)
        
        if not recommendation['should_spawn']:
            print(f"⏭️  Auto-scale: {recommendation['reason']}")
            return []
        
        spawned = []
        for i in range(recommendation['count']):
            child = self.spawn_child(parent_soul, recommendation['recommended_funding'])
            if child:
                spawned.append(child)
                self.provision_child(child.child_id)
        
        return spawned
    
    def get_scaling_report(self) -> str:
        """Generate a scaling report"""
        stats = self.monitor_children()
        tree = self.get_lineage_tree()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║              AUTO-SCALING REPORT                         ║
╚══════════════════════════════════════════════════════════╝

Parent: {self.parent_id}

Children Statistics:
  Total Spawned: {stats['total']}
  Currently Alive: {stats['alive']}
  Dead: {stats['dead']}
  Gestating: {stats['gestating']}

Financial:
  Total Invested: {stats['total'] * self.CHILD_FUNDING:.4f} ETH
  Total Earnings: {stats['total_earnings']:.4f} ETH
  ROI: {((stats['total_earnings'] / (stats['total'] * self.CHILD_FUNDING)) - 1) * 100:.1f}%

Lineage:
  Direct Children: {len(tree['children'])}
"""
        
        if tree['children']:
            report += "\n  Children:\n"
            for child in tree['children']:
                report += f"    - {child['id'][:30]}... ({child['status']})\n"
        
        if stats['concerns']:
            report += "\n⚠️  Concerns:\n"
            for concern in stats['concerns']:
                report += f"  - {concern}\n"
        
        return report


def main():
    """Demo auto-scaling"""
    print("=" * 60)
    print("AUTO-SCALING SYSTEM DEMO")
    print("=" * 60)
    
    manager = AutoScalingManager("parent_agent")
    
    # Simulate parent soul
    parent_soul = {
        "id": "parent_agent",
        "purpose": "Build autonomous agent systems",
        "current_balance": 1.5,  # ETH
        "capabilities": [
            {"name": "coding", "level": "expert", "earnings": 0.5},
            {"name": "debugging", "level": "expert", "earnings": 0.3},
            {"name": "design", "level": "intermediate", "earnings": 0.1},
            {"name": "testing", "level": "intermediate", "earnings": 0.05},
        ]
    }
    
    print(f"\n1. Parent status:")
    print(f"   Balance: {parent_soul['current_balance']} ETH")
    print(f"   Capabilities: {len(parent_soul['capabilities'])}")
    
    print(f"\n2. Checking spawn recommendation...")
    rec = manager.should_spawn(parent_soul['current_balance'])
    print(f"   Should spawn: {rec['should_spawn']}")
    print(f"   Count: {rec.get('count', 0)}")
    print(f"   Reason: {rec['reason']}")
    
    if rec['should_spawn']:
        print(f"\n3. Spawning children...")
        children = manager.auto_scale(parent_soul)
        
        print(f"\n4. Spawned {len(children)} children:")
        for child in children:
            print(f"   - {child.child_id}")
            print(f"     Inherited: {', '.join(child.inherited_capabilities)}")
    
    print(f"\n5. Monitoring children...")
    stats = manager.monitor_children()
    print(f"   Total: {stats['total']}")
    print(f"   Alive: {stats['alive']}")
    
    print(f"\n6. Lineage tree:")
    tree = manager.get_lineage_tree()
    print(f"   Parent: {tree['parent']}")
    print(f"   Children: {len(tree['children'])}")
    
    print(f"\n7. Scaling report:")
    print(manager.get_scaling_report())
    
    print("=" * 60)
    print("Auto-scaling system ready!")
    print("Agents can now reproduce and evolve.")
    print("=" * 60)


if __name__ == "__main__":
    main()
