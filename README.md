# Simulation-Authentication-and-Data-Exchange-in-IoV

This repository hosts a blockchain-integrated digital twin simulation for smart traffic management, combining Python, Azure Digital Twin, Ganache, and SUMO. The simulation is performed for a research paper. The purpose of the research is to propose a novel approach for authenticating vehicles and secure data exchange between them in an IoV environment.

---

## 🧠 Project Overview

- Simulates vehicle & pedestrian traffic with blockchain event logging.  
- Uses SUMO for traffic simulation, Truffle & Ganache for smart contracts.  
- Supports GUI and CLI modes.  
- Supports Dockerized and native environment setups.

---

## 🛠 Tools & Versions Used

| Tool           | Version           |
|----------------|-------------------|
| Python         | 3.12             |
| Truffle        | 5.11.5            |
| Ganache CLI    | 7.9.2             |
| SUMO           | 1.24.0            |
| Docker         | 28.3.2            |

---

## 📥 Installation & Setup

### Clone Repo

```bash
git clone https://github.com/PersonXXIII/Simulation-Authentication-and-Data-Exchange-in-IoV.git
cd your-repo-name
```
### a. Using Docker

Install the docker on your OS (window or linux). then build the docker.

```Bash
docker build -t sumo-simulation .
```
Then for running the built docker,

```Bash
docker run --rm -it sumo-simulation
```
The docker will start and start compiling Blockchain contracts and then setting up the simulation. After that the simulation will start and the data will be collected in /app/Results (inside the docker). The result files can be pulled using the commands:
- Look for your Container name:
```Bash
docker ps -a
```
<img width="1031" height="63" alt="image" src="https://github.com/user-attachments/assets/23d4fe9e-3c55-4d07-82be-3d436d3bfc3f" />

- Start the container:
```Bash
docker start boring_bhaskara
```
Here 'boring_bhaskara' is my created container name.
- Pull the 'Collected_Data' Folder:
```Bash
docker cp boring_bhaskara:/app/Results/Collected_Data ./Collected_Data
```
### b. Without Docker
- Install [Ganache](https://archive.trufflesuite.com/ganache/) and [Truffle](https://archive.trufflesuite.com/docs/truffle/how-to/install/) using [node.js](https://nodejs.org/en).
- Also install [Sumo](https://sumo.dlr.de/docs/index.html) for simulation.
- Now clone the repository and open any IDE (for python) in the root directory.
- Create a python environment,
```Bash
python -m venv .env
```
- Install required libraries,
```Bash
pip3 install -r requirements.txt
```
- Now start the ganache in a separate terminal,
```Bash
ganache
```
- Run main.py
```Bash
python main.py
```
### CLI Based Simulation
The main.py is set to run on CLI and collect Data in the 'Results' folder. It will not show any animation or Visuals

### GUI Based Simulation
i. In IDE:
  - If you wanna run Visuals then change the line 364 in 'main.py'
  ```Python
  traci.start(["sumo", "-c", SUMO_CONFIG ])
  ```
  to >>
  line 364 in 'main.py'
  ```Python
  traci.start(["sumo-gui", "-c", SUMO_CONFIG ])
  ```
  - and then run the 'main.py'.

ii. In Docker
  - As for Docker, first change the main.py line 364 and rebuild the dockerfile using same command.
  ```Bash
  docker build -t sumo-simulation .
  ```
  - Then install any 'server x' on the OS. '[VcXsrv](https://vcxsrv.com/)' is recommanded.
  - Launch VcXsrv.
  - Select:
     - *Multiple windows*
     - *Start no client*
     - *Disable access control* (or allow access from your container IP)
  - Leave the VcXsrv running.
  - Now go to CMD and run:
    ```CMD
      set DISPLAY=host.docker.internal:0.0
    ```
    Then (in same CMD session):
    ```CMD
      docker run -it --rm -e DISPLAY=%DISPLAY% sumo-simulation
    ```
    *Here sumo-simulation is the name of the docker which was built in the start.



