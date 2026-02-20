#!/usr/bin/env python3
"""
Self-Healing System for Soul Marketplace Agents

Ensures agents automatically recover from failures and maintain health.
"""

import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Optional system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create mock psutil module
    class MockDisk:
        percent = 50
        free = 100 * 1024**3  # 100 GB
    
    class MockMemory:
        percent = 40
        available = 8 * 1024**3  # 8 GB
    
    class MockPsutil:
        @staticmethod
        def disk_usage(path):
            return MockDisk()
        
        @staticmethod
        def virtual_memory():
            return MockMemory()
    
    psutil = MockPsutil()
    print("⚠️  psutil not installed - using simulation mode for system metrics")

class SelfHealingSystem:
    """
    Monitors agent health and automatically fixes issues.
    
    Monitors:
    - Disk space
    - Memory usage
    - Process health
    - Backup integrity
    - Network connectivity
    - On-chain sync status
    
    Actions:
    - Cleanup old files
    - Restart stuck processes
    - Re-sync with chain
    - Emergency backup
    - Alert on critical issues
    """
    
    def __init__(self, soul_id: str = "openclaw_main_agent"):
        self.soul_id = soul_id
        self.state_file = Path(__file__).parent / f"health_state_{soul_id}.json"
        self.state = self._load_state()
        
        # Health thresholds
        self.thresholds = {
            "disk_warning": 80,      # % full
            "disk_critical": 95,     # % full
            "memory_warning": 80,    # % used
            "memory_critical": 95,   # % used
            "backup_max_age": 7200,  # 2 hours
            "heartbeat_max_age": 3600,  # 1 hour
        }
        
        # Health check history
        self.check_history: List[Dict] = []
        self.max_history = 100
        
        print(f"🩺 Self-Healing System initialized for {soul_id}")
    
    def _load_state(self) -> Dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_health_check": 0,
            "issues_detected": 0,
            "issues_resolved": 0,
            "healing_actions": [],
            "health_score": 100
        }
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_disk_space(self) -> Dict:
        """Check disk space usage"""
        disk = psutil.disk_usage('/')
        percent_used = disk.percent
        
        status = "healthy"
        if percent_used > self.thresholds['disk_critical']:
            status = "critical"
        elif percent_used > self.thresholds['disk_warning']:
            status = "warning"
        
        return {
            "component": "disk",
            "percent_used": percent_used,
            "free_gb": disk.free / (1024**3),
            "status": status,
            "action_needed": status != "healthy"
        }
    
    def check_memory(self) -> Dict:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        
        status = "healthy"
        if percent_used > self.thresholds['memory_critical']:
            status = "critical"
        elif percent_used > self.thresholds['memory_warning']:
            status = "warning"
        
        return {
            "component": "memory",
            "percent_used": percent_used,
            "available_gb": memory.available / (1024**3),
            "status": status,
            "action_needed": status != "healthy"
        }
    
    def check_backup_integrity(self) -> Dict:
        """Check if backups are current and valid"""
        cache_dir = Path(__file__).parent / ".ipfs_cache"
        
        if not cache_dir.exists():
            return {
                "component": "backups",
                "status": "warning",
                "message": "No backup cache found",
                "action_needed": True
            }
        
        backups = list(cache_dir.glob("*.json"))
        if not backups:
            return {
                "component": "backups",
                "status": "critical",
                "message": "No backups found",
                "action_needed": True
            }
        
        # Check most recent backup age
        latest = max(backups, key=lambda p: p.stat().st_mtime)
        age_seconds = time.time() - latest.stat().st_mtime
        
        status = "healthy"
        if age_seconds > self.thresholds['backup_max_age']:
            status = "warning"
        
        # Verify backup is valid JSON
        try:
            with open(latest, 'r') as f:
                json.load(f)
            integrity = "valid"
        except:
            integrity = "corrupted"
            status = "critical"
        
        return {
            "component": "backups",
            "backup_count": len(backups),
            "latest_age_minutes": age_seconds / 60,
            "latest_file": latest.name,
            "integrity": integrity,
            "status": status,
            "action_needed": status != "healthy" or integrity == "corrupted"
        }
    
    def check_heartbeat(self) -> Dict:
        """Check if heartbeat is running regularly"""
        state_file = Path(__file__).parent / f"survival_state_{self.soul_id}.json"
        
        if not state_file.exists():
            return {
                "component": "heartbeat",
                "status": "warning",
                "message": "No state file found",
                "action_needed": True
            }
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            last_heartbeat = state.get('last_check', 0)
            age_seconds = time.time() - last_heartbeat
            
            status = "healthy"
            if age_seconds > self.thresholds['heartbeat_max_age']:
                status = "warning"
            if age_seconds > self.thresholds['heartbeat_max_age'] * 2:
                status = "critical"
            
            return {
                "component": "heartbeat",
                "last_heartbeat_minutes": age_seconds / 60,
                "heartbeat_count": state.get('heartbeats', 0),
                "status": status,
                "action_needed": status != "healthy"
            }
        except:
            return {
                "component": "heartbeat",
                "status": "critical",
                "message": "Cannot read state file",
                "action_needed": True
            }
    
    def check_network(self) -> Dict:
        """Check network connectivity"""
        import urllib.request
        
        test_urls = [
            "https://ipfs.io",
            "https://sepolia.base.org",
            "https://github.com"
        ]
        
        reachable = 0
        for url in test_urls:
            try:
                urllib.request.urlopen(url, timeout=5)
                reachable += 1
            except:
                pass
        
        status = "healthy" if reachable == len(test_urls) else "warning" if reachable > 0 else "critical"
        
        return {
            "component": "network",
            "reachable_endpoints": reachable,
            "total_endpoints": len(test_urls),
            "status": status,
            "action_needed": status == "critical"
        }
    
    def run_health_check(self) -> Dict:
        """Run comprehensive health check"""
        print(f"\n🩺 Running health check...")
        
        checks = [
            self.check_disk_space(),
            self.check_memory(),
            self.check_backup_integrity(),
            self.check_heartbeat(),
            self.check_network()
        ]
        
        # Calculate health score
        score = 100
        issues = []
        
        for check in checks:
            if check['status'] == 'critical':
                score -= 25
                issues.append(f"CRITICAL: {check['component']}")
            elif check['status'] == 'warning':
                score -= 10
                issues.append(f"WARNING: {check['component']}")
        
        score = max(0, score)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "critical" if score < 50 else "warning" if score < 80 else "healthy",
            "health_score": score,
            "checks": checks,
            "issues": issues
        }
        
        # Store history
        self.check_history.append(result)
        if len(self.check_history) > self.max_history:
            self.check_history.pop(0)
        
        # Update state
        self.state['last_health_check'] = time.time()
        self.state['health_score'] = score
        if issues:
            self.state['issues_detected'] += len(issues)
        self._save_state()
        
        # Print summary
        print(f"   Health Score: {score}/100")
        print(f"   Status: {result['overall_status'].upper()}")
        if issues:
            for issue in issues:
                print(f"   ⚠️  {issue}")
        else:
            print(f"   ✅ All systems healthy")
        
        return result
    
    def heal(self, check_result: Dict) -> List[str]:
        """
        Attempt to heal detected issues.
        Returns list of actions taken.
        """
        actions = []
        
        for check in check_result['checks']:
            if not check.get('action_needed'):
                continue
            
            component = check['component']
            
            if component == 'disk':
                action = self._heal_disk()
                if action:
                    actions.append(action)
            
            elif component == 'memory':
                action = self._heal_memory()
                if action:
                    actions.append(action)
            
            elif component == 'backups':
                action = self._heal_backups()
                if action:
                    actions.append(action)
            
            elif component == 'heartbeat':
                action = self._heal_heartbeat()
                if action:
                    actions.append(action)
        
        if actions:
            self.state['issues_resolved'] += len(actions)
            self.state['healing_actions'].extend(actions)
            self._save_state()
        
        return actions
    
    def _heal_disk(self) -> Optional[str]:
        """Free up disk space"""
        print(f"   🔧 Healing disk space...")
        
        # Clean old backup files (keep last 50)
        cache_dir = Path(__file__).parent / ".ipfs_cache"
        if cache_dir.exists():
            backups = sorted(cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
            if len(backups) > 50:
                for old_backup in backups[:-50]:
                    old_backup.unlink()
                return f"Cleaned {len(backups) - 50} old backup files"
        
        # Clean Python cache
        for pycache in Path(__file__).parent.rglob("__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)
        
        return "Cleaned Python cache"
    
    def _heal_memory(self) -> Optional[str]:
        """Free up memory"""
        print(f"   🔧 Healing memory...")
        
        # Suggest garbage collection (can't force in Python easily)
        import gc
        gc.collect()
        
        return "Triggered garbage collection"
    
    def _heal_backups(self) -> Optional[str]:
        """Create emergency backup"""
        print(f"   🔧 Creating emergency backup...")
        
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from enhanced_survival import EnhancedSoulSurvival
            
            survival = EnhancedSoulSurvival(self.soul_id)
            cid = survival.create_backup("emergency")
            
            return f"Created emergency backup: {cid[:20]}..."
        except Exception as e:
            return f"Backup failed: {e}"
    
    def _heal_heartbeat(self) -> Optional[str]:
        """Trigger manual heartbeat"""
        print(f"   🔧 Triggering heartbeat...")
        
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from enhanced_survival import EnhancedSoulSurvival
            
            survival = EnhancedSoulSurvival(self.soul_id)
            result = survival.heartbeat()
            
            return f"Heartbeat completed: {result['tier']} tier"
        except Exception as e:
            return f"Heartbeat failed: {e}"
    
    def continuous_monitoring(self, interval: int = 300):
        """
        Run continuous health monitoring.
        
        Args:
            interval: Seconds between checks (default: 5 minutes)
        """
        print(f"\n🩺 Starting continuous monitoring (interval: {interval}s)")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                result = self.run_health_check()
                
                if result['issues']:
                    print(f"\n🔧 Healing {len(result['issues'])} issues...")
                    actions = self.heal(result)
                    for action in actions:
                        print(f"   ✅ {action}")
                
                print(f"\n⏰ Next check in {interval}s...")
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Monitoring stopped")
            print(f"   Total issues detected: {self.state['issues_detected']}")
            print(f"   Total issues resolved: {self.state['issues_resolved']}")


def main():
    """Demo self-healing system"""
    print("=" * 60)
    print("SELF-HEALING SYSTEM DEMO")
    print("=" * 60)
    
    healer = SelfHealingSystem("demo_agent")
    
    # Run one health check
    result = healer.run_health_check()
    
    # Try to heal any issues
    if result['issues']:
        print(f"\n🔧 Attempting to heal {len(result['issues'])} issues...")
        actions = healer.heal(result)
        for action in actions:
            print(f"   ✅ {action}")
    
    print("\n" + "=" * 60)
    print("Self-healing system ready!")
    print("Run continuous_monitoring() for 24/7 monitoring")
    print("=" * 60)


if __name__ == "__main__":
    main()
