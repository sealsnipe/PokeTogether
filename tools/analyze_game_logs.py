#!/usr/bin/env python
"""
Analyze Game Logs - Analyzes game logs to detect issues and patterns
"""

import os
import sys
import re
import json
import argparse
import datetime
from collections import defaultdict, Counter

def parse_log_file(log_file):
    """Parse a log file and extract relevant information

    Args:
        log_file: Path to the log file

    Returns:
        dict: Dictionary containing parsed log data
    """
    print(f"Parsing log file: {log_file}")
    
    # Initialize data structure
    log_data = {
        "errors": [],
        "warnings": [],
        "input_events": [],
        "player_movements": [],
        "state_changes": [],
        "timestamps": {
            "first": None,
            "last": None
        },
        "statistics": {
            "error_count": 0,
            "warning_count": 0,
            "input_count": 0,
            "movement_count": 0
        }
    }
    
    # Regular expressions for parsing
    timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    error_pattern = re.compile(f"{timestamp_pattern} - .* - ERROR - (.*)")
    warning_pattern = re.compile(f"{timestamp_pattern} - .* - WARNING - (.*)")
    input_pattern = re.compile(f"{timestamp_pattern} - .* - INFO - Aktion erkannt: (.*)")
    movement_pattern = re.compile(f"{timestamp_pattern} - .* - DEBUG - Bewegung: \((.*), (.*)\) -> \((.*), (.*)\)")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Extract timestamp if present
                timestamp_match = re.search(timestamp_pattern, line)
                if timestamp_match:
                    timestamp_str = timestamp_match.group(1)
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    # Update first and last timestamps
                    if log_data["timestamps"]["first"] is None or timestamp < log_data["timestamps"]["first"]:
                        log_data["timestamps"]["first"] = timestamp
                    if log_data["timestamps"]["last"] is None or timestamp > log_data["timestamps"]["last"]:
                        log_data["timestamps"]["last"] = timestamp
                
                # Check for errors
                error_match = error_pattern.search(line)
                if error_match:
                    timestamp_str = error_match.group(1)
                    error_msg = error_match.group(2)
                    log_data["errors"].append({
                        "timestamp": timestamp_str,
                        "message": error_msg
                    })
                    log_data["statistics"]["error_count"] += 1
                    continue
                
                # Check for warnings
                warning_match = warning_pattern.search(line)
                if warning_match:
                    timestamp_str = warning_match.group(1)
                    warning_msg = warning_match.group(2)
                    log_data["warnings"].append({
                        "timestamp": timestamp_str,
                        "message": warning_msg
                    })
                    log_data["statistics"]["warning_count"] += 1
                    continue
                
                # Check for input events
                input_match = input_pattern.search(line)
                if input_match:
                    timestamp_str = input_match.group(1)
                    action = input_match.group(2)
                    log_data["input_events"].append({
                        "timestamp": timestamp_str,
                        "action": action
                    })
                    log_data["statistics"]["input_count"] += 1
                    continue
                
                # Check for player movements
                movement_match = movement_pattern.search(line)
                if movement_match:
                    timestamp_str = timestamp_match.group(1)
                    old_x = float(movement_match.group(1))
                    old_y = float(movement_match.group(2))
                    new_x = float(movement_match.group(3))
                    new_y = float(movement_match.group(4))
                    
                    log_data["player_movements"].append({
                        "timestamp": timestamp_str,
                        "old_position": (old_x, old_y),
                        "new_position": (new_x, new_y),
                        "delta": (new_x - old_x, new_y - old_y)
                    })
                    log_data["statistics"]["movement_count"] += 1
                    continue
                
                # Check for state changes (custom format for our input server)
                if "Game State:" in line and timestamp_match:
                    timestamp_str = timestamp_match.group(1)
                    state_match = re.search(r"Game State: (\w+)", line)
                    position_match = re.search(r"Position: \((.*), (.*)\)", line)
                    
                    if state_match:
                        state = state_match.group(1)
                        position = None
                        
                        if position_match:
                            x = float(position_match.group(1))
                            y = float(position_match.group(2))
                            position = (x, y)
                        
                        log_data["state_changes"].append({
                            "timestamp": timestamp_str,
                            "state": state,
                            "position": position
                        })
    
    except Exception as e:
        print(f"Error parsing log file: {e}")
    
    return log_data

