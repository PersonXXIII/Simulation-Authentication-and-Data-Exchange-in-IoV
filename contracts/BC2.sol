// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BC2 {
    struct AuthLog {
        string temp_vehicle_ID;
        uint256 timestamp;
        string date;
        string proof;
        string outcome;
        string VIN;             // Only set if the outcome is "Succeed"
        string hashed_VIN;      // Only set if the outcome is "Succeed"
        string sessionKey;      // Only set if the outcome is "Succeed"
        string node;            // New field for node identifier
    }

    mapping(string => AuthLog) public authLogs;  // Mapping from temporary vehicle ID to authentication log
    string[] public tempVehicleIDs;               // Array to store vehicle IDs for iteration
    uint256 public authLogCount = 0;

    // Event to log the addition of authentication data (for off-chain tracking)
    event AuthLogAdded(string temp_vehicle_ID, string proof, string outcome, string node);

    // Add authentication log to BC2
    function addAuthLog(
        string memory temp_vehicle_ID,
        string memory proof,
        string memory outcome,
        string memory VIN,        // Only included if outcome is "Succeed"
        string memory hashed_VIN, // Only included if outcome is "Succeed"
        string memory sessionKey, // Only included if outcome is "Succeed"
        string memory date,
        string memory node        // Node identifier
    ) public {
        authLogCount++;

        // Determine the values for success or failure
        string memory actualVIN = keccak256(bytes(outcome)) == keccak256(bytes("Succeed")) ? VIN : "";
        string memory actualHashedVIN = keccak256(bytes(outcome)) == keccak256(bytes("Succeed")) ? hashed_VIN : "";
        string memory actualSessionKey = keccak256(bytes(outcome)) == keccak256(bytes("Succeed")) ? sessionKey : "";

        // Save the authentication log
        authLogs[temp_vehicle_ID] = AuthLog({
            temp_vehicle_ID: temp_vehicle_ID,
            timestamp: block.timestamp,
            date: date,
            proof: proof,
            outcome: outcome,
            VIN: actualVIN,
            hashed_VIN: actualHashedVIN,
            sessionKey: actualSessionKey,
            node: node
        });

        // Store the temporary vehicle ID for future iteration
        tempVehicleIDs.push(temp_vehicle_ID);

        // Emit event for the new log addition
        emit AuthLogAdded(temp_vehicle_ID, proof, outcome, node);
    }
}
