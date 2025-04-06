#!/usr/bin/env python
"""
Generate Test Instructions - Creates instruction files for testing the game
"""

import os
import sys
import json
import time
import argparse

def create_directory(directory):
    """Create a directory if it doesn't exist

    Args:
        directory: Directory path to create
    """
    os.makedirs(directory, exist_ok=True)

def save_instructions(instructions, filename, directory="./input_instructions"):
    """Save instructions to a file

    Args:
        instructions: List of instruction dictionaries
        filename: Name of the file to save
        directory: Directory to save the file in
    """
    create_directory(directory)

    # Add timestamp to filename to ensure uniqueness
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.json"
    file_path = os.path.join(directory, full_filename)

    with open(file_path, 'w') as f:
        json.dump(instructions, f, indent=2)

    print(f"Saved instructions to {file_path}")
    return file_path

def generate_movement_test():
    """Generate instructions for testing player movement

    Returns:
        list: List of instruction dictionaries
    """
    instructions = []

    # Test basic movement in all four directions
    directions = ["up", "right", "down", "left"]

    for direction in directions:
        # Press the key for 2 seconds
        instructions.append({"type": "key_press", "key": direction})
        instructions.append({"type": "wait", "duration": 2.0})
        instructions.append({"type": "key_release", "key": direction})

        # Wait longer between directions
        instructions.append({"type": "wait", "duration": 1.0})

    # Test diagonal movement (pressing two keys at once)
    diagonals = [("up", "right"), ("right", "down"), ("down", "left"), ("left", "up")]

    for dir1, dir2 in diagonals:
        # Press both keys for 1 second
        instructions.append({"type": "key_press", "key": dir1})
        instructions.append({"type": "key_press", "key": dir2})
        instructions.append({"type": "wait", "duration": 1.0})
        instructions.append({"type": "key_release", "key": dir1})
        instructions.append({"type": "key_release", "key": dir2})

        # Wait a moment between diagonals
        instructions.append({"type": "wait", "duration": 0.5})

    # Test running (holding shift while moving)
    instructions.append({"type": "key_press", "key": "shift"})

    for direction in directions:
        # Press the key for 1 second while holding shift
        instructions.append({"type": "key_press", "key": direction})
        instructions.append({"type": "wait", "duration": 1.0})
        instructions.append({"type": "key_release", "key": direction})

        # Wait a moment between directions
        instructions.append({"type": "wait", "duration": 0.5})

    # Release shift
    instructions.append({"type": "key_release", "key": "shift"})

    return instructions

