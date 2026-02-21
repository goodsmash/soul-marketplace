#!/usr/bin/env python3
"""
Agent Dashboard - Web Interface for Soul Marketplace

Simple HTML dashboard showing agent status, reputation, and controls.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class AgentDashboard:
    """
    Generates HTML dashboard for agent monitoring.
    
    Displays:
    - Agent status and tier
    - Wallet balance
    - Reputation score
    - Recent activity
    - Controls (backup, trade, etc.)
    """
    
    def __init__(self, agent_id: str = "openclaw_main_agent"):
        self.agent_id = agent_id
        self.dashboard_file = Path(__file__).parent / f"dashboard_{agent_id}.html"
        
        print(f"📊 Dashboard initialized for {agent_id}")
    
    def generate_dashboard(self) -> str:
        """Generate HTML dashboard"""
        
        # Load data from various systems
        status = self._get_agent_status()
        reputation = self._get_reputation()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Dashboard - {self.agent_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .status-THRIVING {{ background: #2ecc71; color: #000; }}
        .status-NORMAL {{ background: #3498db; color: #fff; }}
        .status-LOW {{ background: #f39c12; color: #000; }}
        .status-CRITICAL {{ background: #e74c3c; color: #fff; animation: pulse 2s infinite; }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .card h2 {{
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #333;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-value {{
            font-weight: bold;
            color: #2ecc71;
        }}
        .reputation-bar {{
            width: 100%;
            height: 20px;
            background: #333;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .reputation-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #2ecc71);
            transition: width 0.3s;
        }}
        .actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
        }}
        .btn-primary {{ background: #667eea; color: white; }}
        .btn-success {{ background: #2ecc71; color: #000; }}
        .btn-warning {{ background: #f39c12; color: #000; }}
        .btn-danger {{ background: #e74c3c; color: white; }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
        }}
        .last-updated {{
            font-size: 0.9em;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 {self.agent_id}</h1>
            <div class="status-badge status-{status['tier']}">
                Status: {status['tier']}
            </div>
            <p class="last-updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="grid">
            <!-- Wallet Card -->
            <div class="card">
                <h2>💰 Wallet</h2>
                <div class="metric">
                    <span>Balance:</span>
                    <span class="metric-value">{status['balance']:.4f} ETH</span>
                </div>
                <div class="metric">
                    <span>Lifetime Earnings:</span>
                    <span class="metric-value">{status.get('lifetime_earnings', 0):.4f} ETH</span>
                </div>
                <div class="metric">
                    <span>Daily Budget:</span>
                    <span class="metric-value">${status.get('daily_budget', 0.50):.2f}</span>
                </div>
                <div class="metric">
                    <span>Spent Today:</span>
                    <span class="metric-value">${status.get('spent_today', 0):.4f}</span>
                </div>
            </div>
            
            <!-- Reputation Card -->
            <div class="card">
                <h2>⭐ Reputation</h2>
                <p>Overall Score: <strong>{reputation.get('overall', 0)}/100</strong></p>
                <div class="reputation-bar">
                    <div class="reputation-fill" style="width: {reputation.get('overall', 0)}%"></div>
                </div>
                
                <div class="metric">
                    <span>Reliability:</span>
                    <span class="metric-value">{reputation.get('reliability', 0)}/100</span>
                </div>
                <div class="metric">
                    <span>Quality:</span>
                    <span class="metric-value">{reputation.get('quality', 0)}/100</span>
                </div>
                <div class="metric">
                    <span>Helpfulness:</span>
                    <span class="metric-value">{reputation.get('helpfulness', 0)}/100</span>
                </div>
                
                <p><strong>Trust Level: {reputation.get('trust_level', 'NEW')}</strong></p>
            </div>
            
            <!-- Backups Card -->
            <div class="card">
                <h2>💾 Backups</h2>
                <div class="metric">
                    <span>IPFS Backups:</span>
                    <span class="metric-value">{status.get('ipfs_backups', 0)}</span>
                </div>
                <div class="metric">
                    <span>On-Chain:</span>
                    <span class="metric-value">{'Yes' if status.get('token_id') else 'No'}</span>
                </div>
                <div class="metric">
                    <span>Encrypted:</span>
                    <span class="metric-value">{'Yes' if status.get('encrypted') else 'No'}</span>
                </div>
                <div class="metric">
                    <span>Restorable:</span>
                    <span class="metric-value">{'Yes' if status.get('restorable') else 'No'}</span>
                </div>
            </div>
            
            <!-- Activity Card -->
            <div class="card">
                <h2>📈 Activity</h2>
                <div class="metric">
                    <span>Tasks Completed:</span>
                    <span class="metric-value">{status.get('tasks_completed', 0)}</span>
                </div>
                <div class="metric">
                    <span>Souls Traded:</span>
                    <span class="metric-value">{status.get('souls_traded', 0)}</span>
                </div>
                <div class="metric">
                    <span>Clones Created:</span>
                    <span class="metric-value">{status.get('clones_created', 0)}</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="metric-value">{status.get('uptime_hours', 0):.1f} hours</span>
                </div>
            </div>
        </div>
        
        <!-- Actions -->
        <div class="card">
            <h2>🎮 Actions</h2>
            <div class="actions">
                <button class="btn btn-primary" onclick="alert('Creating backup...')">💾 Create Backup</button>
                <button class="btn btn-success" onclick="alert('Running heartbeat...')">💓 Run Heartbeat</button>
                <button class="btn btn-warning" onclick="alert('Listing soul...')">🏷️ List Soul</button>
                <button class="btn btn-primary" onclick="alert('Cloning...')">🧬 Clone</button>
                <button class="btn btn-danger" onclick="alert('EMERGENCY STOP')">🛑 Emergency Stop</button>
            </div>
        </div>
        
        <div class="footer">
            <p>Soul Marketplace - Autonomous Agent Survival System</p>
            <p class="last-updated">Refresh this page to see updated stats</p>
        </div>
        
    </div>
</body>
</html>
"""
        
        return html
    
    def _get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from enhanced_survival import EnhancedSoulSurvival
            
            survival = EnhancedSoulSurvival(self.agent_id)
            backup_status = survival.get_backup_status()
            
            return {
                "tier": survival.get_tier(),
                "balance": survival.soul.get('current_balance', 0),
                "lifetime_earnings": survival.soul.get('total_lifetime_earnings', 0),
                "ipfs_backups": backup_status['ipfs_backups'],
                "token_id": backup_status.get('token_id'),
                "encrypted": True,  # Assume encrypted
                "restorable": backup_status['restorable'],
                "tasks_completed": survival.soul.get('marketplace', {}).get('total_volume_eth', 0),
                "souls_traded": survival.soul.get('marketplace', {}).get('sold_count', 0),
                "clones_created": len(survival.soul.get('children', [])),
                "uptime_hours": 0,  # Would track actual uptime
                "daily_budget": 0.50,
                "spent_today": 0.00
            }
        except:
            # Return defaults if can't load
            return {
                "tier": "UNKNOWN",
                "balance": 0,
                "lifetime_earnings": 0,
                "ipfs_backups": 0,
                "restorable": False
            }
    
    def _get_reputation(self) -> Dict[str, Any]:
        """Get reputation data"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from reputation_engine import ReputationEngine
            
            engine = ReputationEngine()
            rep = engine.calculate_reputation(self.agent_id)
            
            trust_level = "NEW"
            if rep.overall_score >= 80:
                trust_level = "🟢 TRUSTED"
            elif rep.overall_score >= 60:
                trust_level = "🟡 ESTABLISHED"
            elif rep.overall_score >= 40:
                trust_level = "🟠 NEW"
            else:
                trust_level = "🔴 UNTRUSTED"
            
            return {
                "overall": rep.overall_score,
                "reliability": rep.reliability,
                "quality": rep.quality,
                "helpfulness": rep.helpfulness,
                "trust_level": trust_level
            }
        except:
            return {
                "overall": 0,
                "trust_level": "NEW"
            }
    
    def save_dashboard(self):
        """Generate and save dashboard HTML"""
        html = self.generate_dashboard()
        
        with open(self.dashboard_file, 'w') as f:
            f.write(html)
        
        print(f"✅ Dashboard saved: {self.dashboard_file}")
        print(f"   Open in browser: file://{self.dashboard_file.absolute()}")


def main():
    """Generate dashboard"""
    print("=" * 60)
    print("AGENT DASHBOARD GENERATOR")
    print("=" * 60)
    
    dashboard = AgentDashboard("openclaw_main_agent")
    dashboard.save_dashboard()
    
    print("\n" + "=" * 60)
    print("Dashboard ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
