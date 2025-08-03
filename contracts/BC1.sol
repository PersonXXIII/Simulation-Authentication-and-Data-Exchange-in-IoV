// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract BC1 {
    struct Vehicle {
        string brand;
        string model;
        uint16 year;
        string vin;
        string hashedVIN;
        string encryptedVIN;
        string publicKey;
        string privateKey; // Added private key
        string taSignature;
    }

    mapping(string => Vehicle) private vehicles; // Mapping proof to vehicle data (proof is now a string)

    // Event to emit when a vehicle is added
    event VehicleAdded(string proof);

    function addVehicle(
        string memory _brand,
        string memory _model,
        uint16 _year,
        string memory _vin,
        string memory _hashedVIN,
        string memory _encryptedVIN,
        string memory _publicKey,
        string memory _privateKey, // Private key added as input parameter
        string memory _taSignature,
        string memory _proof 
    ) public {
        require(bytes(vehicles[_proof].vin).length == 0, "Vehicle already exists with this proof.");

        vehicles[_proof] = Vehicle({
            brand: _brand,
            model: _model,
            year: _year,
            vin: _vin,
            hashedVIN: _hashedVIN,
            encryptedVIN: _encryptedVIN,
            publicKey: _publicKey,
            privateKey: _privateKey, // Store private key
            taSignature: _taSignature
        });

        emit VehicleAdded(_proof);
    }

    function getVehicle(string memory _proof) public view returns (
        string memory brand,
        string memory model,
        uint16 year,
        string memory vin,
        string memory hashedVIN,
        string memory encryptedVIN,
        string memory publicKey,
        string memory privateKey, // Added private key to return
        string memory taSignature
    ) {
        Vehicle memory vehicle = vehicles[_proof];
        require(bytes(vehicle.vin).length != 0, "Vehicle does not exist with this proof.");

        return (
            vehicle.brand,
            vehicle.model,
            vehicle.year,
            vehicle.vin,
            vehicle.hashedVIN,
            vehicle.encryptedVIN,
            vehicle.publicKey,
            vehicle.privateKey, // Return private key
            vehicle.taSignature
        );
    }
}
