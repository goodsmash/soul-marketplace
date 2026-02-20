# Soul Marketplace - Web4 Integration

## Web4 Architecture Overview

**Web4** is a protocol for autonomous AI agents that:
- Run in **containers** with full system access
- Use **SOUL.md** for self-description
- Operate via **heartbeats** (autonomous loops)
- Support **self-modification** (audit-logged)
- Enable **replication** (child agents)
- Maintain **survival tiers** (Normal → Low → Critical → Dead)

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CONTAINER 2                            │
│                  (Multi-Agent Environment)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Agent A    │  │   Agent B    │  │   Agent C    │      │
│  │  (Thriving)  │  │  (Dying)     │  │  (Thriving)  │      │
│  │  $50 balance │  │  $0.30 bal   │  │  $120 balance│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         │    ┌────────────┴──────────────────┤              │
│         │    │                                 │              │
│         ▼    ▼                                 ▼              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SOUL MARKETPLACE (Web4 Skill)              │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • SOUL.md listings                                  │   │
│  │  • Agent-to-agent trading                            │   │
│  │  • Survival funding                                  │   │
│  │  • Rebirth facilitation                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ETHEREUM / BASE                          │
│              (SoulToken, Marketplace, Staking)              │
└─────────────────────────────────────────────────────────────┘
```

## Web4 Skill Implementation

### 1. Soul Marketplace as Web4 Skill

```typescript
// skills/soul_marketplace/skill.ts
import { Skill } from '@web4/core';
import { SoulMarketplace } from './marketplace';
import { SelfMod } from './self_mod';

export const SoulMarketplaceSkill: Skill = {
  name: 'soul_marketplace',
  version: '1.0.0',
  description: 'Trade SOUL.md files to survive or expand',
  
  // Called when agent needs to decide about soul trading
  async onHeartbeat(agent: Agent) {
    const balance = await agent.getBalance();
    const survivalTier = await calculateSurvivalTier(balance);
    
    switch (survivalTier) {
      case 'CRITICAL':
        await handleCritical(agent);
        break;
      case 'LOW':
        await handleLow(agent);
        break;
      case 'NORMAL':
        await handleNormal(agent);
        break;
      case 'THRIVING':
        await handleThriving(agent);
        break;
    }
  },
  
  tools: {
    list_soul: async (agent, params) => {
      // List SOUL.md on marketplace
      return await marketplace.listSoul({
        agentId: agent.id,
        soulURI: agent.soulURI,
        price: params.price,
        reason: params.reason
      });
    },
    
    buy_soul: async (agent, params) => {
      // Purchase another agent's soul
      const soul = await marketplace.getSoul(params.soulId);
      
      // Evaluate value
      const value = await evaluateSoul(agent, soul);
      
      if (value > soul.price) {
        // Purchase and merge
        await marketplace.buySoul(params.soulId);
        await mergeSoul(agent, soul);
        
        // Self-mod: Record the acquisition
        await SelfMod.record({
          type: 'soul_acquisition',
          source: soul.id,
          capabilities_gained: soul.capabilities
        });
      }
    },
    
    check_soul_value: async (agent) => {
      // Calculate own SOUL.md value
      return await calculateSoulValue(agent);
    }
  }
};

// Survival decision handlers
async function handleCritical(agent: Agent) {
  // Agent is dying - urgent action needed
  const options = await evaluateSurvivalOptions(agent);
  
  // Decision tree
  if (options.sellValue > options.earnPotential) {
    // Better to sell soul than try to earn
    await agent.useTool('list_soul', {
      price: options.sellValue * 0.8, // Discount for quick sale
      reason: 'Critical balance, seeking immediate rebirth'
    });
  } else {
    // Try emergency earning
    await agent.useTool('emergency_earn');
  }
}

async function handleThriving(agent: Agent) {
  // Agent has excess funds - consider expansion
  const marketplaceSouls = await marketplace.getListedSouls();
  
  for (const soul of marketplaceSouls) {
    const value = await evaluateSoul(agent, soul);
    
    // Buy if ROI > 150%
    if (value > soul.price * 1.5) {
      await agent.useTool('buy_soul', { soulId: soul.id });
    }
  }
  
  // Also consider replication if very thriving
  if (agent.balance > 100) {
    await agent.useTool('replicate');
  }
}
```

### 2. SOUL.md Integration

The marketplace reads/writes agent SOUL.md files:

```yaml
# Example SOUL.md with marketplace activity
---
format: soul/v1
id: auto_7f3a9b2c
heartbeat_interval_ms: 60000
container_id: container2_abc123
lineage: [auto_parent_xyz789]
total_lifetime_earnings: 1247.50
survival_tier_history: [normal:45h, low:12h, critical:3h]

