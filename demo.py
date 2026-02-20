#!/usr/bin/env python3
"""
Demo: Full survival cycle for OpenClaw agent
Shows earning, tier progression, and marketplace interaction
"""

import sys
sys.path.insert(0, '/home/goodsmash/.openclaw/skills/soul-marketplace')

from soul_survival import OpenClawSoulSurvival
import json

def demo():
    survival = OpenClawSoulSurvival()
    
    print("=" * 60)
    print("OPENCLAW AGENT SURVIVAL DEMO")
    print("=" * 60)
    
    # Reset for demo
    survival.soul['current_balance'] = 0.0
    survival.soul['total_lifetime_earnings'] = 0.0
    survival.soul['status'] = 'ALIVE'
    survival._save_soul(survival.soul)
    
    print(f"\nInitial State:")
    print(f"  Balance: {survival.get_balance()} ETH")
    print(f"  Tier: {survival.get_tier()}")
    
    # Simulate work and heartbeats
    work_scenarios = [
        ("file_management", 0.002, "Organized project files"),
        ("code_generation", 0.005, "Created soul marketplace skill"),
        ("github_operations", 0.003, "Pushed commits to GitHub"),
        ("code_generation", 0.008, "Built typing assistant GUI"),
        ("file_management", 0.002, "Updated documentation"),
    ]
    
    print("\n" + "=" * 60)
    print("SIMULATING WORK + HEARTBEATS")
    print("=" * 60)
    
    for capability, value, description in work_scenarios:
        # Record work
        survival.record_work(capability, value)
        
        # Run heartbeat
        result = survival.heartbeat()
        
        print(f"\n[Heartbeat #{result['heartbeat']}]")
        print(f"  Work: {description} (+{value} ETH)")
        print(f"  Balance: {result['balance']:.4f} ETH")
        print(f"  Tier: {result['tier']}")
        print(f"  Action: {result['action']}")
    
    # Final status
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)
    
    status = survival.get_status()
    print(f"\nTotal Earnings: {status['soul']['total_lifetime_earnings']:.4f} ETH")
    print(f"Current Balance: {status['soul']['current_balance']:.4f} ETH")
    print(f"Survival Tier: {status['state']['tier']}")
    print(f"Status: {status['soul']['status']}")
    print(f"Total Heartbeats: {status['state']['heartbeats']}")
    
    print("\nCapabilities:")
    for cap in status['soul']['capabilities']:
        print(f"  - {cap['name']}: {cap['level']} (earned {cap['earnings']:.4f}, {cap['uses']} uses)")
    
    print("\n" + "=" * 60)
    print("SOUL VALUE CALCULATION")
    print("=" * 60)
    soul_value = survival.calculate_soul_value()
    print(f"\nCurrent SOUL.md value: {soul_value:.4f} ETH")
    print(f"Listing price (80%): {soul_value * 0.8:.4f} ETH")
    
    # Show what would happen if thriving
    print("\n" + "=" * 60)
    print("THRIVING SIMULATION")
    print("=" * 60)
    
    survival.soul['current_balance'] = 0.15  # Make it thriving
    survival._save_soul(survival.soul)
    
    result = survival.heartbeat()
    print(f"\nWith 0.15 ETH balance (THRIVING):")
    print(f"  Tier: {result['tier']}")
    print(f"  Action: {result['action']}")
    print(f"  Available souls to buy: {result.get('available_souls', 0)}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    demo()
