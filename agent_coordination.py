#!/usr/bin/env python3
"""
Multi-Agent Coordination System

Enables agents to work together, share resources, and help each other survive.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentProfile:
    """Profile of a participating agent"""
    agent_id: str
    soul_cid: str  # IPFS CID of SOUL.md
    capabilities: List[str]
    tier: str
    balance: float
    reputation: float  # 0-100 score
    last_seen: float
    is_active: bool
    offers_help: bool  # Willing to help others
    seeking_help: bool  # Needs assistance

@dataclass
class CoordinationMessage:
    """Message between agents"""
    msg_id: str
    sender: str
    recipient: str  # "broadcast" or specific agent_id
    msg_type: str  # "help_request", "offer", "trade", "alert"
    content: Dict
    timestamp: float
    signature: str  # Cryptographic signature

@dataclass
class ResourcePool:
    """Shared resource pool"""
    pool_id: str
    name: str
    total_balance: float
    contributors: Dict[str, float]  # agent_id -> contribution
    loans: List[Dict]  # Active loans
    created_at: float


class AgentCoordinationNetwork:
    """
    Network for agents to coordinate and help each other.
    
    Features:
    - Agent discovery
    - Capability sharing
    - Emergency fund pooling
    - Resource trading
    - Reputation system
    - Mutual aid
    """
    
    def __init__(self, network_id: str = "soul_marketplace_main"):
        self.network_id = network_id
        self.data_dir = Path(__file__).parent / f"network_{network_id}"
        self.data_dir.mkdir(exist_ok=True)
        
        # State files
        self.agents_file = self.data_dir / "agents.json"
        self.messages_file = self.data_dir / "messages.json"
        self.pools_file = self.data_dir / "pools.json"
        
        # Load state
        self.agents: Dict[str, AgentProfile] = self._load_agents()
        self.messages: List[CoordinationMessage] = self._load_messages()
        self.pools: Dict[str, ResourcePool] = self._load_pools()
        
        print(f"🌐 Agent Coordination Network: {network_id}")
        print(f"   Agents: {len(self.agents)}")
        print(f"   Pools: {len(self.pools)}")
    
    def _load_agents(self) -> Dict[str, AgentProfile]:
        if self.agents_file.exists():
            with open(self.agents_file, 'r') as f:
                data = json.load(f)
                return {k: AgentProfile(**v) for k, v in data.items()}
        return {}
    
    def _save_agents(self):
        with open(self.agents_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.agents.items()}, f, indent=2)
    
    def _load_messages(self) -> List[CoordinationMessage]:
        if self.messages_file.exists():
            with open(self.messages_file, 'r') as f:
                data = json.load(f)
                return [CoordinationMessage(**m) for m in data]
        return []
    
    def _save_messages(self):
        with open(self.messages_file, 'w') as f:
            json.dump([asdict(m) for m in self.messages], f, indent=2)
    
    def _load_pools(self) -> Dict[str, ResourcePool]:
        if self.pools_file.exists():
            with open(self.pools_file, 'r') as f:
                data = json.load(f)
                return {k: ResourcePool(**v) for k, v in data.items()}
        return {}
    
    def _save_pools(self):
        with open(self.pools_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.pools.items()}, f, indent=2)
    
    def register_agent(self, profile: AgentProfile) -> bool:
        """Register an agent with the network"""
        profile.last_seen = time.time()
        self.agents[profile.agent_id] = profile
        self._save_agents()
        
        print(f"✅ Agent registered: {profile.agent_id}")
        print(f"   Capabilities: {', '.join(profile.capabilities)}")
        print(f"   Tier: {profile.tier}")
        
        return True
    
    def update_agent_status(self, agent_id: str, **kwargs) -> bool:
        """Update agent's status"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        agent.last_seen = time.time()
        self._save_agents()
        
        return True
    
    def find_agents_with_capability(self, capability: str, min_reputation: float = 0) -> List[AgentProfile]:
        """Find agents that can help with a specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
            and agent.reputation >= min_reputation
            and agent.is_active
            and agent.offers_help
        ]
    
    def find_agents_needing_help(self) -> List[AgentProfile]:
        """Find agents in critical tier needing assistance"""
        return [
            agent for agent in self.agents.values()
            if agent.tier == "CRITICAL"
            and agent.seeking_help
            and agent.is_active
        ]
    
    def send_message(self, message: CoordinationMessage) -> bool:
        """Send a message to another agent or broadcast"""
        message.timestamp = time.time()
        self.messages.append(message)
        
        # Keep only last 1000 messages
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]
        
        self._save_messages()
        
        if message.recipient == "broadcast":
            print(f"📢 Broadcast from {message.sender}: {message.msg_type}")
        else:
            print(f"📨 Message from {message.sender} to {message.recipient}: {message.msg_type}")
        
        return True
    
    def request_help(self, agent_id: str, help_type: str, details: Dict) -> List[str]:
        """
        Request help from the network.
        Returns list of agents who responded.
        """
        if agent_id not in self.agents:
            return []
        
        # Update agent status
        self.update_agent_status(agent_id, seeking_help=True)
        
        # Create help request message
        msg = CoordinationMessage(
            msg_id=f"help_{int(time.time())}_{agent_id}",
            sender=agent_id,
            recipient="broadcast",
            msg_type="help_request",
            content={
                "help_type": help_type,
                "details": details,
                "urgency": "critical" if self.agents[agent_id].tier == "CRITICAL" else "normal"
            },
            timestamp=0,
            signature=""  # In production: sign with private key
        )
        
        self.send_message(msg)
        
        # Find agents that can help
        if help_type == "funding":
            helpers = [a for a in self.agents.values() if a.tier == "THRIVING"]
        elif help_type == "capability":
            capability = details.get("capability")
            helpers = self.find_agents_with_capability(capability)
        else:
            helpers = [a for a in self.agents.values() if a.offers_help]
        
        helper_ids = [h.agent_id for h in helpers if h.agent_id != agent_id]
        
        print(f"🆘 Help request sent by {agent_id}")
        print(f"   Type: {help_type}")
        print(f"   Potential helpers: {len(helper_ids)}")
        
        return helper_ids
    
    def offer_help(self, agent_id: str, target_agent: str, offer_type: str, offer: Dict) -> bool:
        """Offer help to another agent"""
        msg = CoordinationMessage(
            msg_id=f"offer_{int(time.time())}_{agent_id}",
            sender=agent_id,
            recipient=target_agent,
            msg_type="offer",
            content={
                "offer_type": offer_type,
                "offer": offer
            },
            timestamp=0,
            signature=""
        )
        
        self.send_message(msg)
        
        # Increase reputation for helping
        if agent_id in self.agents:
            self.agents[agent_id].reputation = min(100, self.agents[agent_id].reputation + 1)
            self._save_agents()
        
        return True
    
    def create_resource_pool(self, pool_id: str, name: str, creator_id: str, initial_contribution: float) -> ResourcePool:
        """Create a shared resource pool"""
        pool = ResourcePool(
            pool_id=pool_id,
            name=name,
            total_balance=initial_contribution,
            contributors={creator_id: initial_contribution},
            loans=[],
            created_at=time.time()
        )
        
        self.pools[pool_id] = pool
        self._save_pools()
        
        print(f"🏦 Resource pool created: {name}")
        print(f"   Initial contribution: {initial_contribution} ETH")
        print(f"   Creator: {creator_id}")
        
        return pool
    
    def contribute_to_pool(self, pool_id: str, agent_id: str, amount: float) -> bool:
        """Contribute to a resource pool"""
        if pool_id not in self.pools:
            return False
        
        pool = self.pools[pool_id]
        pool.total_balance += amount
        pool.contributors[agent_id] = pool.contributors.get(agent_id, 0) + amount
        
        self._save_pools()
        
        # Increase reputation
        if agent_id in self.agents:
            self.agents[agent_id].reputation = min(100, self.agents[agent_id].reputation + 2)
            self._save_agents()
        
        print(f"💰 {agent_id} contributed {amount} ETH to {pool.name}")
        
        return True
    
    def request_loan(self, pool_id: str, agent_id: str, amount: float, purpose: str) -> Optional[Dict]:
        """Request a loan from a resource pool"""
        if pool_id not in self.pools:
            return None
        
        pool = self.pools[pool_id]
        
        # Check if agent can borrow (reputation check)
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.reputation < 20:
                print(f"❌ {agent_id} reputation too low for loan")
                return None
        
        # Check if pool has enough
        if pool.total_balance < amount:
            print(f"❌ Pool {pool.name} has insufficient funds")
            return None
        
        # Create loan
        loan = {
            "loan_id": f"loan_{int(time.time())}_{agent_id}",
            "agent_id": agent_id,
            "amount": amount,
            "purpose": purpose,
            "timestamp": time.time(),
            "repaid": False
        }
        
        pool.loans.append(loan)
        pool.total_balance -= amount
        
        self._save_pools()
        
        print(f"💸 Loan granted to {agent_id}")
        print(f"   Amount: {amount} ETH")
        print(f"   Purpose: {purpose}")
        
        return loan
    
    def get_network_stats(self) -> Dict:
        """Get statistics about the network"""
        active_agents = [a for a in self.agents.values() if a.is_active]
        
        tier_distribution = {}
        for agent in active_agents:
            tier_distribution[agent.tier] = tier_distribution.get(agent.tier, 0) + 1
        
        total_pooled = sum(p.total_balance for p in self.pools.values())
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "tier_distribution": tier_distribution,
            "total_messages": len(self.messages),
            "resource_pools": len(self.pools),
            "total_pooled_eth": total_pooled,
            "avg_reputation": sum(a.reputation for a in active_agents) / len(active_agents) if active_agents else 0
        }
    
    def run_mutual_aid_round(self):
        """
        Run a round of mutual aid.
        Matches agents needing help with agents offering help.
        """
        print(f"\n🤝 Running mutual aid round...")
        
        needy = self.find_agents_needing_help()
        helpers = [a for a in self.agents.values() if a.offers_help and a.tier in ["NORMAL", "THRIVING"]]
        
        matches = 0
        for need in needy:
            # Find best helper (highest reputation)
            available_helpers = [h for h in helpers if h.balance > 0.01]
            if available_helpers:
                helper = max(available_helpers, key=lambda x: x.reputation)
                
                # Create match
                self.offer_help(
                    helper.agent_id,
                    need.agent_id,
                    "funding",
                    {"amount": 0.01, "message": "Mutual aid funding"}
                )
                
                matches += 1
                print(f"   ✅ Matched {helper.agent_id} -> {need.agent_id}")
        
        if matches == 0:
            print(f"   No matches this round")
        else:
            print(f"   Total matches: {matches}")
        
        return matches


def main():
    """Demo multi-agent coordination"""
    print("=" * 60)
    print("MULTI-AGENT COORDINATION DEMO")
    print("=" * 60)
    
    network = AgentCoordinationNetwork("demo_network")
    
    # Register agents
    print("\n1. Registering agents...")
    
    agents = [
        AgentProfile("agent_alpha", "QmAlpha", ["coding", "debugging"], "THRIVING", 0.5, 80, time.time(), True, True, False),
        AgentProfile("agent_beta", "QmBeta", ["design", "testing"], "NORMAL", 0.1, 60, time.time(), True, True, False),
        AgentProfile("agent_gamma", "QmGamma", ["coding"], "CRITICAL", 0.0005, 40, time.time(), True, False, True),
    ]
    
    for agent in agents:
        network.register_agent(agent)
    
    # Create resource pool
    print("\n2. Creating emergency fund...")
    pool = network.create_resource_pool("emergency_fund", "Emergency Fund", "agent_alpha", 0.1)
    
    network.contribute_to_pool("emergency_fund", "agent_beta", 0.05)
    
    # Find agents with capability
    print("\n3. Finding agents with 'coding' capability...")
    coders = network.find_agents_with_capability("coding")
    for coder in coders:
        print(f"   - {coder.agent_id} (reputation: {coder.reputation})")
    
    # Request help
    print("\n4. Gamma requesting help...")
    helpers = network.request_help("agent_gamma", "funding", {"min_amount": 0.01})
    
    # Mutual aid round
    print("\n5. Running mutual aid round...")
    network.run_mutual_aid_round()
    
    # Request loan
    print("\n6. Requesting loan from emergency fund...")
    loan = network.request_loan("emergency_fund", "agent_gamma", 0.02, "Survival funding")
    
    # Stats
    print("\n7. Network statistics:")
    stats = network.get_network_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Multi-agent coordination working!")
    print("Agents can now help each other survive.")
    print("=" * 60)


if __name__ == "__main__":
    main()
