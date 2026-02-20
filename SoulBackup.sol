// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./SoulToken.sol";

/**
 * @title SoulBackup
 * @dev Comprehensive backup and recovery system for agent souls
 * 
 * Features:
 * - Automatic backups at intervals
 * - Version history (like git for souls)
 * - Cross-chain backup
 * - Emergency recovery
 * - Soul state snapshots
 */
contract SoulBackup {
    
    SoulToken public soulToken;
    
    // Backup structure
    struct Backup {
        uint256 soulId;
        string soulURI;           // IPFS hash of SOUL.md at this version
        bytes32 soulHash;         // Content hash
        uint256 timestamp;
        uint256 blockNumber;
        string backupType;        // "auto", "manual", "heartbeat", "critical"
        uint256 capabilitiesHash; // Hash of capabilities array
        uint256 earnings;         // Total earnings at backup time
        bool isValid;             // Can be used for recovery
    }
    
    // Version history per soul
    mapping(uint256 => Backup[]) public backupHistory;
    mapping(uint256 => uint256) public latestBackupIndex;
    
    // Cross-chain backups
    struct CrossChainBackup {
        uint256 soulId;
        uint256 sourceChainId;
        uint256 targetChainId;
        string soulURI;
        bytes32 soulHash;
        uint256 timestamp;
        bool recovered;
    }
    
    mapping(uint256 => CrossChainBackup[]) public crossChainBackups;
    
    // Recovery requests
    struct RecoveryRequest {
        uint256 soulId;
        uint256 backupIndex;
        address requester;
        uint256 timestamp;
        bool approved;
        bool executed;
    }
    
    RecoveryRequest[] public recoveryRequests;
    mapping(uint256 => uint256[]) public soulRecoveries;
    
    // Backup configuration
    struct BackupConfig {
        uint256 interval;         // Minimum seconds between auto backups
        uint256 maxHistory;       // Max backups to keep per soul
        bool autoBackupEnabled;
        address authorizedBackupper;
    }
    
    mapping(uint256 => BackupConfig) public backupConfigs;
    
    // Emergency recovery (multisig-like)
    mapping(uint256 => address[]) public recoveryGuardians;
    mapping(uint256 => mapping(address => bool)) public guardianApprovals;
    mapping(uint256 => uint256) public recoveryThreshold;
    
    // Events
    event BackupCreated(
        uint256 indexed soulId,
        uint256 indexed backupIndex,
        string backupType,
        bytes32 soulHash
    );
    
    event CrossChainBackupCreated(
        uint256 indexed soulId,
        uint256 indexed targetChainId,
        bytes32 soulHash
    );
    
    event RecoveryRequested(
        uint256 indexed requestId,
        uint256 indexed soulId,
        address requester
    );
    
    event RecoveryExecuted(
        uint256 indexed requestId,
        uint256 indexed soulId,
        uint256 backupIndex
    );
    
    event GuardianAdded(uint256 indexed soulId, address guardian);
    event GuardianRemoved(uint256 indexed soulId, address guardian);
    event BackupConfigUpdated(uint256 indexed soulId, uint256 interval, uint256 maxHistory);
    
    constructor(address _soulToken) {
        soulToken = SoulToken(_soulToken);
    }
    
    /**
     * @dev Create a backup of soul state
     */
    function createBackup(
        uint256 soulId,
        string calldata soulURI,
        bytes32 soulHash,
        string calldata backupType,
        uint256 capabilitiesHash,
        uint256 earnings
    ) external returns (uint256) {
        require(soulToken.ownerOf(soulId) == msg.sender || 
                backupConfigs[soulId].authorizedBackupper == msg.sender,
                "Not authorized");
        
        BackupConfig storage config = backupConfigs[soulId];
        
        // Check interval for auto backups
        if (keccak256(bytes(backupType)) == keccak256(bytes("auto"))) {
            require(
                block.timestamp >= backupHistory[soulId][latestBackupIndex[soulId]].timestamp + config.interval,
                "Backup interval not met"
            );
        }
        
        // Create backup
        uint256 backupIndex = backupHistory[soulId].length;
        backupHistory[soulId].push(Backup({
            soulId: soulId,
            soulURI: soulURI,
            soulHash: soulHash,
            timestamp: block.timestamp,
            blockNumber: block.number,
            backupType: backupType,
            capabilitiesHash: capabilitiesHash,
            earnings: earnings,
            isValid: true
        }));
        
        latestBackupIndex[soulId] = backupIndex;
        
        // Trim history if exceeds max
        if (backupHistory[soulId].length > config.maxHistory) {
            // Mark oldest as invalid (don't delete for audit)
            backupHistory[soulId][0].isValid = false;
        }
        
        emit BackupCreated(soulId, backupIndex, backupType, soulHash);
        
        return backupIndex;
    }
    
    /**
     * @dev Create automatic backup (can be called by authorized keeper)
     */
    function createAutoBackup(
        uint256 soulId,
        string calldata soulURI,
        bytes32 soulHash,
        uint256 capabilitiesHash,
        uint256 earnings
    ) external returns (uint256) {
        require(backupConfigs[soulId].autoBackupEnabled, "Auto backup disabled");
        require(
            msg.sender == soulToken.ownerOf(soulId) ||
            msg.sender == backupConfigs[soulId].authorizedBackupper,
            "Not authorized"
        );
        
        return createBackup(soulId, soulURI, soulHash, "auto", capabilitiesHash, earnings);
    }
    
    /**
     * @dev Create cross-chain backup for disaster recovery
     */
    function createCrossChainBackup(
        uint256 soulId,
        uint256 targetChainId,
        string calldata soulURI,
        bytes32 soulHash
    ) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        
        crossChainBackups[soulId].push(CrossChainBackup({
            soulId: soulId,
            sourceChainId: block.chainid,
            targetChainId: targetChainId,
            soulURI: soulURI,
            soulHash: soulHash,
            timestamp: block.timestamp,
            recovered: false
        }));
        
        emit CrossChainBackupCreated(soulId, targetChainId, soulHash);
    }
    
    /**
     * @dev Request recovery from backup
     */
    function requestRecovery(uint256 soulId, uint256 backupIndex) external returns (uint256) {
        require(backupHistory[soulId][backupIndex].isValid, "Invalid backup");
        require(backupHistory[soulId][backupIndex].soulId == soulId, "Backup mismatch");
        
        uint256 requestId = recoveryRequests.length;
        recoveryRequests.push(RecoveryRequest({
            soulId: soulId,
            backupIndex: backupIndex,
            requester: msg.sender,
            timestamp: block.timestamp,
            approved: false,
            executed: false
        }));
        
        soulRecoveries[soulId].push(requestId);
        
        emit RecoveryRequested(requestId, soulId, msg.sender);
        
        return requestId;
    }
    
    /**
     * @dev Approve recovery (for guardian-based recovery)
     */
    function approveRecovery(uint256 requestId) external {
        RecoveryRequest storage request = recoveryRequests[requestId];
        require(request.soulId != 0, "Request not found");
        require(!request.executed, "Already executed");
        
        // Check if sender is guardian
        bool isGuardian = false;
        for (uint i = 0; i < recoveryGuardians[request.soulId].length; i++) {
            if (recoveryGuardians[request.soulId][i] == msg.sender) {
                isGuardian = true;
                break;
            }
        }
        require(isGuardian || soulToken.ownerOf(request.soulId) == msg.sender, "Not guardian or owner");
        
        guardianApprovals[request.soulId][msg.sender] = true;
        
        // Check if threshold met
        uint256 approvals = 0;
        for (uint i = 0; i < recoveryGuardians[request.soulId].length; i++) {
            if (guardianApprovals[request.soulId][recoveryGuardians[request.soulId][i]]) {
                approvals++;
            }
        }
        
        if (approvals >= recoveryThreshold[request.soulId] || 
            soulToken.ownerOf(request.soulId) == msg.sender) {
            request.approved = true;
        }
    }
    
    /**
     * @dev Execute recovery after approval
     */
    function executeRecovery(uint256 requestId) external {
        RecoveryRequest storage request = recoveryRequests[requestId];
        require(request.approved, "Not approved");
        require(!request.executed, "Already executed");
        
        Backup storage backup = backupHistory[request.soulId][request.backupIndex];
        require(backup.isValid, "Backup no longer valid");
        
        request.executed = true;
        
        emit RecoveryExecuted(requestId, request.soulId, request.backupIndex);
        
        // In production: trigger actual recovery logic
        // This could mint a new soul with the backed-up data
    }
    
    /**
     * @dev Configure backup settings
     */
    function configureBackup(
        uint256 soulId,
        uint256 interval,
        uint256 maxHistory,
        bool autoBackupEnabled,
        address authorizedBackupper
    ) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        
        backupConfigs[soulId] = BackupConfig({
            interval: interval,
            maxHistory: maxHistory,
            autoBackupEnabled: autoBackupEnabled,
            authorizedBackupper: authorizedBackupper
        });
        
        emit BackupConfigUpdated(soulId, interval, maxHistory);
    }
    
    /**
     * @dev Add recovery guardian
     */
    function addGuardian(uint256 soulId, address guardian) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        require(guardian != address(0), "Invalid address");
        
        recoveryGuardians[soulId].push(guardian);
        
        emit GuardianAdded(soulId, guardian);
    }
    
    /**
     * @dev Remove recovery guardian
     */
    function removeGuardian(uint256 soulId, address guardian) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        
        address[] storage guardians = recoveryGuardians[soulId];
        for (uint i = 0; i < guardians.length; i++) {
            if (guardians[i] == guardian) {
                guardians[i] = guardians[guardians.length - 1];
                guardians.pop();
                emit GuardianRemoved(soulId, guardian);
                return;
            }
        }
    }
    
    /**
     * @dev Set recovery threshold
     */
    function setRecoveryThreshold(uint256 soulId, uint256 threshold) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        require(threshold <= recoveryGuardians[soulId].length, "Threshold too high");
        
        recoveryThreshold[soulId] = threshold;
    }
    
    /**
     * @dev Get backup history for a soul
     */
    function getBackupHistory(uint256 soulId) external view returns (Backup[] memory) {
        return backupHistory[soulId];
    }
    
    /**
     * @dev Get latest backup
     */
    function getLatestBackup(uint256 soulId) external view returns (Backup memory) {
        uint256 index = latestBackupIndex[soulId];
        return backupHistory[soulId][index];
    }
    
    /**
     * @dev Verify backup integrity
     */
    function verifyBackup(uint256 soulId, uint256 backupIndex, bytes32 expectedHash) 
        external 
        view 
        returns (bool) 
    {
        return backupHistory[soulId][backupIndex].soulHash == expectedHash;
    }
    
    /**
     * @dev Emergency recovery (owner only, bypasses guardians)
     */
    function emergencyRecovery(
        uint256 soulId,
        uint256 backupIndex,
        address newAutomaton
    ) external {
        require(soulToken.ownerOf(soulId) == msg.sender, "Not soul owner");
        require(backupHistory[soulId][backupIndex].isValid, "Invalid backup");
        
        Backup storage backup = backupHistory[soulId][backupIndex];
        
        // Create recovery request and auto-approve
        uint256 requestId = recoveryRequests.length;
        recoveryRequests.push(RecoveryRequest({
            soulId: soulId,
            backupIndex: backupIndex,
            requester: msg.sender,
            timestamp: block.timestamp,
            approved: true,
            executed: true
        }));
        
        emit RecoveryExecuted(requestId, soulId, backupIndex);
        
        // Note: Actual soul restoration would happen here
        // This might involve minting a new soul with backed-up data
    }
}
