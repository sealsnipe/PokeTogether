#!/usr/bin/env python
"""
Start Local Multiplayer Script
This script starts a server and two client instances for local multiplayer testing.
"""

import os
import sys
import subprocess
import time
import argparse

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Start local multiplayer testing")
    parser.add_argument("--server-only", action="store_true", help="Start only the server")
    parser.add_argument("--client1-only", action="store_true", help="Start only client 1")
    parser.add_argument("--client2-only", action="store_true", help="Start only client 2")
    parser.add_argument("--port", type=int, default=8765, help="Port for the server")
    parser.add_argument("--minimized", action="store_true", help="Start clients minimized")
    return parser.parse_args()

def start_server(port):
    """Start the multiplayer server"""
    print(f"Starting server on port {port}...")
    server_process = subprocess.Popen(
        [sys.executable, "src/main_refactored.py", "--server", "--port", str(port)],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    return server_process

def start_client(config_file, host=None, port=None, minimized=False):
    """Start a client instance"""
    print(f"Starting client with config {config_file}...")
    
    cmd = [sys.executable, "src/main_refactored.py", "--config", config_file]
    
    if minimized:
        cmd.append("--minimized")
    
    if host:
        cmd.extend(["--join", host])
    
    if port:
        cmd.extend(["--port", str(port)])
    
    client_process = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    return client_process

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create necessary directories
    os.makedirs("saves/player1", exist_ok=True)
    os.makedirs("saves/player2", exist_ok=True)
    os.makedirs("screenshots/player1", exist_ok=True)
    os.makedirs("screenshots/player2", exist_ok=True)
    os.makedirs("logs/player1", exist_ok=True)
    os.makedirs("logs/player2", exist_ok=True)
    
    processes = []
    
    try:
        # Start server if needed
        if not args.client1_only and not args.client2_only:
            server_process = start_server(args.port)
            processes.append(server_process)
            print("Server started. Waiting for it to initialize...")
            time.sleep(2)  # Give the server time to start
        
        # Start client 1 if needed
        if not args.server_only and not args.client2_only:
            client1_process = start_client(
                "config_player1.json", 
                "localhost" if not args.client1_only else None,
                args.port if not args.client1_only else None,
                args.minimized
            )
            processes.append(client1_process)
            print("Client 1 started.")
            time.sleep(1)  # Give client 1 time to start
        
        # Start client 2 if needed
        if not args.server_only and not args.client1_only:
            client2_process = start_client(
                "config_player2.json", 
                "localhost", 
                args.port,
                args.minimized
            )
            processes.append(client2_process)
            print("Client 2 started.")
        
        print("\nLocal multiplayer environment is running!")
        print("Press Ctrl+C to stop all processes and exit.")
        
        # Wait for all processes to complete (or until interrupted)
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nStopping all processes...")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        print("All processes stopped.")

if __name__ == "__main__":
    main()
