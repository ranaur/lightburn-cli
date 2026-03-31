"""
Base class for all commands.
"""

from abc import ABC, abstractmethod
import argparse
import sys
from typing import Any


class BaseCommand(ABC):
    """Base class for all CLI commands."""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Command', '').lower()
    
    @abstractmethod
    def add_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """
        Add this command's parser to the subparsers.
        
        Args:
            subparsers: The subparsers action to add this command to
            
        Returns:
            The created parser for this command
        """
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> None:
        """
        Execute the command with the parsed arguments.
        
        Args:
            args: Parsed command line arguments
        """
        pass
    
    def run(self, args: argparse.Namespace) -> None:
        """
        Run the command with error handling.
        
        Args:
            args: Parsed command line arguments
        """
        try:
            self.execute(args)
        except Exception as e:
            print(f"Error in {self.name} command: {e}", file=sys.stderr)
            sys.exit(1)
