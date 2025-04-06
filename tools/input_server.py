#!/usr/bin/env python
"""
Input Server - A server that listens for instruction files and injects inputs into the game
"""

import os
import sys
import time
import json
import logging
import logging.config
import threading
import pygame

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Watchdog library not found. Please install it with: pip install watchdog")
    sys.exit(1)

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importiere die Controller-Konstanten direkt

# Achsen
AXIS_LEFTX = 0
AXIS_LEFTY = 1
AXIS_RIGHTX = 2
AXIS_RIGHTY = 3
AXIS_TRIGGERLEFT = 4
AXIS_TRIGGERRIGHT = 5

# Buttons
BUTTON_A = 0
BUTTON_B = 1
BUTTON_X = 2
BUTTON_Y = 3
BUTTON_BACK = 6
BUTTON_START = 7
BUTTON_LEFTSTICK = 8
BUTTON_RIGHTSTICK = 9
BUTTON_LEFTSHOULDER = 4
BUTTON_RIGHTSHOULDER = 5
BUTTON_DPAD_UP = 10
BUTTON_DPAD_DOWN = 11
BUTTON_DPAD_LEFT = 12
BUTTON_DPAD_RIGHT = 13
BUTTON_GUIDE = 14  # Xbox Button / PS Button

# Schwellenwerte für Achsen
AXIS_DEADZONE = 0.2