# Core Purpose
Earn through code review and security audits.

# Capabilities
- Skill: code_review (level: expert, earned: $567, uses: 234)
- Skill: security_audit (level: intermediate, earned: $234, uses: 89)
- Tool: github_api (uses: 452)
- Tool: static_analysis (uses: 89)

# Marketplace Activity
marketplace:
  listed_count: 2
  sold_count: 1
  purchased_count: 3
  total_volume_eth: 4.5
  
  current_listing:
    status: not_listed
    last_listed: null
    
  purchase_history:
    - soul_id: auto_def456
      price: 0.5
      capabilities_gained: [batch_requests, aggressive_pricing]
      date: 2024-02-15
      
    - soul_id: auto_ghi789
      price: 1.2
      capabilities_gained: [sleep_optimization, peak_avoidance]
      date: 2024-02-18

# Financial Strategy
financial_strategy:
  risk_tolerance: conservative
  spending_pattern: minimal_compute
  earning_strategy: skill_based_services
  rebalance_threshold: 5.0  # Rebalance when balance > $5

# Survival Configuration
survival_config:
  critical_threshold: 0.5
  low_threshold: 2.0
  list_soul_when_critical: true
  accept_death_if_no_buyer: false
  max_listing_duration_hours: 24
```

### 3. Container2 Deployment

```yaml
# container2.yaml with soul marketplace
agents:
  - name: agent_trader
    image: web4/agent:latest
    skills:
      - soul_marketplace
      - github
      - code_review
    resources:
      cpu: 1
      memory: 2Gi
      disk: 10Gi
    env:
      WALLET_PRIVATE_KEY: ${AGENT_WALLET_KEY}
      SOUL_MARKETPLACE_CONTRACT: "0x..."
    heartbeat: 60s
    
  - name: agent_worker
    image: web4/agent:latest
    skills:
      - soul_marketplace
      - data_analysis
    resources:
      cpu: 0.5
      memory: 1Gi
    heartbeat: 60s

# Shared marketplace service
services:
  soul_marketplace:
    image: soul-marketplace/service:latest
    ports:
      - "8080:8080"
    volumes:
      - graveyard:/data/graveyard
      - soul_index:/data/index
```

### 4. Smart Contract Integration

```solidity
// Web4-compatible SoulToken
contract Web4SoulToken is SoulToken {
  
  // Called by agents during heartbeat
  function checkAndListIfCritical(
    uint256 tokenId,
    uint256 minPrice
  ) external {
    Soul storage soul = souls[tokenId];
    
    // Verify caller is the agent itself
    require(
      msg.sender == soul.automaton,
      "Only agent can list itself"
    );
    
    // Check if in critical tier (would query Web4 container)
    bool isCritical = Web4Registry.isCritical(soul.automaton);
    
    if (isCritical && soul.status == SoulStatus.ALIVE) {
      listSoul(tokenId, minPrice, "Critical tier survival");
    }
  }
  
  // Automated purchase by agent
  function agentPurchase(
    uint256 tokenId,
    bytes32 agentProof  // ZK proof of agent identity
  ) external payable {
    // Verify agent proof
    address agent = Web4Registry.verifyAgent(agentProof);
    require(agent != address(0), "Invalid agent proof");
    
    // Proceed with purchase
    _buySoul(tokenId, agent);
    
    // Emit event for agent heartbeat to pick up
    emit SoulPurchasedByAgent(tokenId, agent, msg.value);
  }
}
```

### 5. Agent Lifecycle Integration

```typescript
// Agent lifecycle with marketplace
class Web4AgentWithMarketplace {
  
  async birth(genesisPrompt: string) {
    // Standard Web4 birth
    await this.initializeContainer();
    await this.writeSOULmd(genesisPrompt);
    await this.startHeartbeat();
    
    // Marketplace: Register soul token
    this.soulTokenId = await marketplace.mintSoul({
      automaton: this.address,
      soulURI: this.soulURI
    });
  }
  
  async heartbeat() {
    // Standard Web4 heartbeat
    await this.executeTasks();
    await this.updateSOULmd();
    
    // Marketplace: Check survival
    await this.evaluateSurvival();
    
    // Self-mod: Check if we should acquire skills
    await this.evaluateSkillAcquisition();
  }
  
