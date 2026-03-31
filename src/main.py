#!/usr/bin/env python3
"""
Lightburn CLI

A modular CLI tool to validate Lightburn .lbrn2 files against configurable rules.
"""

import sys
from pathlib import Path

# Add src directory to path for imports when running directly
_src_dir = Path(__file__).parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

import argparse

from commands import get_command_instances, get_command_names


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate Lightburn .lbrn2 files against configurable rules"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Get all command instances dynamically
    commands = get_command_instances()
    
    # Add parsers for each command
    for command in commands.values():
        command.add_parser(subparsers)
    
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()
    
    # Handle case where no command is provided
    if not args.command:
        valid_commands = get_command_names()
        cmd_str = ', '.join(valid_commands[:-1])
        if len(valid_commands) > 1:
            cmd_str += ', or ' + valid_commands[-1]
        else:
            cmd_str = valid_commands[0]
        print(f"Error: No command specified. Use {cmd_str}", file=sys.stderr)
        sys.exit(1)
    
    # Get command instances dynamically and run the appropriate command
    commands = get_command_instances()
    
    command = commands.get(args.command)
    if command:
        command.run(args)
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
