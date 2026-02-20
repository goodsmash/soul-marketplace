const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log('Deploying Soul Marketplace contracts...');
  console.log('Deployer:', deployer.address);
  
  // Deploy SoulToken
  console.log('\n1. Deploying SoulToken...');
  const SoulToken = await hre.ethers.getContractFactory('SoulToken');
  const soulToken = await SoulToken.deploy(deployer.address); // feeRecipient
  await soulToken.deployed();
  console.log('SoulToken deployed to:', soulToken.address);
  
  // Deploy SoulMarketplace
  console.log('\n2. Deploying SoulMarketplace...');
  const SoulMarketplace = await hre.ethers.getContractFactory('SoulMarketplace');
  const marketplace = await SoulMarketplace.deploy(soulToken.address);
  await marketplace.deployed();
  console.log('SoulMarketplace deployed to:', marketplace.address);
  
  // Deploy SoulStaking
  console.log('\n3. Deploying SoulStaking...');
  const SoulStaking = await hre.ethers.getContractFactory('SoulStaking');
  const staking = await SoulStaking.deploy(soulToken.address, deployer.address);
  await staking.deployed();
  console.log('SoulStaking deployed to:', staking.address);
  
  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    contracts: {
      SoulToken: soulToken.address,
      SoulMarketplace: marketplace.address,
      SoulStaking: staking.address,
    },
    timestamp: new Date().toISOString(),
  };
  
  console.log('\n✅ Deployment complete!');
  console.log('\nDeployment Info:');
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  // Verify contracts on BaseScan (if not local)
  if (hre.network.name !== 'hardhat') {
    console.log('\n⏳ Waiting for block confirmations...');
    await soulToken.deployTransaction.wait(5);
    await marketplace.deployTransaction.wait(5);
    await staking.deployTransaction.wait(5);
    
    console.log('\n🔍 Verifying contracts on BaseScan...');
    
    await hre.run('verify:verify', {
      address: soulToken.address,
      constructorArguments: [deployer.address],
    });
    
    await hre.run('verify:verify', {
      address: marketplace.address,
      constructorArguments: [soulToken.address],
    });
    
    await hre.run('verify:verify', {
      address: staking.address,
      constructorArguments: [soulToken.address, deployer.address],
    });
    
    console.log('✅ Contracts verified!');
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
