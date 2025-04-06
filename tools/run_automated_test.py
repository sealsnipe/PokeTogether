#!/usr/bin/env python
"""
Run Automated Test - Runs the game and input server together for automated testing
"""

import os
import sys
import time
import argparse
import subprocess
import threading
import shutil

def run_game(game_path):
    """Run the game in a separate process

    Args:
        game_path: Path to the game executable or script

    Returns:
        subprocess.Popen: Process object for the game
    """
    print(f"Starting game: {game_path}")
    
    # Determine if it's a Python script or executable
    if game_path.endswith('.py'):
        process = subprocess.Popen([sys.executable, game_path])
    else:
        process = subprocess.Popen([game_path])
    
    return process

def run_input_server(server_script):
    """Run the input server in a separate process

    Args:
        server_script: Path to the input server script

    Returns:
        subprocess.Popen: Process object for the input server
    """
    print(f"Starting input server: {server_script}")
    
    process = subprocess.Popen([sys.executable, server_script])
    
    return process

def generate_test_instructions(generator_script, test_type, output_dir):
    """Generate test instructions using the generator script

    Args:
        generator_script: Path to the test generator script
        test_type: Type of test to generate
        output_dir: Directory to save the instructions

    Returns:
        str: Path to the generated instruction file, or None if generation failed
    """
    print(f"Generating {test_type} test instructions")
    
    # Build the command
    cmd = [sys.executable, generator_script, "--test", test_type, "--output", output_dir]
    
    # If it's a custom test, add the custom parameter
    if test_type == "custom" and ":" in test_type:
        test_type, custom_name = test_type.split(":", 1)
        cmd = [sys.executable, generator_script, "--test", "custom", "--custom", custom_name, "--output", output_dir]
    
    # Run the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error generating test instructions: {result.stderr}")
            return None
        
        # Extract the file path from the output
        for line in result.stdout.splitlines():
            if "Saved instructions to" in line:
                file_path = line.split("Saved instructions to")[-1].strip()
                return file_path
        
        return None
    except Exception as e:
        print(f"Error running test generator: {e}")
        return None

def analyze_logs(analyzer_script, log_file, output_file=None):
    """Analyze the game logs using the analyzer script

    Args:
        analyzer_script: Path to the log analyzer script
        log_file: Path to the log file to analyze
        output_file: Path to save the analysis report (optional)

    Returns:
        bool: True if analysis was successful, False otherwise
    """
    print(f"Analyzing logs: {log_file}")
    
    # Build the command
    cmd = [sys.executable, analyzer_script, "--log", log_file]
    
    if output_file:
        cmd.extend(["--output", output_file])
    
    # Run the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error analyzing logs: {result.stderr}")
            return False
        
        # If no output file was specified, print the analysis
        if not output_file:
            print("\n=== Log Analysis ===")
            print(result.stdout)
        
        return True
    except Exception as e:
        print(f"Error running log analyzer: {e}")
        return False

def wait_for_processes(processes, timeout=60):
    """Wait for processes to complete

    Args:
        processes: List of process objects
        timeout: Maximum time to wait in seconds

    Returns:
        bool: True if all processes completed, False if timeout occurred
    """
    print(f"Waiting for processes to complete (timeout: {timeout}s)")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check if all processes have completed
        if all(process.poll() is not None for process in processes):
            return True
        
        # Sleep to avoid high CPU usage
        time.sleep(0.5)
    
    # Timeout occurred
    return False

def cleanup_processes(processes):
    """Clean up processes by terminating them

    Args:
        processes: List of process objects
    """
    print("Cleaning up processes")
    
    for process in processes:
        if process.poll() is None:  # Process is still running
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")

def setup_test_environment(base_dir="./test_env"):
    """Set up the test environment

    Args:
        base_dir: Base directory for the test environment

    Returns:
        dict: Dictionary containing paths to the test environment
    """
    print(f"Setting up test environment in {base_dir}")
    
    # Create directories
    os.makedirs(base_dir, exist_ok=True)
    
    input_dir = os.path.join(base_dir, "input_instructions")
    log_dir = os.path.join(base_dir, "input_logs")
    report_dir = os.path.join(base_dir, "reports")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    # Copy the game log file if it exists
    game_log = "game.log"
    if os.path.exists(game_log):
        backup_log = os.path.join(log_dir, f"game_previous_{time.strftime('%Y%m%d_%H%M%S')}.log")
        shutil.copy2(game_log, backup_log)
    
    return {
        "base_dir": base_dir,
        "input_dir": input_dir,
        "log_dir": log_dir,
        "report_dir": report_dir
    }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run automated tests for the game")
    parser.add_argument("--game", default="src/main.py", help="Path to the game executable or script")
    parser.add_argument("--server", default="tools/input_server.py", help="Path to the input server script")
    parser.add_argument("--generator", default="tools/generate_test_instructions.py", help="Path to the test generator script")
    parser.add_argument("--analyzer", default="tools/analyze_game_logs.py", help="Path to the log analyzer script")
    parser.add_argument("--test", default="comprehensive", help="Type of test to run (movement, action, controller, menu, comprehensive, or custom:name)")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds for the test")
    parser.add_argument("--env", default="./test_env", help="Directory for the test environment")
    
    args = parser.parse_args()
    
    # Set up the test environment
    env = setup_test_environment(args.env)
    
    # Start the game
    game_process = run_game(args.game)
    
    # Give the game time to initialize
    print("Waiting for game to initialize...")
    time.sleep(5)
    
    # Start the input server
    server_process = run_input_server(args.server)
    
    # Give the server time to initialize
    print("Waiting for input server to initialize...")
    time.sleep(2)
    
    # Generate test instructions
    instruction_file = generate_test_instructions(args.generator, args.test, env["input_dir"])
    
    if not instruction_file:
        print("Failed to generate test instructions")
        cleanup_processes([game_process, server_process])
        return 1
    
    # Wait for the test to complete
    print(f"Test is running. Waiting for completion (timeout: {args.timeout}s)...")
    
    # Wait for the timeout
    time.sleep(args.timeout)
    
    # Clean up processes
    cleanup_processes([game_process, server_process])
    
    # Wait for log files to be flushed
    print("Waiting for log files to be flushed...")
    time.sleep(2)
    
    # Analyze the logs
    game_log = "game.log"
    if os.path.exists(game_log):
        report_file = os.path.join(env["report_dir"], f"analysis_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        analyze_logs(args.analyzer, game_log, report_file)
        
        print(f"Analysis report saved to {report_file}")
    else:
        print("Game log file not found")
    
    print("Test completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
