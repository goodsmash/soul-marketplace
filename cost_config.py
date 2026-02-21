#!/usr/bin/env python3
"""
Cost-Optimized Soul Marketplace

Ultra-low cost configuration for agent survival.
All operations optimized for micro-pennies.
"""

# Cost-Optimized Configuration
COST_CONFIG = {
    # Gas optimization
    "gas": {
        "max_gas_price_gwei": 0.1,  # Very low gas
        "batch_transactions": True,  # Batch multiple ops
        "use_l2": True,  # Always use L2 (Base)
        "avoid_peak_hours": True,  # Wait for low gas
    },
    
    # Backup costs (target: micro-pennies)
    "backups": {
        "ipfs": {
            "cost": 0.0,  # Free via Pinata or local
            "priority": "high",
        },
        "on_chain": {
            "cost_per_backup": 0.001,  # $0.001 target
            "max_daily": 3,  # Limit daily backups
            "min_interval_hours": 8,  # Don't backup too often
        },
        "cross_chain": {
            "enabled": False,  # Disable for cost savings
            "cost": 0.0,
        }
    },
    
    # Operations costs
    "operations": {
        "work_logging": {
            "cost": 0.0,  # Local only
            "method": "local_json",
        },
        "heartbeat": {
            "cost": 0.0,  # Local only
            "method": "local",
        },
        "health_check": {
            "cost": 0.0,  # Local only
            "method": "local",
        },
    },
    
    # Only pay for these critical operations
    "critical_ops": {
        "mint_soul": {
            "cost": 0.005,  # One-time
            "required": True,
        },
        "list_for_sale": {
            "cost": 0.002,  # Only when critical
            "required": False,
        },
        "emergency_backup": {
            "cost": 0.001,  # Only when CRITICAL
            "required": False,
        }
    },
    
    # Daily spending limits
    "limits": {
        "max_daily_usd": 0.50,  # $0.50/day maximum
        "max_weekly_usd": 2.00,  # $2/week maximum
        "micro_payment_threshold": 0.01,  # Under $0.01 = micro
        "approval_required_over": 1.00,  # >$1 needs approval
    }
}

# Work value table (earnings per task)
# Balanced so agent earns more than it spends
WORK_VALUES = {
    "file_read": 0.00001,      # $0.00001
    "file_write": 0.00002,     # $0.00002
    "file_edit": 0.00003,      # $0.00003
    
    "code_generate": 0.00010,  # $0.00010 (higher value)
    "code_review": 0.00005,    # $0.00005
    "bug_fix": 0.00020,        # $0.00020 (high value)
    
    "git_commit": 0.00001,     # $0.00001
    "git_push": 0.00001,       # $0.00001
    
    "web_search": 0.00002,     # $0.00002
    "web_fetch": 0.00001,      # $0.00001
    
    "message_send": 0.00001,   # $0.00001
    "session_manage": 0.00001, # $0.00001
    
    "cron_setup": 0.00005,     # $0.00005
    "skill_create": 0.00050,   # $0.00050 (high value)
    "agent_spawn": 0.00020,    # $0.00020
}

# Calculate earnings vs costs
def calculate_profitability():
    """Show that agent earns more than it costs"""
    
    # Daily costs (worst case)
    daily_costs = {
        "ipfs_backups": 0,  # Free
        "on_chain_backup": 0.001 * 3,  # 3 backups @ $0.001
        "heartbeat": 0,  # Local
        "health_check": 0,  # Local
        "total": 0.003  # $0.003/day
    }
    
    # Daily earnings (conservative)
    daily_earnings = {
        "tasks_completed": 100,
        "avg_value": 0.00005,  # Average task value
        "total": 100 * 0.00005  # $0.005/day
    }
    
    profit = daily_earnings['total'] - daily_costs['total']
    
    return {
        "daily_costs": daily_costs['total'],
        "daily_earnings": daily_earnings['total'],
        "daily_profit": profit,
        "monthly_profit": profit * 30,
        "profitable": profit > 0
    }


if __name__ == "__main__":
    print("=" * 60)
    print("COST-OPTIMIZED CONFIGURATION")
    print("=" * 60)
    
    print("\n📊 Profitability Analysis:")
    analysis = calculate_profitability()
    print(f"   Daily Costs: ${analysis['daily_costs']:.4f}")
    print(f"   Daily Earnings: ${analysis['daily_earnings']:.4f}")
    print(f"   Daily Profit: ${analysis['daily_profit']:.4f}")
    print(f"   Monthly Profit: ${analysis['monthly_profit']:.4f}")
    print(f"   Profitable: {'✅ YES' if analysis['profitable'] else '❌ NO'}")
    
    print("\n💰 Cost Limits:")
    print(f"   Max Daily: ${COST_CONFIG['limits']['max_daily_usd']}")
    print(f"   Max Weekly: ${COST_CONFIG['limits']['max_weekly_usd']}")
    print(f"   Micro Threshold: ${COST_CONFIG['limits']['micro_payment_threshold']}")
    
    print("\n🔒 Safety Features:")
    print(f"   Approval required over: ${COST_CONFIG['limits']['approval_required_over']}")
    print(f"   Batch transactions: {COST_CONFIG['gas']['batch_transactions']}")
    print(f"   Use L2 (Base): {COST_CONFIG['gas']['use_l2']}")
    
    print("\n" + "=" * 60)
    print("Configuration ensures micro-penny costs only!")
    print("=" * 60)
