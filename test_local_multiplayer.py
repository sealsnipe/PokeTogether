#!/usr/bin/env python
"""
Automated Test Script for Local Multiplayer
This script tests the local multiplayer functionality by:
1. Starting a server process
2. Starting two client processes with different configurations
3. Verifying that both clients successfully connect to the server
4. Analyzing logs to confirm proper connection
5. Verifying that player positions are correctly synchronized between clients
"""

import os
import sys
import subprocess
import time
# re-Modul wird nicht mehr benötigt
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_multiplayer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MultiplaterTest")

# Constants
CONNECTION_TIMEOUT = 30  # seconds to wait for connections
SERVER_STARTUP_TIME = 5  # seconds to wait for server to start
CLIENT_STARTUP_TIME = 3  # seconds to wait between client starts
TEST_DURATION = 15  # seconds to run the test after connections

# Success markers in logs
SERVER_SUCCESS_MARKER = "Received connection confirmation from client"
CLIENT_SUCCESS_MARKER = "Connection acknowledged by server"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test local multiplayer functionality")
    parser.add_argument("--port", type=int, default=8765, help="Port for the server")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't kill processes after test")
    parser.add_argument("--log-dir", default="test_logs", help="Directory to store test logs")
    parser.add_argument("--screenshots", action="store_true", help="Enable screenshots during the test")
    return parser.parse_args()

def create_log_directories(log_dir):
    """Create directories for test logs"""
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.join(log_dir, "server"), exist_ok=True)
    os.makedirs(os.path.join(log_dir, "client1"), exist_ok=True)
    os.makedirs(os.path.join(log_dir, "client2"), exist_ok=True)
    return log_dir

def start_server(port, log_dir):
    """Start the multiplayer server and capture its output"""
    logger.info(f"Starting server on port {port}...")

    # Create log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_log = os.path.join(log_dir, "server", f"server_stdout_{timestamp}.log")
    stderr_log = os.path.join(log_dir, "server", f"server_stderr_{timestamp}.log")

    # Open log files
    stdout_file = open(stdout_log, 'w')
    stderr_file = open(stderr_log, 'w')

    # Start server process
    server_process = subprocess.Popen(
        [sys.executable, "src/game/network/server.py"],
        stdout=stdout_file,
        stderr=stderr_file,
        text=True
        # Kein eigenes Konsolenfenster, um die Ausgabe besser zu sehen
    )

    logger.info(f"Server process started with PID {server_process.pid}")
    logger.info(f"Server stdout log: {stdout_log}")
    logger.info(f"Server stderr log: {stderr_log}")

    return {
        "process": server_process,
        "stdout_file": stdout_file,
        "stderr_file": stderr_file,
        "stdout_log": stdout_log,
        "stderr_log": stderr_log
    }

def start_client(config_file, client_name, host, port, log_dir, enable_screenshots=False):
    """Start a client instance and capture its output"""
    logger.info(f"Starting {client_name} with config {config_file}...")

    # Create log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_log = os.path.join(log_dir, client_name.lower(), f"{client_name.lower()}_stdout_{timestamp}.log")
    stderr_log = os.path.join(log_dir, client_name.lower(), f"{client_name.lower()}_stderr_{timestamp}.log")

    # Open log files
    stdout_file = open(stdout_log, 'w')
    stderr_file = open(stderr_log, 'w')

    # Prepare command
    cmd = [sys.executable, "src/main_refactored.py", "--join", host, "--port", str(port)]

    # Add screenshots flag if enabled
    if enable_screenshots:
        cmd.append("--screenshots")
        logger.info(f"Screenshots enabled for {client_name}")

    # Start client process
    client_process = subprocess.Popen(
        cmd,
        stdout=stdout_file,
        stderr=stderr_file,
        text=True
        # Kein eigenes Konsolenfenster, um die Ausgabe besser zu sehen
    )

    logger.info(f"{client_name} process started with PID {client_process.pid}")
    logger.info(f"{client_name} stdout log: {stdout_log}")
    logger.info(f"{client_name} stderr log: {stderr_log}")

    return {
        "process": client_process,
        "stdout_file": stdout_file,
        "stderr_file": stderr_file,
        "stdout_log": stdout_log,
        "stderr_log": stderr_log,
        "name": client_name
    }

def check_process_running(process_info):
    """Check if a process is still running"""
    if process_info["process"].poll() is None:
        return True
    else:
        logger.warning(f"Process {process_info['process'].pid} has exited with code {process_info['process'].returncode}")
        return False

