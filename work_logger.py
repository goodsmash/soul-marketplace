#!/usr/bin/env python3
"""
Real Earning Integration for OpenClaw Agent
Records actual work done and converts to survival balance
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/goodsmash/.openclaw/skills/soul-marketplace')
from soul_survival import OpenClawSoulSurvival

# Value table for different work types
WORK_VALUES = {
    # File operations
    "file_read": 0.0001,
    "file_write": 0.0002,
    "file_edit": 0.0003,
    
    # Code operations
    "code_generate": 0.001,
    "code_review": 0.0005,
    "bug_fix": 0.002,
    
    # Git operations
    "git_commit": 0.0003,
    "git_push": 0.0002,
    "pr_create": 0.001,
    
    # Research
    "web_search": 0.0002,
    "web_fetch": 0.0001,
    
    # Communication
    "message_send": 0.0001,
    "session_manage": 0.0002,
    
    # System
    "cron_setup": 0.0005,
    "skill_create": 0.005,
    "agent_spawn": 0.002,
}

class WorkLogger:
    """Logs agent work and converts to survival balance"""
    
    LOG_FILE = Path(__file__).parent / "work_log.json"
    
    def __init__(self):
        self.survival = OpenClawSoulSurvival()
        self.log = self._load_log()
    
    def _load_log(self):
        if self.LOG_FILE.exists():
            with open(self.LOG_FILE, 'r') as f:
                return json.load(f)
        return {"entries": [], "total_value": 0.0}
    
    def _save_log(self):
        with open(self.LOG_FILE, 'w') as f:
            json.dump(self.log, f, indent=2)
    
    def log_work(self, work_type: str, description: str, capability: str = None):
        """Log work and earn survival balance"""
        
        value = WORK_VALUES.get(work_type, 0.0001)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": work_type,
            "description": description,
            "value": value,
            "capability": capability or self._infer_capability(work_type)
        }
        
        self.log['entries'].append(entry)
        self.log['total_value'] += value
        self._save_log()
        
        # Record in survival system
        self.survival.record_work(entry['capability'], value)
        
        return entry
    
    def _infer_capability(self, work_type: str) -> str:
        """Map work type to capability"""
        mapping = {
            "file_read": "file_management",
            "file_write": "file_management",
            "file_edit": "file_management",
            "code_generate": "code_generation",
            "code_review": "code_generation",
            "bug_fix": "code_generation",
            "git_commit": "github_operations",
            "git_push": "github_operations",
            "pr_create": "github_operations",
            "web_search": "research",
            "web_fetch": "research",
            "message_send": "communication",
            "session_manage": "communication",
            "cron_setup": "system_admin",
            "skill_create": "skill_development",
            "agent_spawn": "agent_management",
        }
        return mapping.get(work_type, "general")
    
    def get_daily_summary(self) -> dict:
        """Get today's work summary"""
        today = datetime.now().date().isoformat()
        
        today_entries = [
            e for e in self.log['entries']
            if e['timestamp'].startswith(today)
        ]
        
        total = sum(e['value'] for e in today_entries)
        by_type = {}
        for e in today_entries:
            by_type[e['type']] = by_type.get(e['type'], 0) + 1
        
        return {
            "date": today,
            "entries": len(today_entries),
            "total_earned": total,
            "by_type": by_type
        }
    
    def get_status(self) -> dict:
        """Get full work status"""
        return {
            "total_entries": len(self.log['entries']),
            "total_value": self.log['total_value'],
            "survival": self.survival.get_status()
        }

# Global instance for easy import
work_logger = WorkLogger()

def log(work_type: str, description: str):
    """Quick log function"""
    return work_logger.log_work(work_type, description)

def main():
    """CLI entry point"""
    import sys
    
    logger = WorkLogger()
    
    if len(sys.argv) < 2:
        print("Usage: python work_logger.py [log|summary|status]")
        print("\nWork types:")
        for wt, val in WORK_VALUES.items():
            print(f"  {wt}: {val} ETH")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "log" and len(sys.argv) >= 4:
        entry = logger.log_work(sys.argv[2], sys.argv[3])
        print(f"Logged: {entry['description']} (+{entry['value']} ETH)")
    
    elif cmd == "summary":
        summary = logger.get_daily_summary()
        print(json.dumps(summary, indent=2))
    
    elif cmd == "status":
        status = logger.get_status()
        print(json.dumps(status, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
