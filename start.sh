#!/bin/bash

# Start SSH service in the background
echo "Starting SSH service..."
/usr/sbin/sshd -D &

# Start the Python chat server in the foreground
# This is important because the container will keep running as long as this process is active.
echo "Starting chat server..."
python3 chat_server.py

# Note: If python3 chat_server.py exits, the container will stop.
# If you wanted SSH to also run in the foreground, you'd need a more complex setup
# like 'supervisord' or running SSH in the background and then a foreground process.
# For simplicity, we'll keep the chat server in the foreground.
