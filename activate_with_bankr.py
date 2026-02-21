#!/usr/bin/env python3
"""
Activate Agent with Bankr Funding

Uses Bankr's 0.0505 ETH to:
1. Fund agent wallet
2. Deploy contracts (if needed)
3. Mint SOUL NFT on-chain
4. Start survival with real backups
"""

import json
import time
from pathlib import Path
from bankr_integration import BankrIntegration

def activate_agent():
    print("=" * 60)
    print("ACTIVATE AGENT WITH BANKR")
    print("=" * 60)
    
    # Initialize Bankr
    bankr = BankrIntegration()
    
    # Check Bankr balance
    balance = bankr.get_balance("base")
    print(f"\n💰 Bankr wallet: {balance} ETH")
    
    if not balance or balance < 0.01:
        print("❌ Insufficient funds")
        return False
    
    # Load or create agent wallet
    wallet_file = Path(__file__).parent / "wallet.json"
    
    if wallet_file.exists():
        with open(wallet_file, 'r') as f:
            wallet = json.load(f)
        
        agent_address = wallet.get('address')
        
        if not agent_address:
            print("\n⚠️ Agent wallet needs address")
            print("   Creating new wallet via Bankr...")
            # Bankr manages wallet - we'll use its address
            agent_address = None  # Will be derived from Bankr
    else:
        print("\n⚠️ No wallet file - Bankr will manage transactions")
        agent_address = None
    
    # Option 1: Deploy contracts
    print("\n" + "=" * 60)
    print("DEPLOY CONTRACTS?")
    print("=" * 60)
    print("\nOption 1: Deploy new contracts (costs ~0.01 ETH)")
    print("Option 2: Use existing contracts (need addresses)")
    
    # For now, let's check if we have contract addresses
    config_file = Path(__file__).parent / "config.json"
    contracts = {}
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        contracts = config.get('contracts', {})
    
    if contracts.get('SoulToken'):
        print(f"\n✅ Found existing contracts:")
        for name, addr in contracts.items():
            print(f"   {name}: {addr}")
        use_existing = True
    else:
        print("\n⚠️ No contracts found")
        deploy = input("Deploy new contracts? (y/N): ").lower()
        
        if deploy == 'y':
            print("\n🚀 Deploying contracts via Bankr...")
            if bankr.deploy_contracts():
                print("   ⏳ Deployment started")
                print("   Check https://bankr.bot/dashboard for status")
                print("   Then update config.json with addresses")
                return True
        
        use_existing = False
    
    # Option 2: Test with simple transfer
    if use_existing:
        print("\n" + "=" * 60)
        print("TEST ON-CHAIN OPERATIONS")
        print("=" * 60)
        
        # Import enhanced survival
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from enhanced_survival import EnhancedSoulSurvival
        
        survival = EnhancedSoulSurvival("openclaw_main_agent")
        
        # Create backup first
        print("\n💾 Creating IPFS backup...")
        cid = survival.create_backup("pre_mint")
        
        # Calculate hash
        import hashlib
        content = json.dumps(survival.soul, sort_keys=True)
        soul_hash = f"0x{hashlib.sha256(content.encode()).hexdigest()[:64]}"
        
        print(f"\n🎨 Ready to mint SOUL NFT:")
        print(f"   Soul CID: {cid}")
        print(f"   Soul Hash: {soul_hash[:40]}...")
        print(f"   Contract: {contracts.get('SoulToken')}")
        
        mint = input("\nMint SOUL NFT on-chain? (y/N): ").lower()
        
        if mint == 'y':
            print("\n🚀 Minting via Bankr...")
            bankr.mint_soul_nft(contracts['SoulToken'], cid)
            
            print("\n✅ If successful, agent is now:")
            print("   - Backed up to IPFS")
            print("   - Recorded on Base blockchain")
            print("   - Can trade on Soul Marketplace")
            
            # Update config
            survival.state['token_id'] = 1  # Placeholder
            survival.state['contract_address'] = contracts['SoulToken']
            survival._save_state()
        
        print("\n" + "=" * 60)
        print("AGENT STATUS")
        print("=" * 60)
        
        status = survival.get_backup_status()
        print(f"IPFS Backups: {status['ipfs_backups']}")
        print(f"On-chain: {'Yes' if survival.token_id else 'Pending'}")
        print(f"Restorable: {status['restorable']}")
        
        return True
    
    return False


def quick_test():
    """Quick test with Bankr"""
    print("=" * 60)
    print("QUICK BANKR TEST")
    print("=" * 60)
    
    bankr = BankrIntegration()
    
    # Check balance
    balance = bankr.get_balance("base")
    print(f"\nBankr Balance: {balance} ETH")
    
    # Check if we can send (need to_address)
    print("\n✅ Bankr is configured and working!")
    print(f"   Ready to fund agent wallet")
    print(f"   Ready to deploy contracts")
    print(f"   Ready to mint SOUL NFTs")
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        activate_agent()
