// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BC3 {
    enum CommunicationType { V2V, V2P, V2I }
    enum DeviceType { V, P, I }
    enum Direction { North, South, West, East }

    struct CommunicationSession {
        string nodeId;
        string commType; // Store as string now
        string sessionKey; // Encryption session key
        string encryptionAlgo;
        string processingLatency; // in milliseconds as string
        string date;
        string time;
        string primaryVTempId;
        string primaryVVin;
        string secondaryDeviceType;
        string secondaryDeviceTempId;
        string secondaryDeviceId; // VIN, MAC, or unique address
        string latitude;
        string longitude;
        string altitude;
        string speed;
        string direction;
        string alerts; // Combined alerts as a string
        string otherData; // Combined otherData as a string (weather, light status, etc.)
        string communicationMode;
    }

    CommunicationSession[] public sessions;

    // Mapping from VIN to an array of session indexes
    mapping(string => uint[]) public vinToSessions;

    function storeSession(
        string memory _nodeId,
        string memory _commType, // Now a string
        string memory _sessionKey,
        string memory _encryptionAlgo,
        string memory _processingLatency, // Store as string
        string memory _date,
        string memory _time,
        string memory _tempId,
        string memory _vin,
        string memory _rType, // Store as string
        string memory _rTempId,
        string memory _rId,
        string memory _latitude,
        string memory _longitude,
        string memory _altitude,
        string memory _speed,
        string memory _direction,
        string memory _alerts,
        string memory _otherData,
        string memory _communicationMode
    ) public {
        CommunicationSession memory newSession = CommunicationSession({
            nodeId: _nodeId,
            commType: _commType,
            sessionKey: _sessionKey,
            encryptionAlgo: _encryptionAlgo,
            processingLatency: _processingLatency,
            date: _date,
            time: _time,
            primaryVTempId: _tempId,
            primaryVVin: _vin,
            secondaryDeviceType: _rType,
            secondaryDeviceTempId: _rTempId,
            secondaryDeviceId: _rId,
            latitude: _latitude,
            longitude: _longitude,
            altitude: _altitude,
            speed: _speed,
            direction: _direction,
            alerts: _alerts,
            otherData: _otherData,
            communicationMode: _communicationMode
        });

        sessions.push(newSession);

        // Store the session index in the VIN-to-sessions mapping
        vinToSessions[_vin].push(sessions.length - 1);
    }

    // Retrieve all sessions for a given VIN
    function getSessionsByVIN(string memory _vin) public view returns (CommunicationSession[] memory) {
        uint[] memory sessionIndexes = vinToSessions[_vin];
        CommunicationSession[] memory result = new CommunicationSession[](sessionIndexes.length);
        
        for (uint i = 0; i < sessionIndexes.length; i++) {
            result[i] = sessions[sessionIndexes[i]];
        }
        
        return result;
    }

    // Helper function to get the total number of sessions stored
    function getTotalSessions() public view returns (uint) {
        return sessions.length;
    }
}
