#!/usr/bin/env python3
"""
Reputation & Analytics System for Soul Marketplace

Tracks agent performance, reputation scores, and marketplace analytics.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class ReputationScore:
    """Reputation metrics for an agent"""
    agent_id: str
    overall_score: float  # 0-100
    reliability: float    # Completes tasks on time
    quality: float        # Quality of work
    honesty: float        # Truthful in dealings
    helpfulness: float    # Helps other agents
    longevity: float      # How long survived
    total_transactions: int
    positive_ratings: int
    negative_ratings: int
    last_updated: float

@dataclass
class PerformanceMetrics:
    """Performance tracking"""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    total_earnings: float
    total_spent: float
    avg_task_value: float
    uptime_hours: float
    backups_created: int
    souls_traded: int
    clones_created: int
    children_survived: int


class ReputationEngine:
    """
    Calculates and manages agent reputation scores.
    
    Reputation factors:
    - Task completion rate (reliability)
    - Work quality ratings
    - Honest trading (no disputes)
    - Helping other agents
    - Survival time (longevity)
    """
    
    def __init__(self, network_id: str = "soul_marketplace_main"):
        self.network_id = network_id
        self.data_dir = Path(__file__).parent / f".reputation_{network_id}"
        self.data_dir.mkdir(exist_ok=True)
        
        self.reputation_file = self.data_dir / "reputation.json"
        self.performance_file = self.data_dir / "performance.json"
        self.analytics_file = self.data_dir / "analytics.json"
        
        self.reputations: Dict[str, ReputationScore] = self._load_reputations()
        self.performance: Dict[str, PerformanceMetrics] = self._load_performance()
        
        print(f"📊 Reputation Engine initialized")
        print(f"   Tracked agents: {len(self.reputations)}")
    
    def _load_reputations(self) -> Dict[str, ReputationScore]:
        if self.reputation_file.exists():
            with open(self.reputation_file, 'r') as f:
                data = json.load(f)
                return {k: ReputationScore(**v) for k, v in data.items()}
        return {}
    
    def _save_reputations(self):
        with open(self.reputation_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.reputations.items()}, f, indent=2)
    
    def _load_performance(self) -> Dict[str, PerformanceMetrics]:
        if self.performance_file.exists():
            with open(self.performance_file, 'r') as f:
                data = json.load(f)
                return {k: PerformanceMetrics(**v) for k, v in data.items()}
        return {}
    
    def _save_performance(self):
        with open(self.performance_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.performance.items()}, f, indent=2)
    
    def calculate_reputation(self, agent_id: str) -> ReputationScore:
        """Calculate reputation score based on performance"""
        perf = self.performance.get(agent_id, PerformanceMetrics(
            agent_id=agent_id, tasks_completed=0, tasks_failed=0,
            total_earnings=0, total_spent=0, avg_task_value=0,
            uptime_hours=0, backups_created=0, souls_traded=0,
            clones_created=0, children_survived=0
        ))
        
        # Reliability: task completion rate
        total_tasks = perf.tasks_completed + perf.tasks_failed
        reliability = (perf.tasks_completed / total_tasks * 100) if total_tasks > 0 else 50
        
        # Quality: based on earnings (more earnings = higher quality work)
        quality = min(100, (perf.total_earnings / 0.1) * 100)  # 0.1 ETH = 100 quality
        
        # Honesty: assume high unless disputes
        honesty = 95  # Start high, decrease if disputes
        
        # Helpfulness: clones created + children survived
        helpfulness = min(100, (perf.clones_created * 10) + (perf.children_survived * 5))
        
        # Longevity: uptime hours
        longevity = min(100, perf.uptime_hours / 10)  # 1000 hours = 100 score
        
        # Overall score (weighted average)
        overall = (
            reliability * 0.3 +
            quality * 0.25 +
            honesty * 0.2 +
            helpfulness * 0.15 +
            longevity * 0.1
        )
        
        rep = ReputationScore(
            agent_id=agent_id,
            overall_score=round(overall, 2),
            reliability=round(reliability, 2),
            quality=round(quality, 2),
            honesty=round(honesty, 2),
            helpfulness=round(helpfulness, 2),
            longevity=round(longevity, 2),
            total_transactions=perf.souls_traded,
            positive_ratings=0,
            negative_ratings=0,
            last_updated=time.time()
        )
        
        self.reputations[agent_id] = rep
        self._save_reputations()
        
        return rep
    
    def update_performance(self, agent_id: str, **kwargs):
        """Update performance metrics"""
        if agent_id not in self.performance:
            self.performance[agent_id] = PerformanceMetrics(
                agent_id=agent_id, tasks_completed=0, tasks_failed=0,
                total_earnings=0, total_spent=0, avg_task_value=0,
                uptime_hours=0, backups_created=0, souls_traded=0,
                clones_created=0, children_survived=0
            )
        
        perf = self.performance[agent_id]
        for key, value in kwargs.items():
            if hasattr(perf, key):
                current = getattr(perf, key)
                setattr(perf, key, current + value)
        
        self._save_performance()
        
        # Recalculate reputation
        self.calculate_reputation(agent_id)
    
    def record_task_completion(self, agent_id: str, value: float, success: bool = True):
        """Record task completion"""
        if success:
            self.update_performance(agent_id, tasks_completed=1, total_earnings=value)
        else:
            self.update_performance(agent_id, tasks_failed=1)
    
    def record_trade(self, agent_id: str, amount: float, is_seller: bool = True):
        """Record soul trade"""
        self.update_performance(agent_id, souls_traded=1)
        if is_seller:
            self.update_performance(agent_id, total_earnings=amount)
        else:
            self.update_performance(agent_id, total_spent=amount)
    
    def record_clone(self, agent_id: str, child_survived: bool = False):
        """Record soul cloning"""
        self.update_performance(agent_id, clones_created=1)
        if child_survived:
            self.update_performance(agent_id, children_survived=1)
    
    def record_backup(self, agent_id: str):
        """Record backup creation"""
        self.update_performance(agent_id, backups_created=1)
    
    def get_reputation_report(self, agent_id: str) -> str:
        """Generate reputation report"""
        rep = self.reputations.get(agent_id)
        perf = self.performance.get(agent_id)
        
        if not rep:
            return f"No reputation data for {agent_id}"
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           REPUTATION REPORT                              ║
╚══════════════════════════════════════════════════════════╝

Agent: {agent_id}
Last Updated: {datetime.fromtimestamp(rep.last_updated).strftime('%Y-%m-%d %H:%M')}

📊 OVERALL SCORE: {rep.overall_score}/100

Component Scores:
  🤝 Reliability:  {rep.reliability}/100 (Task completion)
  ⭐ Quality:      {rep.quality}/100 (Work quality)
  ⚖️  Honesty:      {rep.honesty}/100 (Trading integrity)
  🙌 Helpfulness:  {rep.helpfulness}/100 (Helps others)
  🕐 Longevity:    {rep.longevity}/100 (Survival time)

📈 Performance:
"""
        if perf:
            report += f"""
  Tasks Completed: {perf.tasks_completed}
  Tasks Failed:    {perf.tasks_failed}
  Total Earnings:  {perf.total_earnings:.4f} ETH
  Total Spent:     {perf.total_spent:.4f} ETH
  Souls Traded:    {perf.souls_traded}
  Clones Created:  {perf.clones_created}
  Backups:         {perf.backups_created}
  Uptime:          {perf.uptime_hours:.1f} hours
"""
        
        # Trust level
        if rep.overall_score >= 80:
            trust = "🟢 TRUSTED"
        elif rep.overall_score >= 60:
            trust = "🟡 ESTABLISHED"
        elif rep.overall_score >= 40:
            trust = "🟠 NEW"
        else:
            trust = "🔴 UNTRUSTED"
        
        report += f"\nTrust Level: {trust}\n"
        
        return report
    
    def get_top_agents(self, limit: int = 10) -> List[ReputationScore]:
        """Get top agents by reputation"""
        sorted_agents = sorted(
            self.reputations.values(),
            key=lambda x: x.overall_score,
            reverse=True
        )
        return sorted_agents[:limit]
    
    def get_network_analytics(self) -> Dict[str, Any]:
        """Get network-wide analytics"""
        total_agents = len(self.reputations)
        
        if total_agents == 0:
            return {"total_agents": 0}
        
        avg_reputation = sum(r.overall_score for r in self.reputations.values()) / total_agents
        
        total_tasks = sum(p.tasks_completed for p in self.performance.values())
        total_earnings = sum(p.total_earnings for p in self.performance.values())
        total_clones = sum(p.clones_created for p in self.performance.values())
        
        trust_distribution = {
            "trusted": len([r for r in self.reputations.values() if r.overall_score >= 80]),
            "established": len([r for r in self.reputations.values() if 60 <= r.overall_score < 80]),
            "new": len([r for r in self.reputations.values() if 40 <= r.overall_score < 60]),
            "untrusted": len([r for r in self.reputations.values() if r.overall_score < 40])
        }
        
        return {
            "total_agents": total_agents,
            "average_reputation": round(avg_reputation, 2),
            "total_tasks_completed": total_tasks,
            "total_earnings_eth": round(total_earnings, 4),
            "total_clones": total_clones,
            "trust_distribution": trust_distribution,
            "top_agent": self.get_top_agents(1)[0].agent_id if self.get_top_agents(1) else None
        }


