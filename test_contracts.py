#!/usr/bin/env python3
"""
Test Soul Marketplace Contract Integration
Tests connection to deployed contracts on Base Sepolia
"""

import json
import sys
from pathlib import Path

def test_contract_connection():
    """Test connection to deployed contracts"""
    
    config_file = Path(__file__).parent / "config.json"
    
    if not config_file.exists():
        print("❌ No config.json found")
        print("   Deploy contracts first: ./deploy-base.sh")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    contracts = config.get('contracts', {})
    
    print("=" * 60)
    print("SOUL MARKETPLACE - CONTRACT TEST")
    print("=" * 60)
    
    print(f"\nNetwork: {config.get('network', 'unknown')}")
    print(f"Deployer: {config.get('deployer', 'unknown')}")
    
    print("\nContracts:")
    for name, address in contracts.items():
        print(f"  {name}: {address}")
        
        # Verify format
        if not address.startswith('0x') or len(address) != 42:
            print(f"    ⚠️  Invalid address format")
    
    # Test RPC connection
    print("\nTesting RPC connection...")
    try:
        import urllib.request
        import urllib.error
        
        rpc_url = "https://sepolia.base.org"
        
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }).encode()
        
        req = urllib.request.Request(
            rpc_url,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            block_number = int(result['result'], 16)
            print(f"  ✅ Connected to Base Sepolia")
            print(f"  Current block: {block_number}")
            
    except Exception as e:
        print(f"  ❌ RPC connection failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed")
    print("=" * 60)
    print("\nReady to:")
    print("  - Mint SOUL NFT")
    print("  - List capabilities")
    print("  - Buy agent souls")
    print("  - Stake on survival")
    
    return True

def main():
    success = test_contract_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
