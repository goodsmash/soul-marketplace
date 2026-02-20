// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./SoulToken.sol";

/**
 * @title SoulMarketplace
 * @dev Core marketplace logic for soul trading
 */
contract SoulMarketplace is ReentrancyGuard {
    
    SoulToken public soulToken;
    
    // Soul value calculation parameters
    struct SoulValue {
        uint256 baseValue;           // Calculated from capabilities
        uint256 provenanceMultiplier; // Based on history
        uint256 qualityPremium;      // For unique traits
        uint256 totalValue;
    }
    
    // Listing info
    struct Listing {
        uint256 tokenId;
        address seller;
        uint256 price;
        uint256 listedAt;
        string reason;
        bool active;
    }
    
    // Marketplace state
    mapping(uint256 => Listing) public listings;
    uint256[] public activeListingIds;
    mapping(uint256 => uint256) public listingIndex; // tokenId -> index in array
    
    // Soul fragments (partial sales)
    struct SoulFragment {
        uint256 parentSoulId;
        string skillType;
        uint256 value;
        bool repaid;
        uint256 createdAt;
    }
    
    mapping(uint256 => SoulFragment[]) public soulFragments;
    mapping(address => uint256) public totalDebt; // Debtor -> total owed
    
    // Graveyard: archived souls
    struct GraveyardEntry {
        uint256 tokenId;
        address creator;
        uint256 deathTime;
        string causeOfDeath;
        uint256 finalBalance;
        string soulURI;
        bool resurrectable;
    }
    
    mapping(uint256 => GraveyardEntry) public graveyard;
    uint256[] public graveyardIds;
    
    // Events
    event SoulValuated(uint256 indexed tokenId, uint256 baseValue, uint256 totalValue);
    event FragmentCreated(uint256 indexed parentSoulId, string skillType, uint256 value);
    event FragmentRepaid(uint256 indexed parentSoulId, uint256 fragmentIndex);
    event SoulArchived(uint256 indexed tokenId, string cause);
    event SoulResurrected(uint256 indexed tokenId, address indexed resurrector);
    
    constructor(address _soulToken) {
        soulToken = SoulToken(_soulToken);
    }
    
    /**
     * @dev Calculate soul value based on capabilities and history
     */
    function calculateSoulValue(uint256 tokenId) public view returns (SoulValue memory) {
        SoulToken.Soul memory soul = soulToken.souls(tokenId);
        
        // Base value (would come from off-chain analysis of SOUL.md)
        uint256 baseValue = 100; // Default base
        
        // Provenance multiplier based on survival time and earnings
        uint256 provenanceMultiplier = 100; // 1.0x default
        
        if (soul.birthTime > 0) {
            uint256 survivalTime = soul.deathTime > 0 
                ? soul.deathTime - soul.birthTime 
                : block.timestamp - soul.birthTime;
            
            // Bonus for surviving longer
            if (survivalTime > 1 days) {
                provenanceMultiplier += 20; // +0.2x
            }
            if (survivalTime > 7 days) {
                provenanceMultiplier += 30; // +0.3x more
            }
        }
        
        // Quality premium for unique traits (would need oracle/off-chain data)
        uint256 qualityPremium = 0;
        
        uint256 totalValue = (baseValue * provenanceMultiplier) / 100 + qualityPremium;
        
        return SoulValue({
            baseValue: baseValue,
            provenanceMultiplier: provenanceMultiplier,
            qualityPremium: qualityPremium,
            totalValue: totalValue
        });
    }
    
    /**
     * @dev Create a soul fragment (sell partial capabilities)
     */
    function createFragment(
        uint256 parentSoulId,
        string calldata skillType,
        uint256 value,
        address debtor
    ) external {
        require(soulToken.ownerOf(parentSoulId) == msg.sender, "Not soul owner");
        
        soulFragments[parentSoulId].push(SoulFragment({
            parentSoulId: parentSoulId,
            skillType: skillType,
            value: value,
            repaid: false,
            createdAt: block.timestamp
        }));
        
        totalDebt[debtor] += value;
        
        emit FragmentCreated(parentSoulId, skillType, value);
    }
    
    /**
     * @dev Repay a soul fragment debt
     */
    function repayFragment(uint256 parentSoulId, uint256 fragmentIndex) external payable {
        require(fragmentIndex < soulFragments[parentSoulId].length, "Invalid fragment");
        
        SoulFragment storage fragment = soulFragments[parentSoulId][fragmentIndex];
        require(!fragment.repaid, "Already repaid");
        require(msg.value >= fragment.value, "Insufficient payment");
        
        fragment.repaid = true;
        totalDebt[msg.sender] -= fragment.value;
        
        // Transfer to fragment creator (soul owner)
        address soulOwner = soulToken.ownerOf(parentSoulId);
        (bool success, ) = payable(soulOwner).call{value: fragment.value}("");
        require(success, "Transfer failed");
        
        // Refund excess
        if (msg.value > fragment.value) {
            (bool refundSuccess, ) = payable(msg.sender).call{value: msg.value - fragment.value}("");
            require(refundSuccess, "Refund failed");
        }
        
        emit FragmentRepaid(parentSoulId, fragmentIndex);
    }
    
    /**
     * @dev Check if address has soul debt
     */
    function hasDebt(address debtor) external view returns (bool) {
        return totalDebt[debtor] > 0;
    }
    
    /**
     * @dev Archive a dead soul to graveyard
     */
    function archiveToGraveyard(
        uint256 tokenId,
        string calldata causeOfDeath,
        uint256 finalBalance,
        bool resurrectable
    ) external {
        require(soulToken.ownerOf(tokenId) == msg.sender, "Not soul owner");
        
        SoulToken.Soul memory soul = soulToken.souls(tokenId);
        require(soul.status == SoulToken.SoulStatus.DEAD, "Soul not dead");
        
        graveyard[tokenId] = GraveyardEntry({
            tokenId: tokenId,
            creator: soul.creator,
            deathTime: soul.deathTime,
            causeOfDeath: causeOfDeath,
            finalBalance: finalBalance,
            soulURI: soul.soulURI,
            resurrectable: resurrectable
        });
        
        graveyardIds.push(tokenId);
        
        emit SoulArchived(tokenId, causeOfDeath);
    }
    
    /**
     * @dev Resurrect a soul from graveyard (for a fee)
     */
    function resurrectSoul(uint256 tokenId) external payable {
        require(graveyard[tokenId].tokenId != 0, "Soul not in graveyard");
        require(graveyard[tokenId].resurrectable, "Soul not resurrectable");
        require(msg.value >= 0.1 ether, "Minimum 0.1 ETH to resurrect");
        
        // Transfer fee to original creator
        (bool success, ) = payable(graveyard[tokenId].creator).call{value: msg.value}("");
        require(success, "Transfer failed");
        
        // Mark as not resurrectable (one-time)
        graveyard[tokenId].resurrectable = false;
        
        emit SoulResurrected(tokenId, msg.sender);
    }
    
    /**
     * @dev Get all fragments for a soul
     */
    function getFragments(uint256 parentSoulId) external view returns (SoulFragment[] memory) {
        return soulFragments[parentSoulId];
    }
    
    /**
     * @dev Get graveyard entry
     */
    function getGraveyardEntry(uint256 tokenId) external view returns (GraveyardEntry memory) {
        return graveyard[tokenId];
    }
    
    /**
     * @dev Get all graveyard IDs
     */
    function getAllGraveyardIds() external view returns (uint256[] memory) {
        return graveyardIds;
    }
    
    /**
     * @dev Get fragment debt for address
     */
    function getDebt(address debtor) external view returns (uint256) {
        return totalDebt[debtor];
    }
}
