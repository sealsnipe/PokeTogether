# Local Multiplayer Testing Guide

This guide explains how to test the multiplayer functionality of PokeTogether locally on a single machine.

## Overview

The local multiplayer testing setup allows you to:

1. Run a server and two client instances on the same machine
2. Test player synchronization and multiplayer features
3. Verify that each client has its own configuration and save files
4. Ensure network updates are properly throttled for performance

## Setup

The following components have been implemented to support local multiplayer testing:

1. **Configuration System**: Each client instance uses its own configuration file
2. **Instance-specific Directories**: Each client has its own directories for saves, screenshots, and logs
3. **Network Update Throttling**: Updates are sent at a configurable rate to reduce network traffic
4. **Launcher Script**: A script to easily start the server and client instances

## How to Use

### Starting the Full Environment

To start the server and both client instances:

```bash
python start_local_multiplayer.py
```

This will:
- Start a server on port 8765
- Start Client 1 (Player1) and connect it to the server
- Start Client 2 (Player2) and connect it to the server

### Starting Components Individually

You can also start components individually:

```bash
# Start only the server
python start_local_multiplayer.py --server-only

# Start only Client 1
python start_local_multiplayer.py --client1-only

# Start only Client 2
python start_local_multiplayer.py --client2-only
```

### Additional Options

```bash
# Use a different port
python start_local_multiplayer.py --port 9000

# Start clients minimized
python start_local_multiplayer.py --minimized
```

## Testing Workflow

1. Start the full environment using the launcher script
2. In Client 1, start hosting a game (if not already connected)
3. In Client 2, join the game (if not already connected)
4. Move the player in one client and verify the movement is visible in the other client
5. Test other multiplayer features as needed

## Configuration Files

Two configuration files are provided:

- `config_player1.json`: Configuration for Player 1
- `config_player2.json`: Configuration for Player 2

You can modify these files to change player names, characters, or other settings.

## Directory Structure

The following directories are created for each client instance:

```
saves/
  player1/     # Save files for Player 1
  player2/     # Save files for Player 2
screenshots/
  player1/     # Screenshots for Player 1
  player2/     # Screenshots for Player 2
logs/
  player1/     # Log files for Player 1
  player2/     # Log files for Player 2
```

## Troubleshooting

### Connection Issues

If clients cannot connect to the server:

1. Make sure the server is running
2. Check that the correct port is being used
3. Verify that no firewall is blocking the connection
4. Try restarting the server and clients

### Performance Issues

If you experience lag or performance issues:

1. Reduce the update rate in the configuration files
2. Lower the FPS limit in the settings
3. Close other applications to free up system resources

### Client Crashes

If a client crashes:

1. Check the log files in the `logs/playerX` directory
2. Restart the client using the launcher script with the appropriate option
3. If the issue persists, try restarting the entire environment