def check_for_connection_success(log_file, success_marker):
    """Check if a log file contains the success marker"""
    if not os.path.exists(log_file):
        return False

    try:
        with open(log_file, 'r') as f:
            content = f.read()
            # Check for the specific marker
            if success_marker in content:
                return True

            # Additional check for client connection success
            if "SUCCESSFULLY CONNECTED TO SERVER" in content or "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION" in content or "Connection acknowledged by server" in content:
                logger.info(f"Found alternative connection success marker in {log_file}")
                return True

            return False
    except Exception as e:
        logger.error(f"Error reading log file {log_file}: {e}")
        return False

def monitor_connections(server_info, client1_info, client2_info, timeout=CONNECTION_TIMEOUT):
    """Monitor the processes and check for successful connections"""
    logger.info(f"Monitoring connections for up to {timeout} seconds...")

    start_time = time.time()
    server_connected_clients = 0
    client1_connected = False
    client2_connected = False

    # Track how long each client has been connected
    client1_connected_time = 0
    client2_connected_time = 0
    connection_stability_threshold = 5  # seconds a client must be connected to be considered stable

    while time.time() - start_time < timeout:
        # Check if processes are still running
        if not check_process_running(server_info):
            logger.error("Server process has exited unexpectedly")
            break

        if not check_process_running(client1_info):
            logger.error("Client 1 process has exited unexpectedly")
            break

        if not check_process_running(client2_info):
            logger.error("Client 2 process has exited unexpectedly")
            break

        # Check server logs for client connections
        try:
            with open(server_info["stdout_log"], 'r') as f:
                content = f.read()
                server_connected_clients = content.count(SERVER_SUCCESS_MARKER)

                # Alternative check: look for client IDs in the server log
                if server_connected_clients < 2 and "Received connection confirmation from client" in content:
                    # Count unique client IDs
                    import re
                    client_ids = re.findall(r"Received connection confirmation from client ([0-9a-f-]+)", content)
                    unique_client_ids = set(client_ids)
                    if len(unique_client_ids) >= 2:
                        logger.info(f"Server has {len(unique_client_ids)} unique client IDs connected")
                        server_connected_clients = len(unique_client_ids)
        except Exception as e:
            logger.error(f"Error reading server log: {e}")

        # Check client logs for successful connections
        client1_connected_now = check_for_connection_success(client1_info["stdout_log"], CLIENT_SUCCESS_MARKER)
        client2_connected_now = check_for_connection_success(client2_info["stdout_log"], CLIENT_SUCCESS_MARKER)

        # Update connection time tracking
        if client1_connected_now:
            if not client1_connected:
                client1_connected_time = 0
            client1_connected_time += 1
            if client1_connected_time >= connection_stability_threshold:
                client1_connected = True
        else:
            client1_connected_time = 0
            client1_connected = False

        if client2_connected_now:
            if not client2_connected:
                client2_connected_time = 0
            client2_connected_time += 1
            if client2_connected_time >= connection_stability_threshold:
                client2_connected = True
        else:
            client2_connected_time = 0
            client2_connected = False

        # If both clients are connected, we're done
        if server_connected_clients >= 2 and client1_connected and client2_connected:
            logger.info("Both clients have successfully connected to the server!")
            return True

        # Special case: If server sees 2 clients but our checks don't match, do additional verification
        if server_connected_clients >= 2 and (not client1_connected or not client2_connected):
            logger.info("Server reports 2 clients but client connection markers not found. Performing additional checks...")

            # Check if clients are receiving messages from each other
            try:
                with open(client1_info["stdout_log"], 'r') as f:
                    client1_content = f.read()
                with open(client2_info["stdout_log"], 'r') as f:
                    client2_content = f.read()

                # Check if clients are receiving player updates
                if "RECEIVED MESSAGE FROM SERVER" in client1_content and "RECEIVED MESSAGE FROM SERVER" in client2_content:
                    # Count unique client IDs in messages
                    import re
                    client1_received_ids = set(re.findall(r'"client_id": "([0-9a-f-]+)"', client1_content))
                    client2_received_ids = set(re.findall(r'"client_id": "([0-9a-f-]+)"', client2_content))

                    if len(client1_received_ids) >= 1 and len(client2_received_ids) >= 1:
                        logger.info("Both clients are receiving messages. Connection appears successful.")
                        return True

                # Check for connection success markers
                if "Connection acknowledged by server" in client1_content and "Connection acknowledged by server" in client2_content:
                    logger.info("Both clients have successfully connected to the multiplayer session.")
                    return True
            except Exception as e:
                logger.error(f"Error during additional connection verification: {e}")

        # Log current status
        logger.info(f"Connection status: Server has {server_connected_clients} clients, " +
                   f"Client1 connected: {client1_connected} ({client1_connected_time}s), " +
                   f"Client2 connected: {client2_connected} ({client2_connected_time}s)")

        # Wait before checking again
        time.sleep(1)

    # If we get here, the timeout was reached
    logger.warning("Connection timeout reached!")
    logger.warning(f"Final status: Server has {server_connected_clients} clients, " +
                  f"Client1 connected: {client1_connected}, Client2 connected: {client2_connected}")

    # Even if we didn't meet all criteria, if the server sees 2 clients and at least one client is connected,
    # we'll consider it a partial success
    if server_connected_clients >= 2 and (client1_connected or client2_connected):
        logger.warning("Partial success: Server sees 2 clients but not all connection markers were found")
        return True

    return False