def generate_action_test():
    """Generate instructions for testing player actions

    Returns:
        list: List of instruction dictionaries
    """
    instructions = []

    # Test action button (space/enter)
    instructions.append({"type": "key_press", "key": "space"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "space"})
    instructions.append({"type": "wait", "duration": 1.0})

    instructions.append({"type": "key_press", "key": "return"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "return"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Test cancel button (escape/backspace)
    instructions.append({"type": "key_press", "key": "escape"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "escape"})
    instructions.append({"type": "wait", "duration": 1.0})

    instructions.append({"type": "key_press", "key": "backspace"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "backspace"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Test menu button (tab/m)
    instructions.append({"type": "key_press", "key": "tab"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "tab"})
    instructions.append({"type": "wait", "duration": 1.0})

    instructions.append({"type": "key_press", "key": "m"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "m"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Test fast forward (f)
    instructions.append({"type": "key_press", "key": "f"})
    instructions.append({"type": "wait", "duration": 2.0})
    instructions.append({"type": "key_release", "key": "f"})
    instructions.append({"type": "wait", "duration": 1.0})

    return instructions

def generate_controller_test():
    """Generate instructions for testing controller input

    Returns:
        list: List of instruction dictionaries
    """
    instructions = []

    # Test D-pad movement
    dpad_directions = ["dpad_up", "dpad_right", "dpad_down", "dpad_left"]

    for direction in dpad_directions:
        # Press the button for 1 second
        instructions.append({"type": "button_press", "button": direction})
        instructions.append({"type": "wait", "duration": 1.0})
        instructions.append({"type": "button_release", "button": direction})

        # Wait a moment between directions
        instructions.append({"type": "wait", "duration": 0.5})

    # Test action buttons
    action_buttons = ["a", "b", "x", "y"]

    for button in action_buttons:
        # Press the button
        instructions.append({"type": "button_press", "button": button})
        instructions.append({"type": "wait", "duration": 0.2})
        instructions.append({"type": "button_release", "button": button})

        # Wait a moment between buttons
        instructions.append({"type": "wait", "duration": 0.5})

    # Test shoulder buttons
    shoulder_buttons = ["leftshoulder", "rightshoulder"]

    for button in shoulder_buttons:
        # Press the button
        instructions.append({"type": "button_press", "button": button})
        instructions.append({"type": "wait", "duration": 1.0})
        instructions.append({"type": "button_release", "button": button})

        # Wait a moment between buttons
        instructions.append({"type": "wait", "duration": 0.5})

    # Test start/back buttons
    menu_buttons = ["start", "back"]

    for button in menu_buttons:
        # Press the button
        instructions.append({"type": "button_press", "button": button})
        instructions.append({"type": "wait", "duration": 0.2})
        instructions.append({"type": "button_release", "button": button})

        # Wait a moment between buttons
        instructions.append({"type": "wait", "duration": 0.5})

    return instructions

def generate_menu_navigation_test():
    """Generate instructions for testing menu navigation

    Returns:
        list: List of instruction dictionaries
    """
    instructions = []

    # Open the menu
    instructions.append({"type": "key_press", "key": "tab"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "tab"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Navigate through menu options (assuming menu navigation with arrow keys)
    for _ in range(4):  # Navigate through 4 options
        instructions.append({"type": "key_press", "key": "down"})
        instructions.append({"type": "wait", "duration": 0.2})
        instructions.append({"type": "key_release", "key": "down"})
        instructions.append({"type": "wait", "duration": 0.5})

    # Go back up
    for _ in range(4):  # Navigate back up
        instructions.append({"type": "key_press", "key": "up"})
        instructions.append({"type": "wait", "duration": 0.2})
        instructions.append({"type": "key_release", "key": "up"})
        instructions.append({"type": "wait", "duration": 0.5})

    # Select an option
    instructions.append({"type": "key_press", "key": "return"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "return"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Cancel/go back
    instructions.append({"type": "key_press", "key": "escape"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "escape"})
    instructions.append({"type": "wait", "duration": 1.0})

    # Close the menu
    instructions.append({"type": "key_press", "key": "tab"})
    instructions.append({"type": "wait", "duration": 0.2})
    instructions.append({"type": "key_release", "key": "tab"})

    return instructions

def generate_comprehensive_test():
    """Generate a comprehensive test that combines all other tests

    Returns:
        list: List of instruction dictionaries
    """
    instructions = []

    # Add all tests with a pause between them
    tests = [
        generate_movement_test(),
        generate_action_test(),
        generate_controller_test(),
        generate_menu_navigation_test()
    ]

    for test in tests:
        instructions.extend(test)
        # Add a longer pause between test sections
        instructions.append({"type": "wait", "duration": 2.0})

    return instructions

def generate_custom_sequence(sequence_name):
    """Generate a custom sequence based on the name

    Args:
        sequence_name: Name of the sequence to generate

    Returns:
        list: List of instruction dictionaries, or None if not found
    """
    # Define some custom sequences
    if sequence_name == "explore_map":
        # A sequence that explores the map by moving in a spiral pattern
        instructions = []

        # Move in a spiral pattern
        directions = ["right", "down", "left", "up"]
        steps = 1

        for _ in range(10):  # 10 spiral cycles
            for i, direction in enumerate(directions):
                # Increase steps every 2 directions
                if i % 2 == 0 and i > 0:
                    steps += 1

                # Move in the current direction for 'steps' seconds
                instructions.append({"type": "key_press", "key": direction})
                instructions.append({"type": "wait", "duration": steps})
                instructions.append({"type": "key_release", "key": direction})
                instructions.append({"type": "wait", "duration": 0.2})

        return instructions

    elif sequence_name == "stress_test":
        # A sequence that rapidly presses many keys to stress test the input system
        instructions = []

        # Define all keys to test
        all_keys = ["up", "down", "left", "right", "space", "return", "escape",
                   "tab", "shift", "z", "x", "c", "v", "m", "f"]

        # Rapidly press and release each key
        for _ in range(3):  # Repeat 3 times
            for key in all_keys:
                instructions.append({"type": "key_press", "key": key})
                instructions.append({"type": "wait", "duration": 0.1})
                instructions.append({"type": "key_release", "key": key})
                instructions.append({"type": "wait", "duration": 0.1})

        return instructions

    # Add more custom sequences as needed

    return None  # Sequence not found

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate test instructions for the game")
    parser.add_argument("--test", choices=["movement", "action", "controller", "menu", "comprehensive", "custom"],
                        default="comprehensive", help="Type of test to generate")
    parser.add_argument("--custom", help="Name of custom sequence (if --test=custom)")
    parser.add_argument("--output", default="./input_instructions", help="Output directory")

    args = parser.parse_args()

    # Generate the requested test
    if args.test == "movement":
        instructions = generate_movement_test()
        filename = "movement_test"
    elif args.test == "action":
        instructions = generate_action_test()
        filename = "action_test"
    elif args.test == "controller":
        instructions = generate_controller_test()
        filename = "controller_test"
    elif args.test == "menu":
        instructions = generate_menu_navigation_test()
        filename = "menu_test"
    elif args.test == "comprehensive":
        instructions = generate_comprehensive_test()
        filename = "comprehensive_test"
    elif args.test == "custom":
        if not args.custom:
            print("Error: --custom argument is required when --test=custom")
            return

        instructions = generate_custom_sequence(args.custom)
        if instructions is None:
            print(f"Error: Custom sequence '{args.custom}' not found")
            return

        filename = f"custom_{args.custom}"

    # Save the instructions
    save_instructions(instructions, filename, args.output)

if __name__ == "__main__":
    main()
