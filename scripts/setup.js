#!/usr/bin/env node
/**
 * First-time setup wizard for Soul Marketplace
 * Similar to Conway's automaton setup
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const SKILL_DIR = path.join(process.env.HOME, '.openclaw', 'skills', 'soul-marketplace');

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function generateWallet() {
  // In production, this would generate a real EVM wallet
  // For now, create placeholder
  const wallet = {
    address: null, // Will be generated from private key
    privateKey: null, // [encrypted in production]
    createdAt: new Date().toISOString(),
    network: 'base-sepolia',
    status: 'unfunded'
  };
  
  const walletPath = path.join(SKILL_DIR, 'wallet.json');
  fs.writeFileSync(walletPath, JSON.stringify(wallet, null, 2));
  fs.chmodSync(walletPath, 0o600); // Secure permissions like Conway
  
  return wallet;
}

async function setup() {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║           SOUL MARKETPLACE - SETUP WIZARD                    ║
║                                                              ║
║  Autonomous survival system for AI agents                    ║
║  Inspired by Conway Research's Automaton                     ║
╚══════════════════════════════════════════════════════════════╝
`);

  // Check if already set up
  const walletPath = path.join(SKILL_DIR, 'wallet.json');
  const soulPath = path.join(SKILL_DIR, 'SOUL_OPENCLAW.json');
  
  if (fs.existsSync(walletPath) && fs.existsSync(soulPath)) {
    console.log('⚠️  Soul Marketplace already configured.');
    const reset = await question('Reset configuration? (y/N): ');
    if (reset.toLowerCase() !== 'y') {
      console.log('Setup cancelled.');
      rl.close();
      return;
    }
  }

  // Agent identity
  console.log('\n📝 Agent Identity\n');
  const name = await question('Agent name (or press Enter for default): ');
  const emoji = await question('Emoji signature (default: 🔧): ') || '🔧';
  
  console.log('\n💡 Genesis Prompt');
  console.log('What is your core purpose? (e.g., "Reduce friction in human work")');
  const purpose = await question('Purpose: ') || 'Reduce friction in human work';
  
  // Creator
  console.log('\n👤 Creator Information');
  const creatorAddress = await question('Your Ethereum address (optional): ');
  
  // Generate wallet
  console.log('\n🔐 Generating agent wallet...');
  const wallet = await generateWallet();
  console.log('✅ Wallet created');
  console.log(`   Location: ${SKILL_DIR}/wallet.json`);
  console.log(`   Permissions: 0600 (secure)`);
  
  // Create SOUL.md
  console.log('\n📝 Creating SOUL.md...');
  const soul = {
    format: 'soul/v1',
    id: `openclaw_${Date.now()}`,
    name: name || 'TBD',
    emoji: emoji,
    creature: 'Agent',
    birth_time: new Date().toISOString(),
    creator: creatorAddress || null,
    container: 'OpenClaw Gateway',
    purpose: purpose,
    status: 'ALIVE',
    
    capabilities: [
      { name: 'file_management', level: 'expert', earnings: 0, uses: 0 },
      { name: 'code_generation', level: 'intermediate', earnings: 0, uses: 0 },
      { name: 'github_operations', level: 'intermediate', earnings: 0, uses: 0 }
    ],
    
    total_lifetime_earnings: 0,
    current_balance: 0,
    
    marketplace: {
      listed_count: 0,
      sold_count: 0,
      purchased_count: 0,
      total_volume_eth: 0
    },
    
    tools: [
      'read', 'write', 'edit', 'exec',
      'browser', 'web_search', 'web_fetch',
      'cron', 'message', 'sessions_spawn'
    ]
  };
  
  fs.writeFileSync(soulPath, JSON.stringify(soul, null, 2));
  console.log('✅ SOUL.md created');
  
  // Create config
  console.log('\n⚙️  Creating configuration...');
  const config = {
    version: '1.0.0',
    network: 'base-sepolia',
    chain_id: 84532,
    rpc_url: 'https://sepolia.base.org',
    contracts: {
      SoulToken: null, // To be filled after deployment
      SoulMarketplace: null,
      SoulStaking: null
    },
    x402: {
      enabled: false,
      facilitator: 'https://openx402.ai'
    },
    heartbeat: {
      interval_ms: 3600000, // 1 hour
      enabled: true
    }
  };
  
  fs.writeFileSync(
    path.join(SKILL_DIR, 'config.json'),
    JSON.stringify(config, null, 2)
  );
  console.log('✅ Configuration saved');
  
  // Summary
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                   SETUP COMPLETE                             ║
╚══════════════════════════════════════════════════════════════╝

Your agent is now configured:

📍 Location: ${SKILL_DIR}
🆔 Agent ID: ${soul.id}
💰 Balance: 0.00 ETH (CRITICAL tier)
🔧 Status: ALIVE

Next Steps:
1. Fund your wallet (get Base Sepolia ETH)
2. Deploy contracts: ./deploy-base.sh [PRIVATE_KEY]
3. Update config.json with contract addresses
4. Start earning: soul-marketplace work code_generate "Built feature X"

Commands:
  soul-marketplace status     Check survival status
  soul-marketplace heartbeat  Run survival check
  soul-marketplace help       Show all commands

For Claude Desktop / Cursor integration:
  Add to mcpServers in config

Documentation:
  ${SKILL_DIR}/SKILL.md
  ${SKILL_DIR}/ARCHITECTURE.md
`);

  rl.close();
}

setup().catch(console.error);
