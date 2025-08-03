FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies, Node.js, npm, curl, git, and tools
RUN apt-get update && apt-get install -y \
    build-essential cmake g++ libxerces-c-dev libfox-1.6-dev libgl1-mesa-dev libglu1-mesa-dev libgdal-dev \
    nodejs npm curl git python3-pip python3-setuptools python3-numpy \
    && npm install -g ganache \
    && npm install -g truffle \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Build and install latest SUMO from GitHub
RUN git clone https://github.com/eclipse/sumo.git /tmp/sumo && \
    cd /tmp/sumo && \
    mkdir -p build/cmake && cd build/cmake && \
    cmake ../.. && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    rm -rf /tmp/sumo

WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make run.sh executable
RUN chmod +x run.sh

ENTRYPOINT ["bash", "run.sh"]
