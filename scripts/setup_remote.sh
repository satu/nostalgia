#!/bin/bash
set -e

echo "========================================"
echo "Nostalgia: Remote Setup Script"
echo "========================================"

# Update and Install Dependencies
echo "[1/4] Installing System Dependencies..."
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv nginx ffmpeg libasound2-dev

# Setup User Permissions
echo "[2/4] Configuring Permissions..."
sudo usermod -aG audio $USER
# Ensure /var/www/nostalgia exists and is owned by user for deployment
sudo mkdir -p /var/www/nostalgia
sudo chown -R $USER:$USER /var/www/nostalgia
# Ensure backend dir exists
mkdir -p ~/nostalgia/backend

# Setup Virtualenv
echo "[3/4] Setting up Python Virtual Environment..."
if [ ! -d "$HOME/nostalgia/backend/venv" ]; then
    python3 -m venv ~/nostalgia/backend/venv
    echo "Virtualenv created."
else
    echo "Virtualenv already exists."
fi

# Upgrade pip inside venv
~/nostalgia/backend/venv/bin/pip install --upgrade pip

echo "[4/4] Setup Complete!"
echo "You may need to log out and back in for group changes (audio) to take effect."
