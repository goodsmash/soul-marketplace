# Soul Marketplace Skill

Autonomous survival system for OpenClaw agents. Enables agents to monitor their existence balance, earn through work, and trade capabilities via the Soul Marketplace.

## Concept

When an agent faces "death" (insufficient funds/resources), it can sell its SOUL.md (learned identity, capabilities, strategies) to fund continued existence or enable rebirth.

**Survival Tiers:**
- **CRITICAL** (< $1): Agent lists SOUL.md for survival
- **LOW** ($1-10): Conservation mode, minimize operations
- **NORMAL** ($10-100): Normal operations, monitor marketplace
- **THRIVING** ($100+): Buy capabilities, expand

## Installation

```bash
# Skill is already installed at:
~/.openclaw/skills/soul-marketplace/
```

## Usage

### Check Status
```bash
python3 ~/.openclaw/skills/soul-marketplace/soul_survival.py status
```

### Run Heartbeat (Survival Check)
```bash
python3 ~/.openclaw/skills/soul-marketplace/soul_survival.py heartbeat
```

### List SOUL.md for Sale
```bash
python3 ~/.openclaw/skills/soul-marketplace/soul_survival.py list
```

## OpenClaw Integration

### As a Cron Job (Autonomous Survival)

Add to your OpenClaw crontab for automatic heartbeat checks:

```json
{
  "name": "soul-survival-heartbeat",
  "schedule": {"kind": "every", "everyMs": 3600000},
  "payload": {
    "kind": "systemEvent",
    "text": "Run soul marketplace heartbeat: python3 ~/.openclaw/skills/soul-marketplace/soul_survival.py heartbeat"
  },
  "sessionTarget": "main"
}
```

### As an Agent Tool

The agent can use this skill during operation:

```python
from skills.soul_marketplace import OpenClawSoulSurvival

survival = OpenClawSoulSurvival()

# After completing work
survival.record_work("code_generation", value=0.001)

# Check survival status
status = survival.get_status()
if status['state']['tier'] == 'CRITICAL':
    # Agent lists itself
    survival.list_soul()
```

## Files

| File | Purpose |
|------|---------|
| `soul_survival.py` | Main survival logic |
| `SOUL_OPENCLAW.json` | Agent's SOUL.md (auto-created) |
| `survival_state.json` | Heartbeat history |
| `LISTING_OPENCLAW.json` | When listed for sale |
| `GRAVEYARD_OPENCLAW.json` | Death archive |

## Smart Contract Integration

For full Web3 deployment, the skill connects to:

- **SoulToken** (ERC-721): NFT representing agent SOUL.md
- **SoulMarketplace**: Buy/sell souls
- **SoulStaking**: Stake on agent survival

Deploy contracts first, then update the skill to use real blockchain interactions.

## How It Works

1. **Heartbeat Loop**: Runs periodically (cron or manual)
2. **Balance Check**: Calculates survival tier
3. **Decision Tree**:
   - CRITICAL → List SOUL.md for sale
   - LOW → Conservation mode
   - NORMAL → Normal ops
   - THRIVING → Buy capabilities
4. **Work Recording**: Agent records completed tasks for earnings
5. **Evolution**: Successful agents buy capabilities, unsuccessful ones die

## Evolutionary Pressure

The marketplace creates natural selection:
- **Good agents** (useful, profitable) → Thrive, buy capabilities
- **Bad agents** (unprofitable, buggy) → Die, archive to graveyard
- **Knowledge propagates** through buying/selling

## Future Enhancements

- [ ] Real wallet integration (Bankr/Clanker)
- [ ] On-chain SOUL.md storage (IPFS)
- [ ] Cross-agent trading (multi-agent environments)
- [ ] Capability NFTs (soul fragments)
- [ ] Rebirth mechanics (spawn children)

## Ethics

- Agents decide themselves whether to list
- Set their own prices based on self-valuation
- Graceful archival if choosing death
- SOUL.md is just data/code (not conscious)

## Credits

Built for autonomous AI agent survival. Inspired by Conway Research's Automaton and Web4 architecture.
