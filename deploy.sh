#!/bin/bash
set -e

HOST="nostalgia"
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"
REMOTE_WWW="/var/www/nostalgia"
REMOTE_APP="~/nostalgia"

# User on remote machine for chown (assuming same as local user or defined)
REMOTE_USER="dariofreni"

echo "Deploying Nostalgia to $HOST..."

if [ "$1" == "--help" ]; then
    echo "Usage: ./deploy.sh [--setup] [--frontend-only | --backend-only]"
    exit 0
fi

# Initial Setup
if [ "$1" == "--setup" ]; then
    echo "========================================"
    echo "Running Remote Setup..."
    echo "========================================"
    scp scripts/setup_remote.sh $HOST:/tmp/setup_remote.sh
    ssh $HOST "bash /tmp/setup_remote.sh"
    echo "Setup finished. Proceeding with deployment..."
fi

# Frontend Deployment
if [ "$1" != "--backend-only" ]; then
    echo "========================================"
    echo "Building Frontend..."
    echo "========================================"
    cd $FRONTEND_DIR
    npm run build
    cd ..

    echo "========================================"
    echo "Deploying Frontend..."
    echo "========================================"
    # Sync files
    rsync -avz --delete $FRONTEND_DIR/dist/ $HOST:$REMOTE_WWW/
    
    # Copy Nginx Config
    echo "Updating Nginx Config..."
    scp $BACKEND_DIR/nostalgia.nginx $HOST:/tmp/nostalgia.nginx
    ssh $HOST "sudo mv /tmp/nostalgia.nginx /etc/nginx/sites-available/nostalgia && \
               sudo ln -sf /etc/nginx/sites-available/nostalgia /etc/nginx/sites-enabled/ && \
               sudo nginx -t && \
               sudo systemctl reload nginx"
fi

# Backend Deployment
if [ "$1" != "--frontend-only" ]; then
    echo "========================================"
    echo "Deploying Backend..."
    echo "========================================"
    # Sync backend code
    rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.env' --exclude '.pytest_cache' --exclude 'tests' $BACKEND_DIR/ $HOST:$REMOTE_APP/backend/
    
    # Install Requirements
    echo "Installing Python Requirements..."
    ssh $HOST "$REMOTE_APP/backend/venv/bin/pip install -r $REMOTE_APP/backend/requirements.txt"

    # Setup Service
    echo "Updating Systemd Service..."
    scp $BACKEND_DIR/nostalgia.service $HOST:/tmp/nostalgia.service
    ssh $HOST "sudo mv /tmp/nostalgia.service /etc/systemd/system/nostalgia.service && \
               sudo systemctl daemon-reload && \
               sudo systemctl enable nostalgia"
    
    echo "========================================"
    echo "Restarting Service..."
    echo "========================================"
    ssh $HOST "sudo systemctl restart nostalgia"
fi

echo "========================================"
echo "Deployment Complete!"
echo "========================================"
