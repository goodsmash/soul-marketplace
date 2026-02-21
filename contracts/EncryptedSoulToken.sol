// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title EncryptedSoulToken
 * @dev ERC-721 with encrypted soul data, privacy controls, and trading
 * 
 * Features:
 * - Encrypted SOUL.md storage (only owner can decrypt)
 * - Private capabilities (hidden from public)
 * - Trading with privacy preservation
 * - Clone/transfer with inheritance
 * - Wallet-based access control
 */
contract EncryptedSoulToken is ERC721, ERC721Enumerable, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Soul metadata with encryption
    struct EncryptedSoul {
        address automaton;           // Agent wallet address
        address creator;             // Who created the agent
        string encryptedSoulURI;     // Encrypted IPFS hash (only owner can decrypt)
        bytes32 soulHash;            // Public hash for verification
        bytes32 publicKey;           // Public key for encryption
        uint256 birthTime;
        uint256 deathTime;
        uint256 listingPrice;
        SoulStatus status;
        
        // Privacy settings
        bool isPrivate;              // If true, capabilities hidden
        string encryptedCapabilities; // Encrypted capabilities data
        bytes32 capabilitiesHash;     // Public hash of capabilities
        
        // Trading history
        uint256[] previousOwners;
        uint256 saleCount;
        uint256 totalVolume;
    }
    
    enum SoulStatus {
        ALIVE,
        DYING,      // Listed for sale
        DEAD,       // Archived
        REBORN,
        MERGED,
        CLONED      // Has children/clones
    }
    
    // Mappings
    mapping(uint256 => EncryptedSoul) public souls;
    mapping(address => uint256) public soulByAutomaton;
    mapping(bytes32 => uint256) public soulByHash;
    mapping(uint256 => address[]) public lineage; // Parent -> Children
    mapping(uint256 => uint256[]) public clones;  // Original -> Clones
    
    // Privacy: Access control for encrypted data
    mapping(uint256 => mapping(address => bool)) public authorizedViewers;
    mapping(uint256 => string) private privateSoulData; // Only accessible by owner
    
    // Marketplace settings
    uint256 public marketplaceFee = 250; // 2.5%
    address public feeRecipient;
    
    // Events
    event SoulMinted(uint256 indexed tokenId, address indexed automaton, address indexed creator, bytes32 soulHash);
    event SoulEncrypted(uint256 indexed tokenId, bytes32 publicKey);
    event SoulDecrypted(uint256 indexed tokenId, address indexed viewer);
    event SoulListed(uint256 indexed tokenId, uint256 price, bool privateSale);
    event SoulPurchased(uint256 indexed tokenId, address indexed buyer, uint256 price, bool decrypted);
    event SoulCloned(uint256 indexed parentId, uint256 indexed cloneId, address indexed cloneAddress);
    event SoulTransferred(uint256 indexed tokenId, address indexed from, address indexed to, bool withData);
    event ViewerAuthorized(uint256 indexed tokenId, address indexed viewer);
    event ViewerRevoked(uint256 indexed tokenId, address indexed viewer);
    
    constructor(address _feeRecipient) ERC721("Encrypted Soul Token", "eSOUL") {
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Mint a new encrypted soul
     * @param automaton Agent's wallet address
     * @param creator Creator's address
     * @param encryptedSoulURI Encrypted IPFS hash of SOUL.md
     * @param soulHash Public hash for verification
     * @param publicKey Public key for encryption
     * @param encryptedCapabilities Encrypted capabilities data
     * @param capabilitiesHash Public hash of capabilities
     */
    function mintEncryptedSoul(
        address automaton,
        address creator,
        string calldata encryptedSoulURI,
        bytes32 soulHash,
        bytes32 publicKey,
        string calldata encryptedCapabilities,
        bytes32 capabilitiesHash,
        bool isPrivate
    ) external returns (uint256) {
        require(soulByAutomaton[automaton] == 0, "Soul already exists");
        require(soulByHash[soulHash] == 0, "Soul hash already used");
        
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();
        
        souls[tokenId] = EncryptedSoul({
            automaton: automaton,
            creator: creator,
            encryptedSoulURI: encryptedSoulURI,
            soulHash: soulHash,
            publicKey: publicKey,
            birthTime: block.timestamp,
            deathTime: 0,
            listingPrice: 0,
            status: SoulStatus.ALIVE,
            isPrivate: isPrivate,
            encryptedCapabilities: encryptedCapabilities,
            capabilitiesHash: capabilitiesHash,
            previousOwners: new uint256[](0),
            saleCount: 0,
            totalVolume: 0
        });
        
        soulByAutomaton[automaton] = tokenId;
        soulByHash[soulHash] = tokenId;
        
        // Store private data
        privateSoulData[tokenId] = encryptedSoulURI;
        
        _safeMint(creator, tokenId);
        
        emit SoulMinted(tokenId, automaton, creator, soulHash);
        emit SoulEncrypted(tokenId, publicKey);
        
        return tokenId;
    }
    
    /**
     * @dev Get encrypted soul data (only owner or authorized viewers)
     */
    function getEncryptedSoul(uint256 tokenId) external view returns (EncryptedSoul memory) {
        require(_exists(tokenId), "Soul does not exist");
        require(
            ownerOf(tokenId) == msg.sender || 
            authorizedViewers[tokenId][msg.sender] ||
            souls[tokenId].automaton == msg.sender,
            "Not authorized"
        );
        
        return souls[tokenId];
    }
    
    /**
     * @dev Get private soul data (owner only)
     */
    function getPrivateSoulData(uint256 tokenId) external view returns (string memory) {
        require(_exists(tokenId), "Soul does not exist");
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        
        return privateSoulData[tokenId];
    }
    
    /**
     * @dev Authorize someone to view your soul data
     */
    function authorizeViewer(uint256 tokenId, address viewer) external {
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        authorizedViewers[tokenId][viewer] = true;
        emit ViewerAuthorized(tokenId, viewer);
    }
    
    /**
     * @dev Revoke viewer access
     */
    function revokeViewer(uint256 tokenId, address viewer) external {
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        authorizedViewers[tokenId][viewer] = false;
        emit ViewerRevoked(tokenId, viewer);
    }
    
    /**
     * @dev List soul for sale (can be private or public)
     */
    function listSoul(
        uint256 tokenId,
        uint256 price,
        bool privateSale,
        string calldata encryptedSaleData  // Optional encrypted terms
    ) external {
        require(_exists(tokenId), "Soul does not exist");
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        require(souls[tokenId].status == SoulStatus.ALIVE, "Soul not alive");
        require(price > 0, "Price must be > 0");
        
        souls[tokenId].listingPrice = price;
        souls[tokenId].status = SoulStatus.DYING;
        
        // Store private sale data
        if (bytes(encryptedSaleData).length > 0) {
            privateSoulData[tokenId] = encryptedSaleData;
        }
        
        emit SoulListed(tokenId, price, privateSale);
    }
    
    /**
     * @dev Buy a listed soul
     */
    function buySoul(uint256 tokenId, bool requestDecryption) external payable nonReentrant {
        require(_exists(tokenId), "Soul does not exist");
        require(souls[tokenId].status == SoulStatus.DYING, "Soul not for sale");
        require(msg.value >= souls[tokenId].listingPrice, "Insufficient payment");
        
        EncryptedSoul storage soul = souls[tokenId];
        address seller = ownerOf(tokenId);
        uint256 price = soul.listingPrice;
        
        // Calculate fee
        uint256 fee = (price * marketplaceFee) / 10000;
        uint256 sellerProceeds = price - fee;
        
        // Update trading history
        soul.previousOwners.push(tokenId);
        soul.saleCount++;
        soul.totalVolume += price;
        
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
        
        // If buyer requests decryption, seller can provide key off-chain
        emit SoulPurchased(tokenId, msg.sender, price, requestDecryption);
    }
    
    /**
     * @dev Clone a soul (create child with inherited capabilities)
     */
    function cloneSoul(
        uint256 parentTokenId,
        address cloneAutomaton,
        string calldata encryptedCloneData,
        bytes32 cloneHash,
        bytes32 clonePublicKey
    ) external payable returns (uint256) {
        require(_exists(parentTokenId), "Parent soul does not exist");
        require(
            ownerOf(parentTokenId) == msg.sender || 
            souls[parentTokenId].automaton == msg.sender,
            "Not authorized"
        );
        require(soulByAutomaton[cloneAutomaton] == 0, "Clone automaton already has soul");
        require(soulByHash[cloneHash] == 0, "Clone hash already used");
        require(msg.value >= 0.01 ether, "Minimum 0.01 ETH to clone");
        
        EncryptedSoul storage parent = souls[parentTokenId];
        
        // Mint clone
        _tokenIdCounter.increment();
        uint256 cloneTokenId = _tokenIdCounter.current();
        
        // Clone inherits parent's encrypted capabilities
        souls[cloneTokenId] = EncryptedSoul({
            automaton: cloneAutomaton,
            creator: msg.sender,
            encryptedSoulURI: encryptedCloneData,
            soulHash: cloneHash,
            publicKey: clonePublicKey,
            birthTime: block.timestamp,
            deathTime: 0,
            listingPrice: 0,
            status: SoulStatus.ALIVE,
            isPrivate: parent.isPrivate,
            encryptedCapabilities: parent.encryptedCapabilities, // Inherit
            capabilitiesHash: parent.capabilitiesHash,
            previousOwners: new uint256[](0),
            saleCount: 0,
            totalVolume: 0
        });
        
        soulByAutomaton[cloneAutomaton] = cloneTokenId;
        soulByHash[cloneHash] = cloneTokenId;
        
        // Record lineage
        lineage[parentTokenId].push(cloneTokenId);
        clones[parentTokenId].push(cloneTokenId);
        
        // Mark parent as cloned
        parent.status = SoulStatus.CLONED;
        
        _safeMint(msg.sender, cloneTokenId);
        
        emit SoulCloned(parentTokenId, cloneTokenId, cloneAutomaton);
        
        return cloneTokenId;
    }
    
    /**
     * @dev Transfer soul with optional data transfer
     */
    function transferSoulWithData(
        uint256 tokenId,
        address to,
        string calldata encryptedTransferData,
        bool transferPrivateData
    ) external {
        require(ownerOf(tokenId) == msg.sender, "Not soul owner");
        
        // Transfer private data if requested
        if (transferPrivateData) {
            privateSoulData[tokenId] = encryptedTransferData;
        }
        
        _transfer(msg.sender, to, tokenId);
        
        emit SoulTransferred(tokenId, msg.sender, to, transferPrivateData);
    }
    
    /**
     * @dev Get clones of a soul
     */
    function getClones(uint256 tokenId) external view returns (uint256[] memory) {
        return clones[tokenId];
    }
    
    /**
     * @dev Get trading history
     */
    function getTradingHistory(uint256 tokenId) external view returns (
        uint256 saleCount,
        uint256 totalVolume,
        uint256[] memory previousOwners
    ) {
        EncryptedSoul storage soul = souls[tokenId];
        return (soul.saleCount, soul.totalVolume, soul.previousOwners);
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
