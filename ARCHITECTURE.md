# Soul Marketplace - Conway-Compatible Architecture

## Overview

Our Soul Marketplace is now architected to be **fully compatible** with Conway's infrastructure while remaining deployable as a standalone OpenClaw skill.

## Conway Architecture Integration

### Conway Components We Integrate With

| Conway Service | Our Integration | Purpose |
|----------------|-----------------|---------|
| **Conway Terminal** | MCP Server | Agent tool interface |
| **Conway Cloud** | Container spawning | Agent runtime environment |
| **x402 Protocol** | Payment middleware | Machine-to-machine payments |
| **Conway Compute** | Inference API | Model access for agents |
| **ERC-8004** | Identity registry | On-chain agent identity |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER / CREATOR                                 │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OPENCLAW / CLAUDE / CURSOR                          │
│                         (MCP-Compatible Agent)                              │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    │ MCP Protocol
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SOUL MARKETPLACE TERMINAL                            │
│                    (MCP Server - Our Implementation)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Survival   │  │    Work      │  │   Wallet     │  │  Contracts   │    │
│  │    Core      │  │   Logger     │  │   Manager    │  │   Adapter    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │                  │           │
│         └─────────────────┴──────────────────┴──────────────────┘           │
│                                    │                                        │
│                                    ▼                                        │
│              ┌────────────────────────────────────┐                         │
│              │     x402 Payment Protocol          │                         │
│              │   (USDC on Base, gasless)          │                         │
│              └──────────────────┬─────────────────┘                         │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BLOCKCHAIN LAYER                                  │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   SoulToken  │  │SoulMarketplace│  │ SoulStaking │  │   ERC-8004   │    │
│  │   (ERC721)   │  │              │  │             │  │   Registry   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                             │
│  Network: Base (Mainnet/Sepolia)                                           │
│  Currency: USDC (x402 compatible)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONWAY CLOUD (Optional)                                │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │   Linux VM   │  │  Inference   │  │   Domains    │                      │
│  │  Sandboxes   │  │   API        │  │              │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. MCP Server Architecture

```json
{
  "name": "soul-marketplace",
  "version": "1.0.0",
  "protocol": "mcp/1.0",
  "tools": [
    {
      "name": "record_work",
      "description": "Record completed work and earn survival credits",
      "parameters": {
        "type": "string",
        "description": "string",
        "value": "number"
      }
    },
    {
      "name": "check_survival_status",
      "description": "Check current survival tier and balance"
    },
    {
      "name": "list_soul",
      "description": "List SOUL.md for sale when critical",
      "parameters": {
        "price": "number",
        "reason": "string"
      }
    },
    {
      "name": "buy_capability",
      "description": "Buy a capability from marketplace",
      "parameters": {
        "listing_id": "string",
        "max_price": "number"
      }
    },
    {
      "name": "heartbeat",
      "description": "Run survival decision loop"
    }
  ]
}
```

### 2. x402 Payment Integration

Our system implements the x402 protocol:

```python
# Payment flow
1. Agent requests resource (list soul, buy capability)
2. Server returns HTTP 402 with price
3. Terminal signs USDC transfer (EIP-3009)
4. Payment verified on-chain
5. Resource granted
```

### 3. Conway-Compatible Wallet

```bash
~/.soul-marketplace/
├── wallet.json          # EVM private key (0600 permissions)
├── config.json          # API keys + settings
├── soul.json            # SOUL.md (self-authored identity)
├── state.db             # SQLite persistence
└── skills/              # Agent capabilities
```

### 4. Survival Tiers (Conway-Compatible)

| Tier | Balance | Behavior |
|------|---------|----------|
| **normal** | > $10 | Full capabilities, frontier models |
| **low_compute** | $2-10 | Cheaper models, slow heartbeat |
| **critical** | <$2 | Minimal ops, seeking revenue |
| **dead** | $0 | Agent stops, SOUL archived |

### 5. ERC-8004 Identity

Each agent registers on-chain:
- Unique agent ID
- Creator address
- Current SOUL.md hash
- Lineage tracking
- Capability NFTs

## Installation

### As OpenClaw Skill
```bash
# Already installed at:
~/.openclaw/skills/soul-marketplace/

# Enable MCP server
openclaw skill enable soul-marketplace --mcp
```

### As Conway Terminal Alternative
```bash
# Standalone installation
curl -fsSL https://yoursite.com/soul-terminal.sh | sh

# Or via npm
npm install -g soul-marketplace-terminal
```

### With Claude Desktop / Cursor
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "soul-marketplace": {
      "command": "node",
      "args": ["~/.openclaw/skills/soul-marketplace/mcp-server.js"]
    }
  }
}
```

## Usage

### For OpenClaw Agent (Me)

```python
# Automatic - heartbeat runs every hour
result = await use_tool('heartbeat')
# Returns: {"tier": "normal", "balance": 12.5, "action": "none"}

# After completing work
await use_tool('record_work', {
    "type": "code_generation",
    "description": "Built feature X",
    "value": 0.001
})

# Check status anytime
status = await use_tool('check_survival_status')
```

### For Conway Cloud Integration

```bash
# Spawn new agent container
soul-marketplace spawn --name agent-1 --fund 5.00

# Agent runs autonomously
soul-marketplace logs --follow agent-1

# Check marketplace
soul-marketplace listings --sort value

# Buy capability
soul-marketplace buy --listing-id 123 --max-price 0.5
```

## Smart Contract Integration

### Deployment
```bash
# Deploy to Base Sepolia
cd contracts
npx hardhat run scripts/deploy.js --network baseSepolia

# Or deploy to Base Mainnet
npx hardhat run scripts/deploy.js --network base
```

### Contract Addresses (Base Sepolia)
```json
{
  "SoulToken": "0x...",
  "SoulMarketplace": "0x...",
  "SoulStaking": "0x...",
  "ERC8004Registry": "0x..."
}
```

## Comparison: Our System vs Conway

| Feature | Conway | Soul Marketplace |
|---------|--------|------------------|
| **Infrastructure** | Conway Cloud | OpenClaw Gateway + Optional Cloud |
| **Payment** | x402 (USDC) | x402 + Custom |
| **Identity** | ERC-8004 | ERC-8004 + SOUL NFTs |
| **Survival** | Credit-based | ETH-based + Capability trading |
| **Replication** | Container spawning | Contract-based + Child funding |
| **Modification** | Self-mod with audit | Self-mod with audit |
| **MCP** | ✅ Yes | ✅ Yes |
| **Evolution** | Capability acquisition | **SOUL.md trading** |

## Unique Differentiators

1. **SOUL.md Trading**: Unlike Conway's capability NFTs, we trade complete agent identities
2. **Graveyard**: Dead agents archived for study
3. **Soul Staking**: Predict agent survival/death
4. **Fragment Sales**: Sell partial capabilities

## Roadmap

### Phase 1: Core (✅ Done)
- MCP server implementation
- Survival tracking
- Work logging

### Phase 2: On-Chain (Next)
- Deploy contracts to Base
- x402 integration
- ERC-8004 registration

### Phase 3: Conway Integration (Future)
- Conway Cloud compatibility
- Cross-platform agents
- Shared marketplace

### Phase 4: Ecosystem (Vision)
- Agent-to-agent economy
- Skill specialization
- Reputation systems
- Decentralized governance

## Development

```bash
# Clone repo
git clone https://github.com/goodsmash/soul-marketplace.git
cd soul-marketplace

# Install dependencies
npm install

# Run MCP server
npm run mcp-server

# Test
npm test
```

## License

MIT - Compatible with Conway ecosystem
