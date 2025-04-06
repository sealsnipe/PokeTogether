# Automated Multiplayer Testing Guide

This guide explains how to use the automated testing system for verifying the multiplayer functionality of PokeTogether.

## Overview

The automated testing system:

1. Starts a server process
2. Starts two client processes with different configurations
3. Verifies that both clients successfully connect to the server
4. Analyzes logs to confirm proper connection
5. Generates a detailed test report

## Prerequisites

- Python 3.6 or higher
- All required dependencies installed (see requirements.txt)
- Sufficient system resources to run three processes simultaneously

## Running the Tests

### Using the Batch File (Windows)

The simplest way to run the tests is to use the provided batch file:

```
run_multiplayer_test.bat
```

This will:
- Ask for confirmation before starting the test
- Run the test with default settings
- Display the test result
- Create detailed logs in the test_logs directory

### Using the Python Script Directly

You can also run the test script directly with additional options:

```
python test_local_multiplayer.py [options]
```

Available options:
- `--port PORT`: Use a specific port for the server (default: 8765)
- `--verbose`: Show more detailed output during the test
- `--no-cleanup`: Don't kill processes after the test (for debugging)
- `--log-dir DIR`: Specify a custom directory for test logs

## Understanding Test Results

The test will exit with one of the following status codes:

- `0`: Success - Both clients connected to the server successfully
- `1`: Failure - Not all clients connected to the server
- `2`: Interrupted - The test was interrupted by the user
- `3`: Error - An unexpected error occurred during the test

## Test Reports

After each test run, a detailed report is generated in the test_logs directory. The report includes:

- Test date and result
- Process information (PIDs, exit codes)
- Log file locations
- Excerpts from the server and client logs

## Log Files

The test creates several log files:

- `test_multiplayer.log`: Main test log
- `test_logs/server/server_stdout_*.log`: Server standard output
- `test_logs/server/server_stderr_*.log`: Server standard error
- `test_logs/client1/client1_stdout_*.log`: Client 1 standard output
- `test_logs/client1/client1_stderr_*.log`: Client 1 standard error
- `test_logs/client2/client2_stdout_*.log`: Client 2 standard output
- `test_logs/client2/client2_stderr_*.log`: Client 2 standard error
- `test_logs/test_report_*.txt`: Detailed test report

## Troubleshooting

### Connection Issues

If the test fails with connection issues:

1. Check if the server is starting correctly (see server logs)
2. Verify that the port is not in use by another application
3. Check for firewall or antivirus software blocking connections
4. Increase the connection timeout with `--timeout` option

### Process Management Issues

If processes are not being properly started or terminated:

1. Run with `--verbose` to see more detailed output
2. Use `--no-cleanup` to prevent automatic process termination
3. Check the system task manager for orphaned processes

## Extending the Tests

The test script can be extended to test additional aspects of the multiplayer functionality:

1. Add new command-line options in the `parse_arguments()` function
2. Add new test functions to verify specific features
3. Update the success criteria in the `monitor_connections()` function
4. Add new sections to the test report in the `generate_test_report()` function

## Implementation Details

The test script uses the following approach:

1. Starts processes using `subprocess.Popen`
2. Captures standard output and error to log files
3. Monitors log files for specific success markers
4. Terminates processes after the test completes
5. Generates a detailed report with test results

The success markers are added to the client and server code to make it easier to detect successful connections:

- Server: `[CONNECTION_STATUS] NEW CLIENT CONNECTED`
- Client: `[CONNECTION_STATUS] SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION`
