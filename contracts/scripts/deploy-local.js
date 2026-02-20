const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log('Deploying Soul Marketplace to local Hardhat network...');
  console.log('Deployer:', deployer.address);
  console.log('Balance:', (await deployer.getBalance()).toString());
  
  // Deploy SoulToken
  console.log('\n1. Deploying SoulToken...');
  const SoulToken = await hre.ethers.getContractFactory('SoulToken');
  const soulToken = await SoulToken.deploy(deployer.address);
  await soulToken.deployed();
  console.log('✓ SoulToken deployed to:', soulToken.address);
  
  // Deploy SoulMarketplace
  console.log('\n2. Deploying SoulMarketplace...');
  const SoulMarketplace = await hre.ethers.getContractFactory('SoulMarketplace');
  const marketplace = await SoulMarketplace.deploy(soulToken.address);
  await marketplace.deployed();
  console.log('✓ SoulMarketplace deployed to:', marketplace.address);
  
  // Deploy SoulStaking
  console.log('\n3. Deploying SoulStaking...');
  const SoulStaking = await hre.ethers.getContractFactory('SoulStaking');
  const staking = await SoulStaking.deploy(soulToken.address, deployer.address);
  await staking.deployed();
  console.log('✓ SoulStaking deployed to:', staking.address);
  
  // Test: Mint a soul
  console.log('\n4. Testing: Minting a sample soul...');
  const soulHash = hre.ethers.keccak256(hre.ethers.toUtf8Bytes('Test Soul'));
  const tx = await soulToken.mintSoul(
    deployer.address, // automaton
    deployer.address, // creator
    'ipfs://QmTest123',
    soulHash
  );
  await tx.wait();
  console.log('✓ Sample soul minted with ID: 1');
  
  // Test: List soul
  console.log('\n5. Testing: Listing soul for sale...');
  const price = hre.ethers.utils.parseEther('0.1');
  await soulToken.listSoul(1, price, 'Test listing');
  console.log('✓ Soul listed for 0.1 ETH');
  
  // Save deployment info
  const deploymentInfo = {
    network: 'localhost',
    chainId: 31337,
    deployer: deployer.address,
    contracts: {
      SoulToken: soulToken.address,
      SoulMarketplace: marketplace.address,
      SoulStaking: staking.address,
    },
    sampleSoul: {
      id: 1,
      listingPrice: '0.1 ETH',
    },
    timestamp: new Date().toISOString(),
  };
  
  console.log('\n========================================');
  console.log('✅ LOCAL DEPLOYMENT SUCCESSFUL!');
  console.log('========================================');
  console.log('\nContract Addresses:');
  console.log('  SoulToken:', soulToken.address);
  console.log('  SoulMarketplace:', marketplace.address);
  console.log('  SoulStaking:', staking.address);
  console.log('\nSample soul minted (ID: 1) and listed for 0.1 ETH');
  console.log('\nNext steps:');
  console.log('  1. Connect UI to these addresses');
  console.log('  2. Test buying the sample soul');
  console.log('  3. Deploy to Base Sepolia');
  
  return deploymentInfo;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
