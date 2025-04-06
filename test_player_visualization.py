#!/usr/bin/env python
"""
Test script for player visualization in multiplayer mode
This script tests if players can see each other in the game
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import pygame
import cv2
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_visualization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VisualizationTest")

# Constants
SERVER_STARTUP_TIME = 5  # seconds to wait for server to start
CLIENT_STARTUP_TIME = 3  # seconds to wait between client starts
TEST_DURATION = 20  # seconds to run the test after connections
SCREENSHOT_INTERVAL = 2  # seconds between screenshots
MOVEMENT_INTERVAL = 3  # seconds between movement commands

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test player visualization in multiplayer")
    parser.add_argument("--port", type=int, default=8765, help="Port for the server")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't kill processes after test")
    parser.add_argument("--test-dir", default="test_visualization", help="Directory to store test data")
    return parser.parse_args()

def create_directories(test_dir):
    """Create directories for test data"""
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "server"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "client1"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "client2"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "screenshots"), exist_ok=True)
    return test_dir

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

def take_screenshot(window_title, output_path):
    """Take a screenshot of a window with the given title"""
    try:
        # Find the window
        import win32gui
        import win32ui
        import win32con
        import win32api
        
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd == 0:
            logger.error(f"Window with title '{window_title}' not found")
            return None
        
        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        # Create a device context
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        # Create a bitmap
        saveBitmap = win32ui.CreateBitmap()
        saveBitmap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitmap)
        
        # Copy the screen into the bitmap
        result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        
        # Convert the bitmap to a numpy array
        bmpinfo = saveBitmap.GetInfo()
        bmpstr = saveBitmap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
        img = img[:, :, :3]  # Remove alpha channel
        img = np.ascontiguousarray(img)  # Make contiguous
        
        # Save the image
        cv2.imwrite(output_path, img)
        
        # Clean up
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        win32gui.DeleteObject(saveBitmap.GetHandle())
        
        logger.info(f"Screenshot saved to {output_path}")
        return img
    
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def send_key_to_window(window_title, key_code):
    """Send a key press to a window with the given title"""
    try:
        import win32gui
        import win32api
        import win32con
        
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd == 0:
            logger.error(f"Window with title '{window_title}' not found")
            return False
        
        # Bring window to foreground
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)  # Give time for window to come to foreground
        
        # Send key down
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
        time.sleep(0.1)  # Hold key for a moment
        
        # Send key up
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)
        
        logger.info(f"Sent key {key_code} to window '{window_title}'")
        return True
    
    except Exception as e:
        logger.error(f"Error sending key to window: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def move_player(window_title, direction):
    """Move a player in the given direction"""
    # Key codes
    VK_UP = 0x26    # Arrow up
    VK_DOWN = 0x28  # Arrow down
    VK_LEFT = 0x25  # Arrow left
    VK_RIGHT = 0x27 # Arrow right
    
    key_map = {
        "up": VK_UP,
        "down": VK_DOWN,
        "left": VK_LEFT,
        "right": VK_RIGHT
    }
    
    if direction not in key_map:
        logger.error(f"Invalid direction: {direction}")
        return False
    
    return send_key_to_window(window_title, key_map[direction])

def analyze_screenshots(screenshot1, screenshot2):
    """Analyze screenshots to detect player movement"""
    try:
        # Load images
        img1 = cv2.imread(screenshot1)
        img2 = cv2.imread(screenshot2)
        
        if img1 is None or img2 is None:
            logger.error(f"Failed to load screenshots: {screenshot1} or {screenshot2}")
            return False
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Threshold the difference
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size
        significant_contours = [c for c in contours if cv2.contourArea(c) > 100]
        
        # Draw contours on a copy of the second image
        img_contours = img2.copy()
        cv2.drawContours(img_contours, significant_contours, -1, (0, 255, 0), 2)
        
        # Save the contour image
        contour_path = screenshot2.replace(".png", "_contours.png")
        cv2.imwrite(contour_path, img_contours)
        
        # Check if there are significant changes
        if len(significant_contours) > 0:
            logger.info(f"Detected {len(significant_contours)} significant changes between screenshots")
            return True
        else:
            logger.warning("No significant changes detected between screenshots")
            return False
    
    except Exception as e:
        logger.error(f"Error analyzing screenshots: {e}")
        import traceback
        logger.error(traceback.format_exc())
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

def generate_test_report(test_dir, screenshots, movement_detected):
    """Generate a test report with the results"""
    logger.info("Generating test report...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(test_dir, f"visualization_test_report_{timestamp}.txt")
    
    with open(report_file, 'w') as f:
        f.write("=== PLAYER VISUALIZATION TEST REPORT ===\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Result: {'SUCCESS' if movement_detected else 'FAILURE'}\n\n")
        
        f.write("=== SCREENSHOTS ===\n")
        for i, screenshot in enumerate(screenshots):
            f.write(f"Screenshot {i+1}: {screenshot}\n")
        
        f.write("\n=== MOVEMENT DETECTION ===\n")
        if movement_detected:
            f.write("Player movement was successfully detected in the screenshots.\n")
            f.write("This indicates that players can see each other in the game.\n")
        else:
            f.write("No player movement was detected in the screenshots.\n")
            f.write("This indicates that players cannot see each other in the game.\n")
    
    logger.info(f"Test report generated: {report_file}")
    return report_file

def main():
    """Main function"""
    args = parse_arguments()
    
    # Set up logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create directories
    test_dir = create_directories(args.test_dir)
    
    # Create necessary directories for game data
    os.makedirs("saves/player1", exist_ok=True)
    os.makedirs("saves/player2", exist_ok=True)
    os.makedirs("screenshots/player1", exist_ok=True)
    os.makedirs("screenshots/player2", exist_ok=True)
    os.makedirs("logs/player1", exist_ok=True)
    os.makedirs("logs/player2", exist_ok=True)
    
    # Track all processes for cleanup
    processes_info = []
    screenshots = []
    movement_detected = False
    
    try:
        # Start server
        server_info = start_server(args.port, test_dir)
        processes_info.append(server_info)
        
        # Wait for server to initialize
        logger.info(f"Waiting {SERVER_STARTUP_TIME} seconds for server to initialize...")
        time.sleep(SERVER_STARTUP_TIME)
        
        # Start client 1
        client1_info = start_client("config_player1.json", "Client1", "localhost", args.port, test_dir)
        processes_info.append(client1_info)
        
        # Wait between client starts
        logger.info(f"Waiting {CLIENT_STARTUP_TIME} seconds before starting client 2...")
        time.sleep(CLIENT_STARTUP_TIME)
        
        # Start client 2
        client2_info = start_client("config_player2.json", "Client2", "localhost", args.port, test_dir)
        processes_info.append(client2_info)
        
        # Wait for clients to connect and initialize
        logger.info("Waiting for clients to connect and initialize...")
        time.sleep(5)
        
        # Take initial screenshots
        logger.info("Taking initial screenshots...")
        client1_title = "PokeTogether - Player 1"
        client2_title = "PokeTogether - Player 2"
        
        screenshot1_path = os.path.join(test_dir, "screenshots", f"client1_initial.png")
        screenshot2_path = os.path.join(test_dir, "screenshots", f"client2_initial.png")
        
        take_screenshot(client1_title, screenshot1_path)
        take_screenshot(client2_title, screenshot2_path)
        
        screenshots.append(screenshot1_path)
        screenshots.append(screenshot2_path)
        
        # Move player 1 in different directions
        logger.info("Moving Player 1 in different directions...")
        directions = ["right", "right", "down", "down", "left", "up"]
        
        for i, direction in enumerate(directions):
            # Move player 1
            logger.info(f"Moving Player 1 {direction}...")
            move_player(client1_title, direction)
            
            # Wait for movement to be processed
            time.sleep(MOVEMENT_INTERVAL)
            
            # Take screenshots
            screenshot1_path = os.path.join(test_dir, "screenshots", f"client1_after_move_{i+1}.png")
            screenshot2_path = os.path.join(test_dir, "screenshots", f"client2_after_move_{i+1}.png")
            
            take_screenshot(client1_title, screenshot1_path)
            take_screenshot(client2_title, screenshot2_path)
            
            screenshots.append(screenshot1_path)
            screenshots.append(screenshot2_path)
            
            # Analyze screenshots to detect player movement in client 2's view
            if i > 0:
                prev_screenshot = os.path.join(test_dir, "screenshots", f"client2_after_move_{i}.png")
                movement_detected = analyze_screenshots(prev_screenshot, screenshot2_path)
                
                if movement_detected:
                    logger.info("Player movement detected in Client 2's view!")
                    break
        
        # Generate test report
        report_file = generate_test_report(test_dir, screenshots, movement_detected)
        
        # Print final result
        if movement_detected:
            logger.info("TEST PASSED: Player movement was detected in the other client's view!")
            logger.info(f"See test report for details: {report_file}")
            exit_code = 0
        else:
            logger.error("TEST FAILED: No player movement was detected in the other client's view!")
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
