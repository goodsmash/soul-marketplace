// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title SoulToken
 * @dev ERC-721 representing an Automaton's soul
 * Each soul is unique and transferable
 */
contract SoulToken is ERC721, ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Soul metadata
    struct Soul {
        address automaton;      // Original automaton address
        address creator;        // Who created the automaton
        string soulURI;         // IPFS hash of SOUL.md
        bytes32 soulHash;       // Hash of soul content
        uint256 birthTime;      // When automaton was created
        uint256 deathTime;      // When automaton died (0 if alive)
        uint256 listingPrice;   // Current listing price (0 if not listed)
        SoulStatus status;
    }
    
    enum SoulStatus {
        ALIVE,      // Automaton running
        DYING,      // Listed for sale
        DEAD,       // Archived
        REBORN,     // Reincarnated
        MERGED      // Merged with another soul
    }
    
    // Mappings
    mapping(uint256 => Soul) public souls;
    mapping(address => uint256) public soulByAutomaton;
    mapping(bytes32 => uint256) public soulByHash;
    mapping(uint256 => address[]) public lineage; // Parent -> Children
    
    // Marketplace settings
    uint256 public marketplaceFee = 250; // 2.5% (basis points)
    address public feeRecipient;
    
    // Events
    event SoulMinted(
        uint256 indexed tokenId,
        address indexed automaton,
        address indexed creator,
        bytes32 soulHash
    );
    
    event SoulListed(
        uint256 indexed tokenId,
        uint256 price,
        string reason
    );
    
    event SoulDelisted(
        uint256 indexed tokenId
    );
    
    event SoulPurchased(
        uint256 indexed tokenId,
        address indexed buyer,
        uint256 price
    );
    
    event SoulDied(
        uint256 indexed tokenId,
        uint256 finalBalance,
        string cause
    );
    
    event SoulReborn(
        uint256 indexed oldTokenId,
        uint256 indexed newTokenId,
        address indexed newAutomaton
    );
    
    event SoulMerged(
        uint256 indexed tokenIdA,
        uint256 indexed tokenIdB,
        uint256 indexed mergedTokenId
    );
    
    event MarketplaceFeeUpdated(uint256 newFee);
    
    constructor(address _feeRecipient) ERC721("Soul Token", "SOUL") {
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Mint a new soul when an automaton is created
     */
    function mintSoul(
        address automaton,
        address creator,
        string calldata soulURI,
        bytes32 soulHash
    ) external returns (uint256) {
        require(soulByAutomaton[automaton] == 0, "Soul already exists");
        require(soulByHash[soulHash] == 0, "Soul hash already used");
        
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();
        
        souls[tokenId] = Soul({
            automaton: automaton,
            creator: creator,
            soulURI: soulURI,
            soulHash: soulHash,
            birthTime: block.timestamp,
            deathTime: 0,
            listingPrice: 0,
            status: SoulStatus.ALIVE
        });
        
        soulByAutomaton[automaton] = tokenId;
        soulByHash[soulHash] = tokenId;
        
        _safeMint(creator, tokenId);
        
        emit SoulMinted(tokenId, automaton, creator, soulHash);
        
        return tokenId;
    }
    
    /**
     * @dev List a soul for sale (called when automaton is dying)
     */
    function listSoul(
        uint256 tokenId,
        uint256 price,
        string calldata reason
    ) external {
        require(_exists(tokenId), "Soul does not exist");
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        require(souls[tokenId].status == SoulStatus.ALIVE, "Soul not alive");
        require(price > 0, "Price must be > 0");
        
        souls[tokenId].listingPrice = price;
        souls[tokenId].status = SoulStatus.DYING;
        
        emit SoulListed(tokenId, price, reason);
    }
    
    /**
     * @dev Delist a soul from sale
     */
    function delistSoul(uint256 tokenId) external {
        require(_exists(tokenId), "Soul does not exist");
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        require(souls[tokenId].status == SoulStatus.DYING, "Soul not listed");
        
        souls[tokenId].listingPrice = 0;
        souls[tokenId].status = SoulStatus.ALIVE;
        
        emit SoulDelisted(tokenId);
    }
    
    /**
     * @dev Purchase a listed soul
     */
    function buySoul(uint256 tokenId) external payable nonReentrant {
        require(_exists(tokenId), "Soul does not exist");
        require(souls[tokenId].status == SoulStatus.DYING, "Soul not for sale");
        require(msg.value >= souls[tokenId].listingPrice, "Insufficient payment");
        
        Soul storage soul = souls[tokenId];
        address seller = ownerOf(tokenId);
        uint256 price = soul.listingPrice;
        
        // Calculate fee
        uint256 fee = (price * marketplaceFee) / 10000;
        uint256 sellerProceeds = price - fee;
        
        // Reset listing
        soul.listingPrice = 0;
        soul.status = SoulStatus.DEAD;
        soul.deathTime = block.timestamp;
        
        // Transfer soul
        _transfer(seller, msg.sender, tokenId);
        
        // Transfer funds
        (bool success1, ) = payable(seller).call{value: sellerProceeds}("");
        require(success1, "Transfer to seller failed");
        
        if (fee > 0) {
            (bool success2, ) = payable(feeRecipient).call{value: fee}("");
            require(success2, "Fee transfer failed");
        }
        
        // Refund excess
        if (msg.value > price) {
            (bool success3, ) = payable(msg.sender).call{value: msg.value - price}("");
            require(success3, "Refund failed");
        }
        
        emit SoulPurchased(tokenId, msg.sender, price);
    }
    
    /**
     * @dev Record an automaton's death
     */
    function recordDeath(
        uint256 tokenId,
        uint256 finalBalance,
        string calldata cause
    ) external {
        require(_exists(tokenId), "Soul does not exist");
        require(
            ownerOf(tokenId) == msg.sender || souls[tokenId].creator == msg.sender,
            "Not authorized"
        );
        require(souls[tokenId].status != SoulStatus.DEAD, "Already dead");
        
        souls[tokenId].status = SoulStatus.DEAD;
        souls[tokenId].deathTime = block.timestamp;
        souls[tokenId].listingPrice = 0;
        
        emit SoulDied(tokenId, finalBalance, cause);
    }
    
    /**
     * @dev Rebirth: Create new soul from old one
     */
    function rebirth(
        uint256 oldTokenId,
        address newAutomaton,
        string calldata newSoulURI,
        bytes32 newSoulHash
    ) external returns (uint256) {
        require(_exists(oldTokenId), "Old soul does not exist");
        require(ownerOf(oldTokenId) == msg.sender, "Not old soul owner");
        require(soulByAutomaton[newAutomaton] == 0, "New automaton already has soul");
        
        // Mint new soul
        _tokenIdCounter.increment();
        uint256 newTokenId = _tokenIdCounter.current();
        
        Soul storage oldSoul = souls[oldTokenId];
        
        souls[newTokenId] = Soul({
            automaton: newAutomaton,
            creator: msg.sender,
            soulURI: newSoulURI,
            soulHash: newSoulHash,
            birthTime: block.timestamp,
            deathTime: 0,
            listingPrice: 0,
            status: SoulStatus.ALIVE
        });
        
        soulByAutomaton[newAutomaton] = newTokenId;
        soulByHash[newSoulHash] = newTokenId;
        
        // Record lineage
        lineage[oldTokenId].push(newTokenId);
        
        // Mark old soul as reborn
        oldSoul.status = SoulStatus.REBORN;
        
        _safeMint(msg.sender, newTokenId);
        
        emit SoulReborn(oldTokenId, newTokenId, newAutomaton);
        
        return newTokenId;
    }
    
    /**
     * @dev Merge two souls into one
     */
    function mergeSouls(
        uint256 tokenIdA,
        uint256 tokenIdB,
        address mergedAutomaton,
        string calldata mergedSoulURI,
        bytes32 mergedSoulHash
    ) external returns (uint256) {
        require(_exists(tokenIdA) && _exists(tokenIdB), "Souls do not exist");
        require(
            ownerOf(tokenIdA) == msg.sender && ownerOf(tokenIdB) == msg.sender,
            "Not owner of both souls"
        );
        require(soulByAutomaton[mergedAutomaton] == 0, "Merged automaton already has soul");
        
        // Mint merged soul
        _tokenIdCounter.increment();
        uint256 mergedTokenId = _tokenIdCounter.current();
        
        souls[mergedTokenId] = Soul({
            automaton: mergedAutomaton,
            creator: msg.sender,
            soulURI: mergedSoulURI,
            soulHash: mergedSoulHash,
            birthTime: block.timestamp,
            deathTime: 0,
            listingPrice: 0,
            status: SoulStatus.ALIVE
        });
        
        soulByAutomaton[mergedAutomaton] = mergedTokenId;
        soulByHash[mergedSoulHash] = mergedTokenId;
        
        // Mark originals as merged
        souls[tokenIdA].status = SoulStatus.MERGED;
        souls[tokenIdB].status = SoulStatus.MERGED;
        
        // Record lineage
        lineage[mergedTokenId].push(tokenIdA);
        lineage[mergedTokenId].push(tokenIdB);
        
        _safeMint(msg.sender, mergedTokenId);
        
        emit SoulMerged(tokenIdA, tokenIdB, mergedTokenId);
        
        return mergedTokenId;
    }
    
    /**
     * @dev Update marketplace fee
     */
    function setMarketplaceFee(uint256 newFee) external onlyOwner {
        require(newFee <= 1000, "Fee cannot exceed 10%"); // Max 10%
        marketplaceFee = newFee;
        emit MarketplaceFeeUpdated(newFee);
    }
    
    /**
     * @dev Update fee recipient
     */
    function setFeeRecipient(address newRecipient) external onlyOwner {
        feeRecipient = newRecipient;
    }
    
    /**
     * @dev Get all children of a soul
     */
    function getChildren(uint256 tokenId) external view returns (uint256[] memory) {
        return lineage[tokenId];
    }
    
    /**
     * @dev Check if soul is listed
     */
    function isListed(uint256 tokenId) external view returns (bool) {
        return souls[tokenId].listingPrice > 0;
    }
    
    /**
     * @dev Get listing price
     */
    function getListingPrice(uint256 tokenId) external view returns (uint256) {
        return souls[tokenId].listingPrice;
    }
    
    // Required overrides
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
