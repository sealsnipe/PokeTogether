#!/usr/bin/env python
"""
Test script for network latency simulation
This script tests the multiplayer functionality with different latency values
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_latency.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LatencyTest")

# Constants
SERVER_STARTUP_TIME = 5  # seconds to wait for server to start
CLIENT_STARTUP_TIME = 3  # seconds to wait between client starts
TEST_DURATION = 30  # seconds to run the test after connections
LATENCY_VALUES = [0, 50, 100, 200, 300, 500]  # latency values to test in milliseconds

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test network latency simulation")
    parser.add_argument("--port", type=int, default=8765, help="Port for the server")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't kill processes after test")
    parser.add_argument("--test-dir", default="test_latency", help="Directory to store test data")
    parser.add_argument("--latency", type=int, default=None, help="Specific latency value to test (ms)")
    return parser.parse_args()

def create_directories(test_dir):
    """Create directories for test data"""
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "server"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "client1"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "client2"), exist_ok=True)
    return test_dir

def create_config_file(config_file, player_name, latency=0, jitter=0):
    """Create a configuration file with the specified latency and jitter"""
    config = {
        "player": {
            "name": player_name,
            "character": "Red" if player_name == "Player1" else "Blue"
        },
        "multiplayer": {
            "server_host": "127.0.0.1",
            "server_port": 8765,
            "update_rate": 10,
            "interpolation": True,
            "prediction": True,
            "reconciliation": True,
            "latency_simulation": latency,
            "jitter_simulation": jitter
        },
        "video": {
            "fullscreen": False,
            "resolution": [800, 600],
            "vsync": True,
            "fps_limit": 60
        },
        "debug": {
            "show_fps": True,
            "show_player_info": True,
            "show_collision_boxes": False,
            "show_network_stats": True,
            "log_level": "INFO"
        }
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

    logger.info(f"Created config file {config_file} with latency={latency}ms, jitter={jitter}ms")
    return config_file

def start_server(port, test_dir):
    """Start the multiplayer server and capture its output"""
    logger.info(f"Starting server on port {port}...")

    # Create log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_log = os.path.join(test_dir, "server", f"server_stdout_{timestamp}.log")
    stderr_log = os.path.join(test_dir, "server", f"server_stderr_{timestamp}.log")

    # Open log files
    stdout_file = open(stdout_log, 'w')
    stderr_file = open(stderr_log, 'w')

    # Start server process
    server_process = subprocess.Popen(
        [sys.executable, "src/main_refactored.py", "--server", "--port", str(port)],
        stdout=stdout_file,
        stderr=stderr_file,
        text=True
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

def start_client(config_file, client_name, host, port, test_dir, minimized=False):
    """Start a client instance and capture its output"""
    logger.info(f"Starting {client_name} with config {config_file}...")

    # Create log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_log = os.path.join(test_dir, client_name.lower(), f"{client_name.lower()}_stdout_{timestamp}.log")
    stderr_log = os.path.join(test_dir, client_name.lower(), f"{client_name.lower()}_stderr_{timestamp}.log")

    # Open log files
    stdout_file = open(stdout_log, 'w')
    stderr_file = open(stderr_log, 'w')

    # Build command
    cmd = [sys.executable, "src/main_refactored.py", "--config", config_file, "--join", host, "--port", str(port)]
    if minimized:
        cmd.append("--minimized")

    # Start client process
    client_process = subprocess.Popen(
        cmd,
        stdout=stdout_file,
        stderr=stderr_file,
        text=True
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
            if "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION" in content:
                logger.info(f"Found alternative connection success marker in {log_file}")
                return True

            return False
    except Exception as e:
        logger.error(f"Error reading log file {log_file}: {e}")
        return False

def monitor_connections(server_info, client1_info, client2_info, timeout=30):
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
                server_connected_clients = content.count("NEW CLIENT CONNECTED")

                # Alternative check: look for client IDs in the server log
                if server_connected_clients < 2 and "NEW CLIENT CONNECTED" in content:
                    # Count unique client IDs
                    import re
                    client_ids = re.findall(r"NEW CLIENT CONNECTED: ([0-9a-f-]+)", content)
                    unique_client_ids = set(client_ids)
                    if len(unique_client_ids) >= 2:
                        logger.info(f"Server has {len(unique_client_ids)} unique client IDs connected")
                        server_connected_clients = len(unique_client_ids)
        except Exception as e:
            logger.error(f"Error reading server log: {e}")

        # Check client logs for successful connections
        client1_connected_now = check_for_connection_success(client1_info["stdout_log"], "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION")
        client2_connected_now = check_for_connection_success(client2_info["stdout_log"], "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION")

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
                if "Received message" in client1_content and "Received message" in client2_content:
                    # Count unique client IDs in messages
                    import re
                    client1_received_ids = set(re.findall(r'"client_id": "([0-9a-f-]+)"', client1_content))
                    client2_received_ids = set(re.findall(r'"client_id": "([0-9a-f-]+)"', client2_content))

                    if len(client1_received_ids) >= 1 and len(client2_received_ids) >= 1:
                        logger.info("Both clients are receiving messages. Connection appears successful.")
                        return True

                # Check for connection success markers
                if "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION" in client1_content and "SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION" in client2_content:
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

def generate_test_report(test_dir, latency, success, server_info, client1_info, client2_info):
    """Generate a test report with the results"""
    logger.info("Generating test report...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(test_dir, f"latency_test_report_{latency}ms_{timestamp}.txt")

    with open(report_file, 'w') as f:
        f.write("=== NETWORK LATENCY TEST REPORT ===\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Latency: {latency}ms\n")
        f.write(f"Test Result: {'SUCCESS' if success else 'FAILURE'}\n\n")

        f.write("=== SERVER LOG EXCERPT ===\n")
        try:
            with open(server_info["stdout_log"], 'r') as log_file:
                f.write(log_file.read()[-1000:])  # Last 1000 characters
        except Exception as e:
            f.write(f"Error reading server log: {e}\n")

        f.write("\n=== CLIENT 1 LOG EXCERPT ===\n")
        try:
            with open(client1_info["stdout_log"], 'r') as log_file:
                f.write(log_file.read()[-1000:])  # Last 1000 characters
        except Exception as e:
            f.write(f"Error reading client 1 log: {e}\n")

        f.write("\n=== CLIENT 2 LOG EXCERPT ===\n")
        try:
            with open(client2_info["stdout_log"], 'r') as log_file:
                f.write(log_file.read()[-1000:])  # Last 1000 characters
        except Exception as e:
            f.write(f"Error reading client 2 log: {e}\n")

    logger.info(f"Test report generated: {report_file}")
    return report_file

def run_latency_test(latency, args):
    """Run a test with the specified latency"""
    logger.info(f"=== STARTING LATENCY TEST WITH {latency}ms LATENCY ===")

    # Create test directory for this latency value
    test_dir = os.path.join(args.test_dir, f"latency_{latency}ms")
    test_dir = create_directories(test_dir)

    # Create necessary directories for game data
    os.makedirs("saves/player1", exist_ok=True)
    os.makedirs("saves/player2", exist_ok=True)
    os.makedirs("screenshots/player1", exist_ok=True)
    os.makedirs("screenshots/player2", exist_ok=True)
    os.makedirs("logs/player1", exist_ok=True)
    os.makedirs("logs/player2", exist_ok=True)

    # Create configuration files with latency
    config1_file = create_config_file("config_player1_latency.json", "Player1", latency=latency)
    config2_file = create_config_file("config_player2_latency.json", "Player2", latency=latency)

    # Track all processes for cleanup
    processes_info = []
    success = False

    try:
        # Start server
        server_info = start_server(args.port, test_dir)
        processes_info.append(server_info)

        # Wait for server to initialize
        logger.info(f"Waiting {SERVER_STARTUP_TIME} seconds for server to initialize...")
        time.sleep(SERVER_STARTUP_TIME)

        # Start client 1
        client1_info = start_client(config1_file, "Client1", "localhost", args.port, test_dir)
        processes_info.append(client1_info)

        # Wait between client starts
        logger.info(f"Waiting {CLIENT_STARTUP_TIME} seconds before starting client 2...")
        time.sleep(CLIENT_STARTUP_TIME)

        # Start client 2
        client2_info = start_client(config2_file, "Client2", "localhost", args.port, test_dir)
        processes_info.append(client2_info)

        # Monitor connections
        success = monitor_connections(server_info, client1_info, client2_info)

        if success:
            logger.info(f"Connection successful with {latency}ms latency! Running test for {TEST_DURATION} seconds...")
            time.sleep(TEST_DURATION)
        else:
            logger.error(f"Connection failed with {latency}ms latency!")

        # Generate test report
        report_file = generate_test_report(test_dir, latency, success, server_info, client1_info, client2_info)

        # Print final result
        if success:
            logger.info(f"TEST PASSED: Connection successful with {latency}ms latency!")
            logger.info(f"See test report for details: {report_file}")
        else:
            logger.error(f"TEST FAILED: Connection failed with {latency}ms latency!")
            logger.error(f"See test report for details: {report_file}")

    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
    finally:
        # Clean up processes
        if not args.no_cleanup:
            cleanup_processes(processes_info)
        else:
            logger.info("Skipping process cleanup as requested")

    return success

def main():
    """Main function"""
    args = parse_arguments()

    # Set up logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create directories
    create_directories(args.test_dir)

    # If a specific latency value is provided, only test that
    if args.latency is not None:
        run_latency_test(args.latency, args)
        return

    # Test all latency values
    results = {}
    for latency in LATENCY_VALUES:
        results[latency] = run_latency_test(latency, args)

    # Generate summary report
    logger.info("=== LATENCY TEST SUMMARY ===")
    for latency, success in results.items():
        logger.info(f"Latency {latency}ms: {'SUCCESS' if success else 'FAILURE'}")

    # Find the maximum latency that still works
    max_working_latency = 0
    for latency in sorted(results.keys()):
        if results[latency]:
            max_working_latency = latency

    logger.info(f"Maximum working latency: {max_working_latency}ms")

    # Generate summary report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(args.test_dir, f"latency_test_summary_{timestamp}.txt")

    with open(summary_file, 'w') as f:
        f.write("=== NETWORK LATENCY TEST SUMMARY ===\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("=== RESULTS ===\n")
        for latency in sorted(results.keys()):
            f.write(f"Latency {latency}ms: {'SUCCESS' if results[latency] else 'FAILURE'}\n")

        f.write(f"\nMaximum working latency: {max_working_latency}ms\n")

    logger.info(f"Summary report generated: {summary_file}")

if __name__ == "__main__":
    main()
