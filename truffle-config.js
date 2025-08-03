module.exports = {
  compilers: {
    solc: {
      version: "0.8.21", // Match your contract version
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        viaIR: true // Enable Intermediate Representation (IR) pipeline
      }
    }
  }
};