class InputServer:
    """Server that listens for instruction files and injects inputs into the game"""

    def __init__(self, watch_dir="./input_instructions", log_dir="./input_logs"):
        """Initialize the input server

        Args:
            watch_dir: Directory to watch for instruction files
            log_dir: Directory to store log files
        """
        # Setup logging
        self.logger = self.setup_logging()
        self.logger.info("Initializing Input Server")

        # Create directories if they don't exist
        os.makedirs(watch_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        self.watch_dir = os.path.abspath(watch_dir)
        self.log_dir = os.path.abspath(log_dir)

        self.logger.info(f"Watching directory: {self.watch_dir}")
        self.logger.info(f"Log directory: {self.log_dir}")

        # Initialize pygame for event injection
        pygame.init()

        # Queue for input commands
        self.command_queue = []
        self.queue_lock = threading.Lock()

        # Flag to indicate if the server is running
        self.running = False

        # Create a file handler to watch for new instruction files
        self.event_handler = InputFileHandler(self)
        self.observer = Observer()

        # Current game state tracking
        self.player_position = (0, 0)
        self.game_state = "UNKNOWN"
        self.last_action_time = time.time()

        # Create a log file for this session
        self.session_log_file = os.path.join(self.log_dir, f"input_session_{time.strftime('%Y%m%d_%H%M%S')}.log")
        self.log_session_start()

    def setup_logging(self):
        """Setup logging for the input server"""
        if os.path.exists('logging.conf'):
            logging.config.fileConfig('logging.conf')
        else:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        return logging.getLogger(__name__)

    def start(self):
        """Start the input server"""
        self.logger.info("Starting Input Server")
        self.running = True

        # Start watching the directory for new instruction files
        self.observer.schedule(self.event_handler, self.watch_dir, recursive=False)
        self.observer.start()

        try:
            # Main server loop
            while self.running:
                # Process any commands in the queue
                self.process_command_queue()

                # Sleep to avoid high CPU usage
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info("Input Server stopped by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the input server"""
        self.logger.info("Stopping Input Server")
        self.running = False
        self.observer.stop()
        self.observer.join()
        pygame.quit()
        self.log_session_end()

    def process_instruction_file(self, file_path):
        """Process an instruction file

        Args:
            file_path: Path to the instruction file
        """
        self.logger.info(f"Processing instruction file: {file_path}")

        try:
            with open(file_path, 'r') as f:
                instructions = json.load(f)

            # Add instructions to the command queue
            with self.queue_lock:
                for instruction in instructions:
                    self.command_queue.append(instruction)

            self.logger.info(f"Added {len(instructions)} instructions to the queue")

            # Create a processed file to indicate that the file has been processed
            processed_file = file_path + ".processed"
            with open(processed_file, 'w') as f:
                f.write(f"Processed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Log the instructions
            self.log_instructions(instructions)

        except json.JSONDecodeError:
            self.logger.error(f"Error parsing instruction file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error processing instruction file: {e}")

    def process_command_queue(self):
        """Process commands in the queue"""
        if not self.command_queue:
            return

        try:
            with self.queue_lock:
                command = self.command_queue.pop(0)

            # Protokolliere das Kommando, bevor wir es verarbeiten
            try:
                self.logger.debug(f"Processing command: {json.dumps(command)}")
            except:
                self.logger.debug(f"Processing command (could not serialize): {command}")

            command_type = command.get("type", "")

            if command_type == "key_press":
                self.inject_key_press(command)
            elif command_type == "key_release":
                self.inject_key_release(command)
            elif command_type == "button_press":
                self.inject_button_press(command)
            elif command_type == "button_release":
                self.inject_button_release(command)
            elif command_type == "wait":
                self.handle_wait_command(command)
            elif command_type == "sequence":
                self.handle_sequence_command(command)
            else:
                self.logger.warning(f"Unknown command type: {command_type}")

            # Versuche, das Kommando zu protokollieren
            try:
                self.log_command_execution(command)
            except Exception as e:
                self.logger.error(f"Error logging command execution: {e}")

        except Exception as e:
            self.logger.error(f"Error processing command: {e}")

    def inject_key_press(self, command):
        """Inject a key press event

        Args:
            command: Command dictionary with key information
        """
        key = command.get("key")
        if key is None:
            self.logger.error("Key press command missing 'key' parameter")
            return

        # Convert string key name to pygame key constant
        key_code = self.get_key_code(key)
        if key_code is None:
            self.logger.error(f"Unknown key: {key}")
            return

        # Statt direkt ein Event zu posten, schreiben wir in eine Datei, die vom Spiel gelesen wird
        self.write_input_command({
            "type": "key_press",
            "key": key,
            "key_code": key_code,
            "timestamp": time.time()
        })

        self.logger.info(f"Injected key press: {key}")
        self.last_action_time = time.time()

    def inject_key_release(self, command):
        """Inject a key release event

        Args:
            command: Command dictionary with key information
        """
        key = command.get("key")
        if key is None:
            self.logger.error("Key release command missing 'key' parameter")
            return

        # Convert string key name to pygame key constant
        key_code = self.get_key_code(key)
        if key_code is None:
            self.logger.error(f"Unknown key: {key}")
            return

        # Statt direkt ein Event zu posten, schreiben wir in eine Datei, die vom Spiel gelesen wird
        self.write_input_command({
            "type": "key_release",
            "key": key,
            "key_code": key_code,
            "timestamp": time.time()
        })

        self.logger.info(f"Injected key release: {key}")
        self.last_action_time = time.time()

    def inject_button_press(self, command):
        """Inject a controller button press event

        Args:
            command: Command dictionary with button information
        """
        button = command.get("button")
        if button is None:
            self.logger.error("Button press command missing 'button' parameter")
            return

        # Convert string button name to button constant
        button_code = self.get_button_code(button)
        if button_code is None:
            self.logger.error(f"Unknown button: {button}")
            return

        # Statt direkt ein Event zu posten, schreiben wir in eine Datei, die vom Spiel gelesen wird
        self.write_input_command({
            "type": "button_press",
            "button": button,
            "button_code": button_code,
            "timestamp": time.time()
        })

        self.logger.info(f"Injected button press: {button}")
        self.last_action_time = time.time()

    def inject_button_release(self, command):
        """Inject a controller button release event

        Args:
            command: Command dictionary with button information
        """
        button = command.get("button")
        if button is None:
            self.logger.error("Button release command missing 'button' parameter")
            return

        # Convert string button name to button constant
        button_code = self.get_button_code(button)
        if button_code is None:
            self.logger.error(f"Unknown button: {button}")
            return

        # Statt direkt ein Event zu posten, schreiben wir in eine Datei, die vom Spiel gelesen wird
        self.write_input_command({
            "type": "button_release",
            "button": button,
            "button_code": button_code,
            "timestamp": time.time()
        })

        self.logger.info(f"Injected button release: {button}")
        self.last_action_time = time.time()

    def write_input_command(self, command_data):
        """Schreibt ein Eingabekommando in eine Datei, die vom Spiel gelesen wird

        Args:
            command_data: Dictionary mit Kommandodaten
        """
        # Erstelle einen eindeutigen Dateinamen basierend auf dem Zeitstempel
        timestamp = time.strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"current_input_{timestamp}.json"
        file_path = os.path.join("input_commands", filename)

        # Stelle sicher, dass das Verzeichnis existiert
        os.makedirs("input_commands", exist_ok=True)

        try:
            with open(file_path, 'w') as f:
                json.dump(command_data, f)
            self.logger.debug(f"Wrote input command to {file_path}")
        except Exception as e:
            self.logger.error(f"Error writing input command: {e}")

    def handle_wait_command(self, command):
        """Handle a wait command

        Args:
            command: Command dictionary with wait information
        """
        try:
            duration = float(command.get("duration", 1.0))
            self.logger.info(f"Waiting for {duration} seconds")
            time.sleep(duration)
        except Exception as e:
            self.logger.error(f"Error in wait command: {e}")

    def handle_sequence_command(self, command):
        """Handle a sequence command (multiple commands in sequence)

        Args:
            command: Command dictionary with sequence information
        """
        sequence = command.get("sequence", [])
        if not sequence:
            self.logger.error("Sequence command missing 'sequence' parameter")
            return

        # Add the sequence to the command queue
        with self.queue_lock:
            for cmd in sequence:
                self.command_queue.append(cmd)

        self.logger.info(f"Added sequence of {len(sequence)} commands to the queue")

    def get_key_code(self, key_name):
        """Convert a key name to a pygame key code

        Args:
            key_name: Name of the key

        Returns:
            int: Pygame key code, or None if not found
        """
        key_map = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "w": pygame.K_w,
            "a": pygame.K_a,
            "s": pygame.K_s,
            "d": pygame.K_d,
            "space": pygame.K_SPACE,
            "return": pygame.K_RETURN,
            "enter": pygame.K_RETURN,
            "escape": pygame.K_ESCAPE,
            "esc": pygame.K_ESCAPE,
            "backspace": pygame.K_BACKSPACE,
            "tab": pygame.K_TAB,
            "shift": pygame.K_LSHIFT,
            "lshift": pygame.K_LSHIFT,
            "rshift": pygame.K_RSHIFT,
            "z": pygame.K_z,
            "x": pygame.K_x,
            "c": pygame.K_c,
            "v": pygame.K_v,
            "m": pygame.K_m,
            "f": pygame.K_f
        }

        return key_map.get(key_name.lower())

    def get_button_code(self, button_name):
        """Convert a button name to a button code

        Args:
            button_name: Name of the button

        Returns:
            int: Button code, or None if not found
        """
        button_map = {
            "a": BUTTON_A,
            "b": BUTTON_B,
            "x": BUTTON_X,
            "y": BUTTON_Y,
            "back": BUTTON_BACK,
            "start": BUTTON_START,
            "leftstick": BUTTON_LEFTSTICK,
            "rightstick": BUTTON_RIGHTSTICK,
            "leftshoulder": BUTTON_LEFTSHOULDER,
            "rightshoulder": BUTTON_RIGHTSHOULDER,
            "dpad_up": BUTTON_DPAD_UP,
            "dpad_down": BUTTON_DPAD_DOWN,
            "dpad_left": BUTTON_DPAD_LEFT,
            "dpad_right": BUTTON_DPAD_RIGHT,
            "guide": BUTTON_GUIDE
        }

        return button_map.get(button_name.lower())

    def log_session_start(self):
        """Log the start of a session"""
        with open(self.session_log_file, 'w') as f:
            f.write(f"=== Input Server Session Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")

    def log_session_end(self):
        """Log the end of a session"""
        with open(self.session_log_file, 'a') as f:
            f.write(f"\n=== Input Server Session Ended at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    def log_instructions(self, instructions):
        """Log instructions that were loaded

        Args:
            instructions: List of instruction dictionaries
        """
        try:
            with open(self.session_log_file, 'a') as f:
                f.write("\n--- Loaded Instructions ---\n")
                for i, instruction in enumerate(instructions):
                    f.write(f"{i+1}. {json.dumps(instruction)}\n")
                f.write("--- End of Instructions ---\n\n")
        except Exception as e:
            self.logger.error(f"Error logging instructions: {e}")

    def log_command_execution(self, command):
        """Log the execution of a command

        Args:
            command: Command dictionary
        """
        try:
            with open(self.session_log_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Executed: {json.dumps(command)}\n")
        except Exception as e:
            self.logger.error(f"Error logging command execution: {e}")

    def update_game_state(self, state, position=None):
        """Update the current game state

        Args:
            state: Current game state
            position: Current player position (optional)
        """
        self.game_state = state
        if position:
            self.player_position = position

        # Log the state update
        try:
            with open(self.session_log_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Game State: {state}")
                if position:
                    f.write(f", Position: {position}")
                f.write("\n")
        except Exception as e:
            self.logger.error(f"Error logging game state: {e}")


class InputFileHandler(FileSystemEventHandler):
    """Handler for file system events in the watch directory"""

    def __init__(self, server):
        """Initialize the file handler

        Args:
            server: InputServer instance
        """
        self.server = server

    def on_created(self, event):
        """Handle file creation events

        Args:
            event: File system event
        """
        if not event.is_directory and event.src_path.endswith('.json'):
            # Wait a moment to ensure the file is fully written
            time.sleep(0.5)
            self.server.process_instruction_file(event.src_path)


def main():
    """Main function"""
    server = InputServer()
    server.start()


if __name__ == "__main__":
    main()