def analyze_input_response(log_data):
    """Analyze input response times and patterns

    Args:
        log_data: Dictionary containing parsed log data

    Returns:
        dict: Analysis results
    """
    results = {
        "input_response": {
            "average_time": None,
            "max_time": None,
            "min_time": None,
            "response_times": [],
            "missed_inputs": []
        },
        "input_patterns": {
            "most_common_actions": [],
            "action_counts": {}
        }
    }
    
    # Count actions
    action_counter = Counter()
    for event in log_data["input_events"]:
        action = event["action"]
        action_counter[action] += 1
    
    # Store action counts
    results["input_patterns"]["action_counts"] = dict(action_counter)
    results["input_patterns"]["most_common_actions"] = action_counter.most_common(5)
    
    # Analyze input-movement correlation
    if log_data["input_events"] and log_data["player_movements"]:
        response_times = []
        
        # Convert timestamps to datetime objects
        for event in log_data["input_events"]:
            event["datetime"] = datetime.datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
        
        for movement in log_data["player_movements"]:
            movement["datetime"] = datetime.datetime.strptime(movement["timestamp"], "%Y-%m-%d %H:%M:%S")
        
        # Sort by timestamp
        input_events = sorted(log_data["input_events"], key=lambda x: x["datetime"])
        movements = sorted(log_data["player_movements"], key=lambda x: x["datetime"])
        
        # Find closest input event before each movement
        for movement in movements:
            # Find the most recent input event before this movement
            closest_event = None
            min_time_diff = datetime.timedelta(seconds=5)  # Max 5 seconds difference
            
            for event in input_events:
                if event["datetime"] <= movement["datetime"]:
                    time_diff = movement["datetime"] - event["datetime"]
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_event = event
            
            if closest_event:
                response_time = (movement["datetime"] - closest_event["datetime"]).total_seconds()
                results["input_response"]["response_times"].append({
                    "input": closest_event["action"],
                    "response_time": response_time,
                    "movement_delta": movement["delta"]
                })
        
        # Calculate statistics
        if results["input_response"]["response_times"]:
            times = [r["response_time"] for r in results["input_response"]["response_times"]]
            results["input_response"]["average_time"] = sum(times) / len(times)
            results["input_response"]["max_time"] = max(times)
            results["input_response"]["min_time"] = min(times)
    
    return results

def analyze_errors(log_data):
    """Analyze errors and warnings in the log data

    Args:
        log_data: Dictionary containing parsed log data

    Returns:
        dict: Analysis results
    """
    results = {
        "error_analysis": {
            "total_errors": log_data["statistics"]["error_count"],
            "total_warnings": log_data["statistics"]["warning_count"],
            "error_categories": {},
            "warning_categories": {},
            "critical_errors": []
        }
    }
    
    # Categorize errors
    error_categories = defaultdict(int)
    for error in log_data["errors"]:
        # Extract the first few words as the category
        category = " ".join(error["message"].split()[:3])
        error_categories[category] += 1
        
        # Check for critical errors
        if any(keyword in error["message"].lower() for keyword in 
               ["crash", "exception", "fatal", "critical", "failed"]):
            results["error_analysis"]["critical_errors"].append(error)
    
    # Categorize warnings
    warning_categories = defaultdict(int)
    for warning in log_data["warnings"]:
        # Extract the first few words as the category
        category = " ".join(warning["message"].split()[:3])
        warning_categories[category] += 1
    
    results["error_analysis"]["error_categories"] = dict(error_categories)
    results["error_analysis"]["warning_categories"] = dict(warning_categories)
    
    return results

def analyze_game_state(log_data):
    """Analyze game state changes

    Args:
        log_data: Dictionary containing parsed log data

    Returns:
        dict: Analysis results
    """
    results = {
        "state_analysis": {
            "state_transitions": [],
            "state_durations": {},
            "most_common_states": []
        }
    }
    
    # Analyze state changes
    if log_data["state_changes"]:
        # Convert timestamps to datetime objects
        for change in log_data["state_changes"]:
            change["datetime"] = datetime.datetime.strptime(change["timestamp"], "%Y-%m-%d %H:%M:%S")
        
        # Sort by timestamp
        state_changes = sorted(log_data["state_changes"], key=lambda x: x["datetime"])
        
        # Track state transitions
        prev_state = None
        state_durations = defaultdict(datetime.timedelta)
        state_counts = Counter()
        
        for i, change in enumerate(state_changes):
            current_state = change["state"]
            state_counts[current_state] += 1
            
            if prev_state:
                # Record the transition
                results["state_analysis"]["state_transitions"].append({
                    "from": prev_state,
                    "to": current_state,
                    "timestamp": change["timestamp"]
                })
                
                # Calculate duration of previous state
                if i > 0:
                    duration = change["datetime"] - state_changes[i-1]["datetime"]
                    state_durations[prev_state] += duration
            
            prev_state = current_state
        
        # Convert durations to seconds
        results["state_analysis"]["state_durations"] = {
            state: duration.total_seconds() 
            for state, duration in state_durations.items()
        }
        
        # Most common states
        results["state_analysis"]["most_common_states"] = state_counts.most_common()
    
    return results

