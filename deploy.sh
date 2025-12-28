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
    echo "Usage: ./deploy.sh [--frontend-only | --backend-only]"
    exit 0
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
    # Prepare permissions
    ssh $HOST "sudo chown -R $REMOTE_USER:$REMOTE_USER $REMOTE_WWW"
    # Sync files
    rsync -avz --delete $FRONTEND_DIR/dist/ $HOST:$REMOTE_WWW/
    # Restore web server permissions
    ssh $HOST "sudo chown -R www-data:www-data $REMOTE_WWW"
fi

# Backend Deployment
if [ "$1" != "--frontend-only" ]; then
    echo "========================================"
    echo "Deploying Backend..."
    echo "========================================"
    # Sync backend code
    # Excluding __pycache__ and other unnecessary files
    rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.env' $BACKEND_DIR/ $HOST:$REMOTE_APP/backend/
    
    echo "========================================"
    echo "Restarting Service..."
    echo "========================================"
    ssh $HOST "sudo systemctl restart nostalgia"
fi

echo "========================================"
echo "Deployment Complete!"
echo "========================================"
