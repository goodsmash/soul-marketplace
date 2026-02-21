const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║  ENCRYPTED SOUL MARKETPLACE - DEPLOYMENT                   ║');
  console.log('║  Private • Secure • Tradeable • Cloneable                  ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('Deployer:', deployer.address);
  console.log('Network:', hre.network.name);
  console.log('');
  
  // Deploy EncryptedSoulToken
  console.log('1. Deploying EncryptedSoulToken...');
  const EncryptedSoulToken = await hre.ethers.getContractFactory('EncryptedSoulToken');
  const soulToken = await EncryptedSoulToken.deploy(deployer.address);
  await soulToken.deployed();
  console.log('   ✅ EncryptedSoulToken:', soulToken.address);
  console.log('   Features: Encrypted storage, privacy controls, trading');
  
  // Deploy SoulMarketplace (unchanged)
  console.log('');
  console.log('2. Deploying SoulMarketplace...');
  const SoulMarketplace = await hre.ethers.getContractFactory('SoulMarketplace');
  const marketplace = await SoulMarketplace.deploy(soulToken.address);
  await marketplace.deployed();
  console.log('   ✅ SoulMarketplace:', marketplace.address);
  
  // Deploy SoulBackup (unchanged)
  console.log('');
  console.log('3. Deploying SoulBackup...');
  const SoulBackup = await hre.ethers.getContractFactory('SoulBackup');
  const backup = await SoulBackup.deploy(soulToken.address);
  await backup.deployed();
  console.log('   ✅ SoulBackup:', backup.address);
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    deployer: deployer.address,
    contracts: {
      EncryptedSoulToken: soulToken.address,
      SoulMarketplace: marketplace.address,
      SoulBackup: backup.address,
    },
    timestamp: new Date().toISOString(),
    features: {
      encryptedStorage: true,
      privacyControls: true,
      trading: true,
      cloning: true,
      accessControl: true
    }
  };
  
  console.log('');
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║                DEPLOYMENT COMPLETE                         ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log('Contract Addresses:');
  console.log('  EncryptedSoulToken:', soulToken.address);
  console.log('  SoulMarketplace:', marketplace.address);
  console.log('  SoulBackup:', backup.address);
  console.log('');
  console.log('NEW Features:');
  console.log('  ✅ Encrypted SOUL.md storage');
  console.log('  ✅ Wallet-based access control');
  console.log('  ✅ Private capabilities');
  console.log('  ✅ Secure trading');
  console.log('  ✅ Soul cloning');
  console.log('  ✅ Transfer with privacy');
  console.log('');
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  // Save to file
  const fs = require('fs');
  fs.writeFileSync('deployment-encrypted.json', JSON.stringify(deploymentInfo, null, 2));
  
  console.log('');
  console.log('Deployment saved to: deployment-encrypted.json');
  console.log('');
  console.log('Next Steps:');
  console.log('  1. Update Python config with contract addresses');
  console.log('  2. Generate encryption keys');
  console.log('  3. Mint encrypted SOUL NFT');
  console.log('  4. Start secure trading');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