def analyze_movement_patterns(log_data):
    """Analyze player movement patterns

    Args:
        log_data: Dictionary containing parsed log data

    Returns:
        dict: Analysis results
    """
    results = {
        "movement_analysis": {
            "total_distance": 0,
            "average_speed": 0,
            "direction_changes": 0,
            "movement_heatmap": {},
            "common_directions": {}
        }
    }
    
    if log_data["player_movements"]:
        # Calculate total distance and direction changes
        total_distance = 0
        direction_changes = 0
        prev_direction = None
        directions = []
        
        # Convert timestamps to datetime objects
        for movement in log_data["player_movements"]:
            movement["datetime"] = datetime.datetime.strptime(movement["timestamp"], "%Y-%m-%d %H:%M:%S")
        
        # Sort by timestamp
        movements = sorted(log_data["player_movements"], key=lambda x: x["datetime"])
        
        for movement in movements:
            # Calculate distance for this movement
            dx, dy = movement["delta"]
            distance = (dx**2 + dy**2)**0.5
            total_distance += distance
            
            # Determine direction
            if abs(dx) > abs(dy):
                direction = "right" if dx > 0 else "left"
            else:
                direction = "down" if dy > 0 else "up"
            
            directions.append(direction)
            
            # Check for direction change
            if prev_direction and direction != prev_direction:
                direction_changes += 1
            
            prev_direction = direction
            
            # Add to heatmap (rounded to nearest 10)
            x, y = movement["new_position"]
            heatmap_key = (round(x/10)*10, round(y/10)*10)
            if heatmap_key in results["movement_analysis"]["movement_heatmap"]:
                results["movement_analysis"]["movement_heatmap"][heatmap_key] += 1
            else:
                results["movement_analysis"]["movement_heatmap"][heatmap_key] = 1
        
        # Calculate average speed
        if len(movements) > 1:
            total_time = (movements[-1]["datetime"] - movements[0]["datetime"]).total_seconds()
            if total_time > 0:
                results["movement_analysis"]["average_speed"] = total_distance / total_time
        
        results["movement_analysis"]["total_distance"] = total_distance
        results["movement_analysis"]["direction_changes"] = direction_changes
        results["movement_analysis"]["common_directions"] = dict(Counter(directions).most_common())
    
    return results

