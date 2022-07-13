#! /bin/bash

cd client

# Install client dependencies
echo "Installing client dependencies..."
npm install  --production

# Start client
echo "Starting client..."
npm start