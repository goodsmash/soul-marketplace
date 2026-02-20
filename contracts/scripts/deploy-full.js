const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     SOUL MARKETPLACE - COMPLETE DEPLOYMENT                 ║');
  console.log('║     With On-Chain Backup System                            ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('Deployer:', deployer.address);
  console.log('Network:', hre.network.name);
  console.log('');
  
  // Deploy SoulToken
  console.log('1. Deploying SoulToken (ERC-721)...');
  const SoulToken = await hre.ethers.getContractFactory('SoulToken');
  const soulToken = await SoulToken.deploy(deployer.address);
  await soulToken.deployed();
  console.log('   ✅ SoulToken:', soulToken.address);
  
  // Deploy SoulMarketplace
  console.log('');
  console.log('2. Deploying SoulMarketplace...');
  const SoulMarketplace = await hre.ethers.getContractFactory('SoulMarketplace');
  const marketplace = await SoulMarketplace.deploy(soulToken.address);
  await marketplace.deployed();
  console.log('   ✅ SoulMarketplace:', marketplace.address);
  
  // Deploy SoulStaking
  console.log('');
  console.log('3. Deploying SoulStaking...');
  const SoulStaking = await hre.ethers.getContractFactory('SoulStaking');
  const staking = await SoulStaking.deploy(soulToken.address, deployer.address);
  await staking.deployed();
  console.log('   ✅ SoulStaking:', staking.address);
  
  // Deploy SoulBackup (NEW)
  console.log('');
  console.log('4. Deploying SoulBackup (On-Chain Backup System)...');
  const SoulBackup = await hre.ethers.getContractFactory('SoulBackup');
  const backup = await SoulBackup.deploy(soulToken.address);
  await backup.deployed();
  console.log('   ✅ SoulBackup:', backup.address);
  
  // Set up contract relationships
  console.log('');
  console.log('5. Configuring contract relationships...');
  
  // Set marketplace as authorized minter if needed
  // (SoulToken already has mint function open)
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    deployer: deployer.address,
    contracts: {
      SoulToken: soulToken.address,
      SoulMarketplace: marketplace.address,
      SoulStaking: staking.address,
      SoulBackup: backup.address,  // NEW
    },
    timestamp: new Date().toISOString(),
    features: {
      onChainBackup: true,
      crossChainReplication: true,
      emergencyRecovery: true,
      ipfsIntegration: true
    }
  };
  
  console.log('');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║                DEPLOYMENT COMPLETE                         ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('Contract Addresses:');
  console.log('  SoulToken:', soulToken.address);
  console.log('  SoulMarketplace:', marketplace.address);
  console.log('  SoulStaking:', staking.address);
  console.log('  SoulBackup:', backup.address);
  console.log('');
  console.log('Features Enabled:');
  console.log('  ✅ Soul NFTs (ERC-721)');
  console.log('  ✅ Marketplace trading');
  console.log('  ✅ Staking on survival');
  console.log('  ✅ On-chain backups (NEW)');
  console.log('  ✅ Cross-chain replication');
  console.log('  ✅ Emergency recovery');
  console.log('');
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  // Save to file
  const fs = require('fs');
  fs.writeFileSync(
    'deployment.json',
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log('');
  console.log('Deployment saved to: deployment.json');
  
  // Update skill config
  console.log('');
  console.log('6. Updating skill configuration...');
  const skillConfig = {
    version: '1.1.0',
    network: hre.network.name,
    chain_id: deploymentInfo.chainId,
    rpc_url: hre.network.config.url,
    contracts: deploymentInfo.contracts,
    features: deploymentInfo.features,
    deployed_at: deploymentInfo.timestamp
  };
  
  // Save to skill directory
  const skillPath = require('path').join(
    require('os').homedir(),
    '.openclaw', 'skills', 'soul-marketplace',
    'config.json'
  );
  
  fs.writeFileSync(skillPath, JSON.stringify(skillConfig, null, 2));
  console.log('   ✅ Skill config updated:', skillPath);
  
  // Verify contracts if not local
  if (hre.network.name !== 'hardhat' && hre.network.name !== 'localhost') {
    console.log('');
    console.log('⏳ Waiting for block confirmations...');
    await soulToken.deployTransaction.wait(5);
    await marketplace.deployTransaction.wait(5);
    await staking.deployTransaction.wait(5);
    await backup.deployTransaction.wait(5);
    
    console.log('');
    console.log('🔍 Verifying contracts...');
    
    try {
      await hre.run('verify:verify', {
        address: soulToken.address,
        constructorArguments: [deployer.address],
      });
      console.log('   ✅ SoulToken verified');
    } catch (e) {
      console.log('   ⚠️ SoulToken verification failed (may already be verified)');
    }
    
    try {
      await hre.run('verify:verify', {
        address: marketplace.address,
        constructorArguments: [soulToken.address],
      });
      console.log('   ✅ SoulMarketplace verified');
    } catch (e) {
      console.log('   ⚠️ SoulMarketplace verification failed');
    }
    
    try {
      await hre.run('verify:verify', {
        address: staking.address,
        constructorArguments: [soulToken.address, deployer.address],
      });
      console.log('   ✅ SoulStaking verified');
    } catch (e) {
      console.log('   ⚠️ SoulStaking verification failed');
    }
    
    try {
      await hre.run('verify:verify', {
        address: backup.address,
        constructorArguments: [soulToken.address],
      });
      console.log('   ✅ SoulBackup verified');
    } catch (e) {
      console.log('   ⚠️ SoulBackup verification failed');
    }
  }
  
  console.log('');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║              READY FOR AGENT SURVIVAL                      ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('Next Steps:');
  console.log('  1. Fund your agent wallet with ETH');
  console.log('  2. Run: python3 enhanced_survival.py');
  console.log('  3. Mint your soul on-chain');
  console.log('  4. Enable automatic backups');
  console.log('');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
