const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('SoulToken', function () {
  let SoulToken, soulToken, owner, addr1, addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    
    SoulToken = await ethers.getContractFactory('SoulToken');
    soulToken = await SoulToken.deploy(owner.address);
    await soulToken.waitForDeployment();
  });

  describe('Deployment', function () {
    it('Should set the right owner', async function () {
      expect(await soulToken.owner()).to.equal(owner.address);
    });

    it('Should have correct name and symbol', async function () {
      expect(await soulToken.name()).to.equal('Soul Token');
      expect(await soulToken.symbol()).to.equal('SOUL');
    });
  });

  describe('Minting', function () {
    it('Should mint a new soul', async function () {
      const automaton = addr1.address;
      const creator = owner.address;
      const soulURI = 'ipfs://QmTest';
      const soulHash = ethers.keccak256(ethers.toUtf8Bytes('test soul'));

      await expect(soulToken.mintSoul(automaton, creator, soulURI, soulHash))
        .to.emit(soulToken, 'SoulMinted')
        .withArgs(1, automaton, creator, soulHash);

      expect(await soulToken.ownerOf(1)).to.equal(creator);
      
      const soul = await soulToken.souls(1);
      expect(soul.automaton).to.equal(automaton);
      expect(soul.creator).to.equal(creator);
      expect(soul.soulURI).to.equal(soulURI);
      expect(soul.soulHash).to.equal(soulHash);
      expect(soul.status).to.equal(0); // ALIVE
    });

    it('Should prevent duplicate soul for same automaton', async function () {
      const soulHash1 = ethers.keccak256(ethers.toUtf8Bytes('soul1'));
      const soulHash2 = ethers.keccak256(ethers.toUtf8Bytes('soul2'));

      await soulToken.mintSoul(addr1.address, owner.address, 'uri1', soulHash1);
      
      await expect(
        soulToken.mintSoul(addr1.address, owner.address, 'uri2', soulHash2)
      ).to.be.revertedWith('Soul already exists');
    });

    it('Should prevent duplicate soul hash', async function () {
      const soulHash = ethers.keccak256(ethers.toUtf8Bytes('unique soul'));

      await soulToken.mintSoul(addr1.address, owner.address, 'uri1', soulHash);
      
      await expect(
        soulToken.mintSoul(addr2.address, owner.address, 'uri2', soulHash)
      ).to.be.revertedWith('Soul hash already used');
    });
  });

  describe('Listing and Buying', function () {
    beforeEach(async function () {
      const soulHash = ethers.keccak256(ethers.toUtf8Bytes('test'));
      await soulToken.mintSoul(addr1.address, owner.address, 'uri', soulHash);
    });

    it('Should list a soul for sale', async function () {
      const price = ethers.parseEther('1.0');
      
      await expect(soulToken.listSoul(1, price, 'Need funds'))
        .to.emit(soulToken, 'SoulListed')
        .withArgs(1, price, 'Need funds');

      const soul = await soulToken.souls(1);
      expect(soul.listingPrice).to.equal(price);
      expect(soul.status).to.equal(1); // DYING
    });

    it('Should buy a listed soul', async function () {
      const price = ethers.parseEther('1.0');
      await soulToken.listSoul(1, price, 'For sale');

      await expect(
        soulToken.connect(addr1).buySoul(1, { value: price })
      ).to.emit(soulToken, 'SoulPurchased')
        .withArgs(1, addr1.address, price);

      expect(await soulToken.ownerOf(1)).to.equal(addr1.address);
      
      const soul = await soulToken.souls(1);
      expect(soul.status).to.equal(2); // DEAD
      expect(soul.listingPrice).to.equal(0);
    });

    it('Should refund excess payment', async function () {
      const price = ethers.parseEther('1.0');
      await soulToken.listSoul(1, price, 'For sale');

      const balanceBefore = await ethers.provider.getBalance(addr1.address);
      
      const tx = await soulToken.connect(addr1).buySoul(1, { value: ethers.parseEther('1.5') });
      const receipt = await tx.wait();
      
      const gasUsed = receipt.gasUsed * receipt.gasPrice;
      const balanceAfter = await ethers.provider.getBalance(addr1.address);
      
      // Should have spent ~1.0 ETH + gas, not 1.5 ETH
      const spent = balanceBefore - balanceAfter - gasUsed;
      expect(spent).to.be.closeTo(price, ethers.parseEther('0.01'));
    });
  });

  describe('Rebirth', function () {
    beforeEach(async function () {
      const soulHash = ethers.keccak256(ethers.toUtf8Bytes('test'));
      await soulToken.mintSoul(addr1.address, owner.address, 'uri', soulHash);
      
      const price = ethers.parseEther('1.0');
      await soulToken.listSoul(1, price, 'For sale');
      await soulToken.connect(addr1).buySoul(1, { value: price });
    });

    it('Should rebirth a soul', async function () {
      const newAutomaton = addr2.address;
      const newSoulHash = ethers.keccak256(ethers.toUtf8Bytes('reborn soul'));

      await expect(
        soulToken.connect(addr1).rebirth(1, newAutomaton, 'new uri', newSoulHash)
      ).to.emit(soulToken, 'SoulReborn')
        .withArgs(1, 2, newAutomaton);

      const newSoul = await soulToken.souls(2);
      expect(newSoul.automaton).to.equal(newAutomaton);
      expect(newSoul.status).to.equal(0); // ALIVE
      
      const oldSoul = await soulToken.souls(1);
      expect(oldSoul.status).to.equal(3); // REBORN
    });
  });

  describe('Merging', function () {
    beforeEach(async function () {
      const soulHash1 = ethers.keccak256(ethers.toUtf8Bytes('soul1'));
      const soulHash2 = ethers.keccak256(ethers.toUtf8Bytes('soul2'));
      
      await soulToken.mintSoul(addr1.address, owner.address, 'uri1', soulHash1);
      await soulToken.mintSoul(addr2.address, owner.address, 'uri2', soulHash2);
    });

    it('Should merge two souls', async function () {
      const mergedAutomaton = ethers.Wallet.createRandom().address;
      const mergedSoulHash = ethers.keccak256(ethers.toUtf8Bytes('merged'));

      await expect(
        soulToken.mergeSouls(1, 2, mergedAutomaton, 'merged uri', mergedSoulHash)
      ).to.emit(soulToken, 'SoulMerged')
        .withArgs(1, 2, 3);

      const mergedSoul = await soulToken.souls(3);
      expect(mergedSoul.automaton).to.equal(mergedAutomaton);
      expect(mergedSoul.status).to.equal(0); // ALIVE

      const soul1 = await soulToken.souls(1);
      const soul2 = await soulToken.souls(2);
      expect(soul1.status).to.equal(4); // MERGED
      expect(soul2.status).to.equal(4); // MERGED
    });
  });
});
