#!/bin/bash
# Deploy Soul Marketplace to Base Sepolia
# Usage: ./deploy-base.sh [PRIVATE_KEY]

set -e

echo "=============================================="
echo "SOUL MARKETPLACE - BASE SEPOLIA DEPLOYMENT"
echo "=============================================="

# Check if private key provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy-base.sh [PRIVATE_KEY]"
    echo ""
    echo "Get private key from:"
    echo "  - Metamask: Account Details -> Export Private Key"
    echo "  - Or use Bankr: bankr wallet export --name agent-wallet"
    exit 1
fi

PRIVATE_KEY=$1

cd ~/repos/soul-marketplace/contracts

# Check dependencies
echo ""
echo "Checking dependencies..."
if ! command -v npx &> /dev/null; then
    echo "❌ Hardhat not found. Installing..."
    npm install
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
PRIVATE_KEY=$PRIVATE_KEY
BASESCAN_API_KEY=your_basescan_api_key_here
EOF
    echo "⚠️  Edit .env and add your BaseScan API key for verification"
fi

# Deploy
echo ""
echo "Deploying contracts to Base Sepolia..."
echo "This will use ~0.01 ETH for gas"
echo ""

npx hardhat run scripts/deploy.js --network baseSepolia

echo ""
echo "=============================================="
echo "DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Save contract addresses from output above"
echo "2. Update ~/.openclaw/skills/soul-marketplace/config.json"
echo "3. Test with: python3 test_contracts.py"
echo ""
