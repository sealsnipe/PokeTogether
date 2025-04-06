# Autonomous Testing System for PokeTogether

This directory contains tools for autonomous testing of the PokeTogether game. These tools allow you to:

1. Inject input commands into the game
2. Monitor the game's behavior through logs
3. Automate testing scenarios
4. Analyze the game's performance and behavior

## Components

The autonomous testing system consists of the following components:

### 1. Input Server (`input_server.py`)

A server that listens for instruction files in a designated directory and injects inputs into the game. The server:

- Watches a directory for JSON instruction files
- Processes these instructions to simulate keyboard/controller inputs
- Injects these inputs into the game using pygame events
- Logs the results for analysis

### 2. Test Instruction Generator (`generate_test_instructions.py`)

A tool that generates test instruction files for various testing scenarios:

- Movement tests (basic movement, diagonal movement, running)
- Action tests (interaction, menu navigation)
- Controller tests (buttons, D-pad, analog sticks)
- Menu navigation tests
- Comprehensive tests (combining all of the above)
- Custom test sequences

### 3. Log Analyzer (`analyze_game_logs.py`)

A tool that analyzes the game logs to detect issues and patterns:

- Input response times
- Error patterns
- Game state transitions
- Player movement patterns
- Performance metrics

### 4. Automated Test Runner (`run_automated_test.py`)

A script that runs the game and input server together for automated testing:

- Starts the game and input server
- Generates and applies test instructions
- Waits for the test to complete
- Analyzes the logs
- Generates a report

## Usage

### Basic Usage

To run a comprehensive test of the game:

```bash
python tools/run_automated_test.py
```

This will:
1. Start the game
2. Start the input server
3. Generate comprehensive test instructions
4. Wait for the test to complete (default: 120 seconds)
5. Analyze the logs
6. Generate a report

### Advanced Usage

#### Running Specific Tests

```bash
python tools/run_automated_test.py --test movement
```

Available test types:
- `movement`: Tests basic movement controls
- `action`: Tests action buttons
- `controller`: Tests controller input
- `menu`: Tests menu navigation
- `comprehensive`: Combines all tests
- `custom:name`: Runs a custom test sequence (e.g., `custom:explore_map`)

#### Adjusting Timeout

```bash
python tools/run_automated_test.py --timeout 300
```

This sets the test timeout to 300 seconds (5 minutes).

#### Using Custom Paths

```bash
python tools/run_automated_test.py --game path/to/game.py --server path/to/server.py
```

### Manual Testing

You can also use the components individually:

#### Running the Input Server

```bash
python tools/input_server.py
```

#### Generating Test Instructions

```bash
python tools/generate_test_instructions.py --test movement --output ./input_instructions
```

#### Analyzing Logs

```bash
python tools/analyze_game_logs.py --log game.log --output analysis_report.txt
```

## Creating Custom Test Sequences

You can create custom test sequences by modifying the `generate_custom_sequence` function in `generate_test_instructions.py`. The function takes a sequence name and returns a list of instruction dictionaries.

Example:

```python
def generate_custom_sequence(sequence_name):
    if sequence_name == "my_custom_test":
        instructions = []
        
        # Add your custom instructions here
        instructions.append({"type": "key_press", "key": "up"})
        instructions.append({"type": "wait", "duration": 1.0})
        instructions.append({"type": "key_release", "key": "up"})
        
        return instructions
    
    return None  # Sequence not found
```

Then run:

```bash
python tools/run_automated_test.py --test custom:my_custom_test
```

## Instruction Format

Instructions are JSON objects with the following format:

```json
[
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 1.0},
  {"type": "key_release", "key": "up"},
  {"type": "button_press", "button": "a"},
  {"type": "wait", "duration": 0.2},
  {"type": "button_release", "button": "a"}
]
```

Supported instruction types:
- `key_press`: Simulates a key press (requires `key` parameter)
- `key_release`: Simulates a key release (requires `key` parameter)
- `button_press`: Simulates a controller button press (requires `button` parameter)
- `button_release`: Simulates a controller button release (requires `button` parameter)
- `wait`: Waits for a specified duration in seconds (requires `duration` parameter)
- `sequence`: Executes a sequence of instructions (requires `sequence` parameter)

## Troubleshooting

### Game Not Responding to Inputs

- Make sure the game window is in focus
- Check that the input server is running (`python tools/input_server.py`)
- Verify that the instruction files are being created in the correct directory
- Check the input server logs for errors

### Input Server Not Starting

- Make sure pygame is installed (`pip install pygame`)
- Check that the watchdog library is installed (`pip install watchdog`)
- Verify that the input_instructions directory exists

### Log Analysis Failing

- Make sure the game.log file exists
- Check that the log format matches what the analyzer expects
- Try running the analyzer manually with verbose output

## Dependencies

- Python 3.6+
- pygame
- watchdog (for file system monitoring)

Install dependencies:

```bash
pip install pygame watchdog
```
