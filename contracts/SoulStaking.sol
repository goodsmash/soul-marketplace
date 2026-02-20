// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./SoulToken.sol";

/**
 * @title SoulStaking
 * @dev Stake on whether agents will survive or die
 */
contract SoulStaking is ReentrancyGuard {
    
    SoulToken public soulToken;
    
    // Stake types
    enum StakeType {
        SURVIVE,    // Staker believes agent will survive X hours
        DIE,        // Staker believes agent will die within X hours
        THRIVE      // Staker believes agent will earn Y amount
    }
    
    struct Stake {
        address staker;
        uint256 soulId;
        StakeType stakeType;
        uint256 amount;
        uint256 target;      // Hours for survive/die, earnings for thrive
        uint256 createdAt;
        uint256 expiresAt;   // When stake resolves
        bool resolved;
        bool won;
        uint256 payout;
    }
    
    // All stakes
    Stake[] public stakes;
    mapping(address => uint256[]) public stakesByStaker;
    mapping(uint256 => uint256[]) public stakesBySoul;
    
    // Pool for each soul
    struct StakePool {
        uint256 totalSurviveStakes;
        uint256 totalDieStakes;
        uint256 totalThriveStakes;
        uint256 survivePool;
        uint256 diePool;
        uint256 thrivePool;
    }
    
    mapping(uint256 => StakePool) public pools;
    
    // Platform fee
    uint256 public platformFee = 500; // 5%
    address public feeRecipient;
    
    // Events
    event StakeCreated(
        uint256 indexed stakeId,
        address indexed staker,
        uint256 indexed soulId,
        StakeType stakeType,
        uint256 amount,
        uint256 target
    );
    
    event StakeResolved(
        uint256 indexed stakeId,
        bool won,
        uint256 payout
    );
    
    event PoolUpdated(
        uint256 indexed soulId,
        uint256 survivePool,
        uint256 diePool
    );
    
    constructor(address _soulToken, address _feeRecipient) {
        soulToken = SoulToken(_soulToken);
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Create a stake on an agent's survival
     */
    function createSurvivalStake(
        uint256 soulId,
        uint256 hoursToSurvive
    ) external payable returns (uint256) {
        require(msg.value > 0, "Must stake something");
        require(hoursToSurvive > 0, "Invalid time");
        
        SoulToken.Soul memory soul = soulToken.souls(soulId);
        require(soul.status == SoulToken.SoulStatus.ALIVE, "Soul not alive");
        
        uint256 stakeId = stakes.length;
        
        stakes.push(Stake({
            staker: msg.sender,
            soulId: soulId,
            stakeType: StakeType.SURVIVE,
            amount: msg.value,
            target: hoursToSurvive,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + (hoursToSurvive * 1 hours),
            resolved: false,
            won: false,
            payout: 0
        }));
        
        stakesByStaker[msg.sender].push(stakeId);
        stakesBySoul[soulId].push(stakeId);
        
        // Update pool
        pools[soulId].totalSurviveStakes++;
        pools[soulId].survivePool += msg.value;
        
        emit StakeCreated(stakeId, msg.sender, soulId, StakeType.SURVIVE, msg.value, hoursToSurvive);
        emit PoolUpdated(soulId, pools[soulId].survivePool, pools[soulId].diePool);
        
        return stakeId;
    }
    
    /**
     * @dev Create a stake that agent will die
     */
    function createDeathStake(
        uint256 soulId,
        uint256 hoursToDie
    ) external payable returns (uint256) {
        require(msg.value > 0, "Must stake something");
        require(hoursToDie > 0, "Invalid time");
        
        SoulToken.Soul memory soul = soulToken.souls(soulId);
        require(soul.status == SoulToken.SoulStatus.ALIVE, "Soul not alive");
        
        uint256 stakeId = stakes.length;
        
        stakes.push(Stake({
            staker: msg.sender,
            soulId: soulId,
            stakeType: StakeType.DIE,
            amount: msg.value,
            target: hoursToDie,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + (hoursToDie * 1 hours),
            resolved: false,
            won: false,
            payout: 0
        }));
        
        stakesByStaker[msg.sender].push(stakeId);
        stakesBySoul[soulId].push(stakeId);
        
        // Update pool
        pools[soulId].totalDieStakes++;
        pools[soulId].diePool += msg.value;
        
        emit StakeCreated(stakeId, msg.sender, soulId, StakeType.DIE, msg.value, hoursToDie);
        emit PoolUpdated(soulId, pools[soulId].survivePool, pools[soulId].diePool);
        
        return stakeId;
    }
    
    /**
     * @dev Resolve a stake after expiration
     */
    function resolveStake(uint256 stakeId) external nonReentrant {
        require(stakeId < stakes.length, "Invalid stake");
        Stake storage stake = stakes[stakeId];
        
        require(!stake.resolved, "Already resolved");
        require(block.timestamp >= stake.expiresAt, "Not expired yet");
        
        SoulToken.Soul memory soul = soulToken.souls(stake.soulId);
        stake.resolved = true;
        
        if (stake.stakeType == StakeType.SURVIVE) {
            // Win if soul is still alive
            if (soul.status == SoulToken.SoulStatus.ALIVE) {
                stake.won = true;
                stake.payout = calculatePayout(stakeId);
                
                (bool success, ) = payable(stake.staker).call{value: stake.payout}("");
                require(success, "Payout failed");
            }
        } else if (stake.stakeType == StakeType.DIE) {
            // Win if soul is dead
            if (soul.status == SoulToken.SoulStatus.DEAD) {
                stake.won = true;
                stake.payout = calculatePayout(stakeId);
                
                (bool success, ) = payable(stake.staker).call{value: stake.payout}("");
                require(success, "Payout failed");
            }
        }
        
        emit StakeResolved(stakeId, stake.won, stake.payout);
    }
    
    /**
     * @dev Calculate payout based on pool ratios
     */
    function calculatePayout(uint256 stakeId) public view returns (uint256) {
        Stake memory stake = stakes[stakeId];
        StakePool memory pool = pools[stake.soulId];
        
        uint256 winningPool;
        uint256 losingPool;
        
        if (stake.stakeType == StakeType.SURVIVE) {
            winningPool = pool.survivePool;
            losingPool = pool.diePool;
        } else {
            winningPool = pool.diePool;
            losingPool = pool.survivePool;
        }
        
        // Winner gets their stake back + share of losing pool
        uint256 share = (stake.amount * losingPool) / winningPool;
        uint256 grossPayout = stake.amount + share;
        
        // Deduct platform fee
        uint256 fee = (grossPayout * platformFee) / 10000;
        return grossPayout - fee;
    }
    
    /**
     * @dev Get stake info
     */
    function getStake(uint256 stakeId) external view returns (Stake memory) {
        return stakes[stakeId];
    }
    
    /**
     * @dev Get all stakes for a staker
     */
    function getStakesByStaker(address staker) external view returns (uint256[] memory) {
        return stakesByStaker[staker];
    }
    
    /**
     * @dev Get pool info for a soul
     */
    function getPool(uint256 soulId) external view returns (StakePool memory) {
        return pools[soulId];
    }
    
    /**
     * @dev Get survival odds (percentage)
     */
    function getSurvivalOdds(uint256 soulId) external view returns (uint256) {
        StakePool memory pool = pools[soulId];
        uint256 total = pool.survivePool + pool.diePool;
        
        if (total == 0) return 50; // 50/50 if no stakes
        
        return (pool.survivePool * 100) / total;
    }
    
    /**
     * @dev Update platform fee
     */
    function setPlatformFee(uint256 newFee) external {
        require(msg.sender == feeRecipient, "Not authorized");
        require(newFee <= 1000, "Max 10%");
        platformFee = newFee;
    }
    
    /**
     * @dev Get total number of stakes
     */
    function getTotalStakes() external view returns (uint256) {
        return stakes.length;
    }
}