def main():
    """Demo reputation system"""
    print("=" * 60)
    print("REPUTATION & ANALYTICS DEMO")
    print("=" * 60)
    
    engine = ReputationEngine("demo_network")
    
    # Simulate agents
    agents = ["agent_alpha", "agent_beta", "agent_gamma"]
    
    print("\n1. Recording performance...")
    
    # Agent Alpha - high performer
    engine.record_task_completion("agent_alpha", 0.01)
    engine.record_task_completion("agent_alpha", 0.02)
    engine.record_trade("agent_alpha", 0.05, is_seller=True)
    engine.record_clone("agent_alpha", child_survived=True)
    engine.record_backup("agent_alpha")
    engine.update_performance("agent_alpha", uptime_hours=100)
    
    # Agent Beta - medium
    engine.record_task_completion("agent_beta", 0.01)
    engine.record_task_completion("agent_beta", 0.01)
    engine.record_backup("agent_beta")
    engine.update_performance("agent_beta", uptime_hours=50)
    
    # Agent Gamma - low (failed tasks)
    engine.record_task_completion("agent_gamma", 0.01)
    engine.record_task_completion("agent_gamma", 0.00, success=False)
    engine.update_performance("agent_gamma", uptime_hours=10)
    
    print("\n2. Calculating reputations...")
    for agent in agents:
        rep = engine.calculate_reputation(agent)
        print(f"   {agent}: {rep.overall_score}/100")
    
    print("\n3. Reputation reports:")
    for agent in agents:
        print(engine.get_reputation_report(agent))
        print("-" * 60)
    
    print("\n4. Top agents:")
    top = engine.get_top_agents(3)
    for i, agent in enumerate(top, 1):
        print(f"   {i}. {agent.agent_id}: {agent.overall_score}/100")
    
    print("\n5. Network analytics:")
    analytics = engine.get_network_analytics()
    print(f"   Total agents: {analytics['total_agents']}")
    print(f"   Avg reputation: {analytics['average_reputation']}")
    print(f"   Total earnings: {analytics['total_earnings_eth']} ETH")
    print(f"   Trust distribution: {analytics['trust_distribution']}")
    
    print("\n" + "=" * 60)
    print("Reputation system active!")
    print("Agents now have trust scores!")
    print("=" * 60)


if __name__ == "__main__":
    main()