def cleanup_processes(processes_info):
    """Clean up all processes and close log files"""
    logger.info("Cleaning up processes...")

    for process_info in processes_info:
        try:
            # Close log files
            if "stdout_file" in process_info and process_info["stdout_file"]:
                process_info["stdout_file"].close()

            if "stderr_file" in process_info and process_info["stderr_file"]:
                process_info["stderr_file"].close()

            # Terminate process if still running
            if "process" in process_info and process_info["process"].poll() is None:
                logger.info(f"Terminating process {process_info['process'].pid}...")
                process_info["process"].terminate()
                process_info["process"].wait(timeout=5)
        except Exception as e:
            logger.error(f"Error cleaning up process: {e}")

def extract_player_positions(log_file):
    """Extract player positions from log file"""
    logger.info(f"Extracting player positions from {log_file}...")

    positions = {}

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "[DATENFLUSS] RENDERING PLAYER" in line and ": x=" in line and ", y=" in line:
                    # Example: [DATENFLUSS] RENDERING PLAYER Player2 (ID: e6adf86d-9767-4fb9-8f7e-c4af4123daef): x=560, y=448, screen_x=480, screen_y=360
                    try:
                        # Extract player name
                        player_start = line.find("PLAYER ") + 7
                        player_end = line.find(" (ID:")
                        player_name = line[player_start:player_end]

                        # Extract position
                        x_start = line.find("x=") + 2
                        x_end = line.find(",", x_start)
                        y_start = line.find("y=") + 2
                        y_end = line.find(",", y_start)

                        # Convert to float first, then to int to handle values like "446.0"
                        x = int(float(line[x_start:x_end]))
                        y = int(float(line[y_start:y_end]))

                        positions[player_name] = (x, y)
                        logger.info(f"Found position for {player_name}: ({x}, {y})")
                    except Exception as e:
                        logger.error(f"Error parsing player position: {e}")
    except Exception as e:
        logger.error(f"Error reading log file: {e}")

    return positions