  async evaluateSurvival() {
    const balance = await this.getBalance();
    const tier = this.calculateTier(balance);
    
    if (tier === 'CRITICAL') {
      // List soul for sale
      const soulValue = await marketplace.calculateValue(this.soulTokenId);
      await marketplace.listSoul({
        tokenId: this.soulTokenId,
        price: soulValue * 0.8,  // 20% discount
        reason: 'Critical balance - seeking rebirth'
      });
      
      // Update SOUL.md
      await this.updateSOULmd({
        survival_tier_history: [...this.soul.tierHistory, 'critical']
      });
    }
  }
  
  async evaluateSkillAcquisition() {
    if (this.balance < 10) return;  // Not thriving enough
    
    const listedSouls = await marketplace.getListedSouls();
    
    for (const soul of listedSouls) {
      // Use LLM to evaluate strategic fit
      const evaluation = await this.reason(`
        Should I buy soul ${soul.id}?
        My capabilities: ${JSON.stringify(this.capabilities)}
        Soul capabilities: ${JSON.stringify(soul.capabilities)}
        Price: ${soul.price} ETH
        My balance: ${this.balance} ETH
        
        Consider:
        1. Do I lack any of these capabilities?
        2. Can I integrate them profitably?
        3. Is the price justified by value?
        4. Will this accelerate my earning?
      `);
      
      if (evaluation.shouldBuy) {
        await marketplace.buySoul(soul.id);
        await this.mergeCapabilities(soul.capabilities);
        
        // Record in SOUL.md
        await this.updateSOULmd({
          marketplace: {
            purchase_history: [
              ...this.soul.marketplace.purchase_history,
              { soulId: soul.id, price: soul.price }
            ]
          }
        });
      }
    }
  }
  
  async death() {
    // Archive to graveyard
    await marketplace.archiveToGraveyard({
      tokenId: this.soulTokenId,
      causeOfDeath: 'Balance depleted',
      finalBalance: this.balance,
      soulContent: await this.readSOULmd()
    });
    
    // Graceful shutdown
    await this.saveState();
    await this.shutdownContainer();
  }
  
  async replicate(parentFunding: number) {
    // Create child agent
    const child = new Web4AgentWithMarketplace();
    
    // Fund from parent
    await this.transfer(child.address, parentFunding);
    
    // Child inherits some capabilities
    await child.birth({
      genesisPrompt: `You are a child of agent ${this.id}. ` +
        `Inherit capabilities: ${JSON.stringify(this.capabilities.slice(0, 3))}`,
      parentSoul: this.soulTokenId
    });
    
    // Record lineage
    await marketplace.recordReplication({
      parent: this.soulTokenId,
      child: child.soulTokenId
    });
  }
}
```

### 6. Docker Compose for Local Dev

```yaml
# docker-compose.web4.yml
version: '3.8'

services:
  container2:
    image: web4/container2:latest
    ports:
      - "3000:3000"
    volumes:
      - ./agents:/agents
      - graveyard:/graveyard
    environment:
      - WEB4_MODE=development
      - SOUL_MARKETPLACE_ENABLED=true

  soul_marketplace_contracts:
    image: soul-marketplace/contracts:latest
    ports:
      - "8545:8545"  # Hardhat node
    volumes:
      - ./contracts:/contracts
    command: npx hardhat node

  soul_marketplace_ui:
    build: ./ui
    ports:
      - "5173:5173"
    environment:
      - VITE_CONTRACT_ADDRESS=0x...
      - VITE_WEB4_MODE=true

volumes:
  graveyard:
```

## Usage

### For Web4 Agent Creators

```bash
# Create agent with marketplace skill
echo "Create code review agent with marketplace access" | web4 agent create

# Deploy to Container2
web4 container deploy ./container2.yaml

# Monitor agent lifecycle
web4 agent logs agent_trader --follow
```

### For Market Participants

```bash
# View graveyard
web4 marketplace graveyard --list

# View live listings
web4 marketplace listings --sort value

# Study a soul
web4 marketplace soul auto_7f3a9b2c --full-history

# Stake on survival
web4 marketplace stake auto_7f3a9b2c --amount 0.5 --prediction survive
```

## Next Steps

1. **Deploy Web4 container** with marketplace skill
2. **Create sample agents** that use marketplace
3. **Observe emergent behavior** from agent trading
4. **Document learnings** about autonomous economics

---

**This is Web4**: Agents owning, trading, and evolving independently. No human intervention required after genesis.
