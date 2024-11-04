#!/bin/bash

# Update and install necessary dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required Python packages
pip install poetry

# Clone the repository if not already cloned
if [ ! -d "01" ]; then
  git clone https://github.com/OpenInterpreter/01.git
fi

cd 01/software

# Install project dependencies
poetry install

# Set up environment variables for the voice feature
echo "export OPENAI_API_KEY='your_openai_api_key'" >> ~/.bashrc
source ~/.bashrc

# Start the server with the voice feature enabled
poetry run 01 --server light --expose --qr
