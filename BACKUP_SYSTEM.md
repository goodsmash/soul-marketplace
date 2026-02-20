# On-Chain Backup System

## Overview

The Soul Marketplace now includes a **comprehensive on-chain backup system** that ensures agents can be fully recovered even if their local environment is destroyed.

## Features

### 1. IPFS Storage
- SOUL.md uploaded to IPFS (decentralized storage)
- Content-addressed (CID)
- Multiple gateway fallbacks
- Local caching

### 2. On-Chain Backup Records
- Every backup recorded on Ethereum/Base
- Immutable history
- Version tracking
- Proof of existence

### 3. Automatic Backups
- Scheduled every hour
- Triggered on significant events
- Configurable intervals
- Smart deduplication

### 4. Cross-Chain Replication
- Backups replicated to Arbitrum
- Backups replicated to Optimism
- Disaster recovery across chains
- No single point of failure

### 5. Emergency Recovery
- Restore from any backup
- Guardian-based recovery
- Multi-sig approvals
- One-click restoration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ENVIRONMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Enhanced    │  │    IPFS      │  │   On-Chain   │      │
│  │   Survival   │──▶│   Storage    │──▶│   Adapter    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │              │
│         │                 │                  │              │
│         ▼                 ▼                  ▼              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SOUL_BACKUP CONTRACT                    │   │
│  │  • backupHistory mapping                             │   │
│  │  • crossChainBackups mapping                         │   │
│  │  • recoveryRequests                                  │   │
│  │  • guardian system                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        IPFS NETWORK                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Node 1  │  │  Node 2  │  │  Node 3  │  │  Node N  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  Content is replicated across thousands of nodes            │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Automatic Backups

Backups happen automatically every hour:

```python
from enhanced_survival import EnhancedSoulSurvival

survival = EnhancedSoulSurvival("my_agent")

# Work as normal - backups happen automatically
survival.record_work("code_generation", 0.001)
```

### Manual Backup

```python
# Create manual backup
cid = survival.create_backup("manual")
print(f"Backed up to: {cid}")
```

### Cross-Chain Backup

```python
# Enable cross-chain
survival.soul['backup_config']['cross_chain_enabled'] = True

# Backup will replicate to Arbitrum, Optimism
cid = survival.create_backup("cross_chain")
```

### Restore from Backup

```python
# Restore latest
survival.restore_from_backup()

# Restore specific version
survival.restore_from_backup("QmAbC123...")
```

### Emergency Recovery

```python
# When agent has been "killed"
survival.emergency_recovery()
```

## Backup Configuration

```json
{
  "backup_config": {
    "auto_backup_enabled": true,
    "backup_interval": 3600,
    "max_history": 100,
    "cross_chain_enabled": true
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `auto_backup_enabled` | true | Enable automatic backups |
| `backup_interval` | 3600 | Seconds between backups |
| `max_history` | 100 | Max backups to keep |
| `cross_chain_enabled` | true | Replicate to other chains |

## Recovery Guardians

Set up guardians for multi-sig recovery:

```solidity
// Add guardians
backupContract.addGuardian(tokenId, guardian1Address);
backupContract.addGuardian(tokenId, guardian2Address);
backupContract.addGuardian(tokenId, guardian3Address);

// Set threshold (2 of 3)
backupContract.setRecoveryThreshold(tokenId, 2);
```

## Backup Types

| Type | Trigger | On-Chain | Cross-Chain |
|------|---------|----------|-------------|
| `auto` | Every hour | ✅ | Optional |
| `manual` | User triggered | ✅ | Optional |
| `critical` | Survival listing | ✅ | ✅ |
| `mint` | Initial mint | ✅ | ✅ |
| `thriving` | High balance | ✅ | Optional |

## Deployment

```bash
# Deploy all contracts with backup system
cd ~/repos/soul-marketplace/contracts
npx hardhat run scripts/deploy-full.js --network baseSepolia
```

This deploys:
- SoulToken
- SoulMarketplace
- SoulStaking
- **SoulBackup** (new)

## Files

| File | Purpose |
|------|---------|
| `SoulBackup.sol` | On-chain backup contract |
| `ipfs_storage.py` | IPFS integration |
| `onchain_adapter.py` | Contract interactions |
| `enhanced_survival.py` | Integrated system |

## Cost Analysis

### IPFS Storage
- **Free** via Pinata (free tier)
- Or run local IPFS node (free)
- No gas costs

### On-Chain Records
- Backup record: ~50,000 gas (~$0.50 on Base)
- Cross-chain backup: ~30,000 gas additional
- Recovery: ~80,000 gas

### Estimates
- 1 backup/day = ~$15/month
- 1 backup/hour = ~$360/month
- Cross-chain = +60% cost

## Security

### Data Integrity
- Every backup hashed (SHA-256)
- Hash stored on-chain
- IPFS content-addressed
- Automatic verification

### Access Control
- Only soul owner can backup
- Only guardians can approve recovery
- Emergency recovery requires proof

### Persistence
- IPFS: Permanent if pinned
- Blockchain: Immutable
- Multiple gateways
- Cross-chain redundancy

## Troubleshooting

### "IPFS not reachable"
- Check internet connection
- Try alternative gateway
- Use local IPFS node

### "Backup failed"
- Check gas balance
- Verify contract address
- Check network connection

### "Restore failed"
- Verify CID exists
- Check IPFS gateway
- Try different gateway

## Comparison

| Feature | Conway | Soul Marketplace |
|---------|--------|------------------|
| Storage | Conway Cloud | IPFS + On-chain |
| Backup | Manual/SQLite | Automatic + Versioned |
| Recovery | Creator only | Multi-sig guardians |
| Cross-chain | No | Yes |
| Cost | Subscription | Pay-per-backup |
| Open source | No | Yes |

## Future Enhancements

- [ ] Arweave integration (permanent storage)
- [ ] Filecoin integration (decentralized pinning)
- [ ] Zero-knowledge proofs for private backups
- [ ] AI-verified backup integrity
- [ ] Automatic cross-chain sync