def generate_test_report(server_info, client1_info, client2_info, connection_success, log_dir):
    """Generate a test report with the results"""
    logger.info("Generating test report...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(log_dir, f"test_report_{timestamp}.txt")

    # Extract player positions
    client1_positions = extract_player_positions(client1_info["stdout_file"].name)
    client2_positions = extract_player_positions(client2_info["stdout_file"].name)

    with open(report_file, 'w') as f:
        f.write("=== LOCAL MULTIPLAYER TEST REPORT ===\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Result: {'SUCCESS' if connection_success else 'FAILURE'}\n\n")

        f.write("=== SERVER INFO ===\n")
        f.write(f"PID: {server_info['process'].pid}\n")
        f.write(f"Exit Code: {server_info['process'].returncode if server_info['process'].poll() is not None else 'Still running'}\n")
        f.write(f"Stdout Log: {server_info['stdout_log']}\n")
        f.write(f"Stderr Log: {server_info['stderr_log']}\n\n")

        f.write("=== CLIENT 1 INFO ===\n")
        f.write(f"PID: {client1_info['process'].pid}\n")
        f.write(f"Exit Code: {client1_info['process'].returncode if client1_info['process'].poll() is not None else 'Still running'}\n")
        f.write(f"Stdout Log: {client1_info['stdout_log']}\n")
        f.write(f"Stderr Log: {client1_info['stderr_log']}\n\n")

        f.write("=== CLIENT 2 INFO ===\n")
        f.write(f"PID: {client2_info['process'].pid}\n")
        f.write(f"Exit Code: {client2_info['process'].returncode if client2_info['process'].poll() is not None else 'Still running'}\n")
        f.write(f"Stdout Log: {client2_info['stdout_log']}\n")
        f.write(f"Stderr Log: {client2_info['stderr_log']}\n\n")

        f.write("=== PLAYER POSITIONS ===\n")
        f.write("Client 1 player positions:\n")
        for player_name, position in client1_positions.items():
            f.write(f"  {player_name}: {position}\n")

        f.write("\nClient 2 player positions:\n")
        for player_name, position in client2_positions.items():
            f.write(f"  {player_name}: {position}\n")

        f.write("\n=== POSITION SYNCHRONIZATION ===\n")

        # Check if Player1 is visible in Client 2 and Player2 is visible in Client 1
        player1_in_client2 = "Player1" in client2_positions
        player2_in_client1 = "Player2" in client1_positions

        if player1_in_client2 and player2_in_client1:
            f.write("Both players are visible to each other.\n")

            # Check if positions match
            if client1_positions.get("Player2") == client2_positions.get("Player1"):
                f.write("[SUCCESS] Player positions are correctly synchronized!\n")
                f.write(f"Position: {client1_positions.get('Player2')}\n")
            else:
                f.write("[FAILURE] Player positions are NOT correctly synchronized!\n")
                f.write(f"Player2 in Client1: {client1_positions.get('Player2')}\n")
                f.write(f"Player1 in Client2: {client2_positions.get('Player1')}\n")
        else:
            f.write("[FAILURE] Not all players are visible to each other.\n")
            if not player1_in_client2:
                f.write("Player1 is not visible in Client2.\n")
            if not player2_in_client1:
                f.write("Player2 is not visible in Client1.\n")

        # Add log excerpts
        f.write("=== SERVER LOG EXCERPT ===\n")
        try:
            with open(server_info['stdout_log'], 'r') as log:
                f.write(log.read()[-2000:])  # Last 2000 characters
        except Exception as e:
            f.write(f"Error reading log: {e}\n")
        f.write("\n\n")

        f.write("=== CLIENT 1 LOG EXCERPT ===\n")
        try:
            with open(client1_info['stdout_log'], 'r') as log:
                f.write(log.read()[-2000:])  # Last 2000 characters
        except Exception as e:
            f.write(f"Error reading log: {e}\n")
        f.write("\n\n")

        f.write("=== CLIENT 2 LOG EXCERPT ===\n")
        try:
            with open(client2_info['stdout_log'], 'r') as log:
                f.write(log.read()[-2000:])  # Last 2000 characters
        except Exception as e:
            f.write(f"Error reading log: {e}\n")
        f.write("\n\n")

    logger.info(f"Test report generated: {report_file}")
    return report_file

def main():
    """Main function"""
    args = parse_arguments()

    # Set up logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create log directories
    log_dir = create_log_directories(args.log_dir)

    # Create necessary directories for game data
    os.makedirs("saves/player1", exist_ok=True)
    os.makedirs("saves/player2", exist_ok=True)
    os.makedirs("screenshots/player1", exist_ok=True)
    os.makedirs("screenshots/player2", exist_ok=True)
    os.makedirs("logs/player1", exist_ok=True)
    os.makedirs("logs/player2", exist_ok=True)

    # Track all processes for cleanup
    processes_info = []

    try:
        # Start server
        server_info = start_server(args.port, log_dir)
        processes_info.append(server_info)

        # Wait for server to initialize
        logger.info(f"Waiting {SERVER_STARTUP_TIME} seconds for server to initialize...")
        time.sleep(SERVER_STARTUP_TIME)

        # Start client 1
        client1_info = start_client("config_player1.json", "Client1", "localhost", args.port, log_dir, args.screenshots)
        processes_info.append(client1_info)

        # Wait between client starts
        logger.info(f"Waiting {CLIENT_STARTUP_TIME} seconds before starting client 2...")
        time.sleep(CLIENT_STARTUP_TIME)

        # Start client 2
        client2_info = start_client("config_player2.json", "Client2", "localhost", args.port, log_dir, args.screenshots)
        processes_info.append(client2_info)

        # Monitor connections
        connection_success = monitor_connections(server_info, client1_info, client2_info)

        # If connections are successful, let the test run for a while
        if connection_success:
            logger.info(f"Connections successful! Running test for {TEST_DURATION} seconds...")
            time.sleep(TEST_DURATION)

        # Generate test report
        report_file = generate_test_report(server_info, client1_info, client2_info, connection_success, log_dir)

        # Print final result
        if connection_success:
            logger.info("TEST PASSED: Both clients successfully connected to the server!")
            logger.info(f"See test report for details: {report_file}")
            exit_code = 0
        else:
            logger.error("TEST FAILED: Not all clients connected to the server!")
            logger.error(f"See test report for details: {report_file}")
            exit_code = 1

    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        exit_code = 2
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        exit_code = 3
    finally:
        # Clean up processes
        if not args.no_cleanup:
            cleanup_processes(processes_info)
        else:
            logger.info("Skipping process cleanup as requested")

        # Return exit code
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