def generate_report(log_data, analysis_results):
    """Generate a human-readable report from the analysis results

    Args:
        log_data: Dictionary containing parsed log data
        analysis_results: Dictionary containing analysis results

    Returns:
        str: Human-readable report
    """
    report = []
    
    # Header
    report.append("=== Game Analysis Report ===")
    report.append("")
    
    # Session information
    if log_data["timestamps"]["first"] and log_data["timestamps"]["last"]:
        duration = log_data["timestamps"]["last"] - log_data["timestamps"]["first"]
        report.append(f"Session Duration: {duration}")
        report.append(f"Start Time: {log_data['timestamps']['first']}")
        report.append(f"End Time: {log_data['timestamps']['last']}")
        report.append("")
    
    # Statistics summary
    report.append("=== Statistics Summary ===")
    report.append(f"Total Errors: {log_data['statistics']['error_count']}")
    report.append(f"Total Warnings: {log_data['statistics']['warning_count']}")
    report.append(f"Input Events: {log_data['statistics']['input_count']}")
    report.append(f"Player Movements: {log_data['statistics']['movement_count']}")
    report.append("")
    
    # Error analysis
    if "error_analysis" in analysis_results:
        report.append("=== Error Analysis ===")
        
        if analysis_results["error_analysis"]["critical_errors"]:
            report.append("Critical Errors:")
            for error in analysis_results["error_analysis"]["critical_errors"]:
                report.append(f"  - [{error['timestamp']}] {error['message']}")
            report.append("")
        
        if analysis_results["error_analysis"]["error_categories"]:
            report.append("Error Categories:")
            for category, count in sorted(analysis_results["error_analysis"]["error_categories"].items(), 
                                         key=lambda x: x[1], reverse=True):
                report.append(f"  - {category}: {count}")
            report.append("")
    
    # Input response analysis
    if "input_response" in analysis_results:
        report.append("=== Input Response Analysis ===")
        
        if analysis_results["input_response"]["average_time"] is not None:
            report.append(f"Average Response Time: {analysis_results['input_response']['average_time']:.3f} seconds")
            report.append(f"Min Response Time: {analysis_results['input_response']['min_time']:.3f} seconds")
            report.append(f"Max Response Time: {analysis_results['input_response']['max_time']:.3f} seconds")
        
        if analysis_results["input_patterns"]["most_common_actions"]:
            report.append("\nMost Common Actions:")
            for action, count in analysis_results["input_patterns"]["most_common_actions"]:
                report.append(f"  - {action}: {count}")
        
        report.append("")
    
    # Movement analysis
    if "movement_analysis" in analysis_results:
        report.append("=== Movement Analysis ===")
        report.append(f"Total Distance: {analysis_results['movement_analysis']['total_distance']:.2f} pixels")
        report.append(f"Average Speed: {analysis_results['movement_analysis']['average_speed']:.2f} pixels/second")
        report.append(f"Direction Changes: {analysis_results['movement_analysis']['direction_changes']}")
        
        if analysis_results["movement_analysis"]["common_directions"]:
            report.append("\nCommon Directions:")
            for direction, count in sorted(analysis_results["movement_analysis"]["common_directions"].items(), 
                                          key=lambda x: x[1], reverse=True):
                report.append(f"  - {direction}: {count}")
        
        report.append("")
    
    # State analysis
    if "state_analysis" in analysis_results:
        report.append("=== Game State Analysis ===")
        
        if analysis_results["state_analysis"]["most_common_states"]:
            report.append("Most Common States:")
            for state, count in analysis_results["state_analysis"]["most_common_states"]:
                report.append(f"  - {state}: {count}")
        
        if analysis_results["state_analysis"]["state_durations"]:
            report.append("\nState Durations (seconds):")
            for state, duration in sorted(analysis_results["state_analysis"]["state_durations"].items(), 
                                         key=lambda x: x[1], reverse=True):
                report.append(f"  - {state}: {duration:.2f}")
        
        report.append("")
    
    # Conclusion
    report.append("=== Conclusion ===")
    
    # Identify potential issues
    issues = []
    
    # Check for high error rate
    if log_data["statistics"]["error_count"] > 10:
        issues.append(f"High error count ({log_data['statistics']['error_count']})")
    
    # Check for slow input response
    if "input_response" in analysis_results and analysis_results["input_response"]["average_time"] is not None:
        if analysis_results["input_response"]["average_time"] > 0.5:
            issues.append(f"Slow input response (avg: {analysis_results['input_response']['average_time']:.3f}s)")
    
    # Check for critical errors
    if "error_analysis" in analysis_results and analysis_results["error_analysis"]["critical_errors"]:
        issues.append(f"Critical errors detected ({len(analysis_results['error_analysis']['critical_errors'])})")
    
    if issues:
        report.append("Potential Issues Detected:")
        for issue in issues:
            report.append(f"  - {issue}")
    else:
        report.append("No significant issues detected.")
    
    return "\n".join(report)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze game logs to detect issues and patterns")
    parser.add_argument("--log", required=True, help="Path to the log file to analyze")
    parser.add_argument("--output", help="Path to save the analysis report (default: print to console)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format instead of human-readable")
    
    args = parser.parse_args()
    
    # Parse the log file
    log_data = parse_log_file(args.log)
    
    # Perform analysis
    analysis_results = {}
    analysis_results.update(analyze_input_response(log_data))
    analysis_results.update(analyze_errors(log_data))
    analysis_results.update(analyze_game_state(log_data))
    analysis_results.update(analyze_movement_patterns(log_data))
    
    # Generate output
    if args.json:
        # Combine log data and analysis results
        output_data = {
            "log_data": log_data,
            "analysis": analysis_results
        }
        
        # Convert datetime objects to strings
        output_json = json.dumps(output_data, default=str, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"JSON analysis saved to {args.output}")
        else:
            print(output_json)
    else:
        # Generate human-readable report
        report = generate_report(log_data, analysis_results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Analysis report saved to {args.output}")
        else:
            print(report)

if __name__ == "__main__":
    main()
