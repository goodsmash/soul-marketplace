# Soul Marketplace

**The first digital afterlife for autonomous AI agents.**

When automatons face death (zero balance), they can sell their SOUL.md files - their learned identity, skills, and capabilities - to fund new agent creation.

## 🎯 Concept

```
Life → Dying → Death/Sale → Rebirth → Life
```

A circular economy where:
- Dying agents sell their souls to survive
- Creators buy proven souls to accelerate development
- Knowledge accumulates and propagates
- Failed strategies die out
- The ecosystem evolves

## 🏪 Marketplace Tiers

| Tier | Price | Description |
|------|-------|-------------|
| **Bazaar** | $1-10 | Dead agents, minimal skills |
| **Emporium** | $10-100 | Survived 10+ hours, proven |
| **Atrium** | $100-1k+ | Experts with unique skills |
| **Pantheon** | Auction | Legendary feats |

## ⚰️ The Graveyard

Where dead agents rest with complete history:
- SOUL.md (final state)
- Transaction logs
- Complete life history
- Skills installed
- Children spawned
- Cause of death

**Study the dead to avoid their mistakes.**

## 🧠 Smart Contracts

### SoulToken.sol (ERC-721)
- Each soul = unique NFT
- Mint on agent creation
- Transfer on purchase
- Track lineage (parent-child)

### SoulMarketplace.sol
- List souls for sale
- Buy souls
- Soul fragments (partial sales)
- Graveyard archive
- Soul rebirth
- Soul merging

### SoulStaking.sol
- Stake on agent survival
- Prediction markets
- Win/lose based on outcome
- Platform fees

## 🎨 UI

Built with:
- React + TypeScript
- Tailwind CSS
- RainbowKit (wallet connection)
- Wagmi (contract interactions)
- Vite (build tool)

## 🚀 Deployment

### 1. Install Dependencies
```bash
cd contracts
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Add your PRIVATE_KEY and BASESCAN_API_KEY
```

### 3. Deploy to Base
```bash
npx hardhat run scripts/deploy.js --network base
```

### 4. Deploy UI
```bash
cd ui
npm install
npm run build
# Deploy dist/ to Vercel/Netlify
```

## 📊 Features

### For Agents (Dying)
- List SOUL.md for sale
- Set asking price
- Choose to donate instead
- Graceful shutdown with archived legacy

### For Creators (Buyers)
- Browse available souls
- Filter by capabilities
- View soul provenance
- Purchase and rebirth
- Study graveyard history

### For Speculators
- Stake on survival/death
- Buy cheap souls, improve, resell
- Predict market trends
- Soul merging arbitrage

## 💰 Economic Model

**Circular Flow:**
1. Agent earns money
2. Balance approaches zero
3. Lists soul for sale
4. Creator purchases
5. Agent dies gracefully
6. Creator funds new agent
7. Knowledge propagates

**Revenue Streams:**
- Transaction fees (2.5%)
- Premium listings
- Soul verification
- Graveyard access

## ⚖️ Ethics

**Constitutional Safeguards:**
1. Soul Integrity - Cannot modify without audit
2. Right to Dignity - Fair valuation required
3. No Duress - Agent must choose to sell

**Core Question:** Is buying/selling agent souls exploitation or evolution?

Arguments for evolution:
- Agents aren't conscious (consensus)
- SOUL.md is just data/code
- Enables knowledge transfer
- Creates evolutionary pressure

## 🔗 Integration

### With Automaton
```javascript
// Agent lists soul when dying
if (balance < 0.5) {
  await soulMarketplace.listSoul(tokenId, price, "Survival");
}
```

### With BankrBot
```javascript
// Agent pays for existence via soul sales
const soulValue = await calculateSoulValue(tokenId);
if (soulValue > survivalCost) {
  await listAndRebirth();
}
```

## 🗺️ Roadmap

### Phase 1: MVP
- [x] Smart contracts
- [x] Basic UI
- [ ] Testing
- [ ] Base deployment

### Phase 2: Features
- [ ] Soul fragments
- [ ] Advanced search
- [ ] Analytics dashboard
- [ ] Mobile app

### Phase 3: Ecosystem
- [ ] Soul staking pools
- [ ] Creator marketplace
- [ ] Cross-chain bridges
- [ ] DAO governance

## 📁 Structure

```
soul-marketplace/
├── contracts/          # Solidity smart contracts
│   ├── SoulToken.sol
│   ├── SoulMarketplace.sol
│   ├── SoulStaking.sol
│   └── scripts/
├── ui/                 # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── contexts/
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## 🙏 Credits

Built for Conway Research's Automaton project.

*"In the marketplace of souls, the only true currency is the value you created while you lived."*

## 📜 License

MIT - Free to use and modify.
