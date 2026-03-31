"""
Command discovery utility for automatically loading command classes.
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Type

from ._base import BaseCommand


def discover_commands() -> Dict[str, Type[BaseCommand]]:
    """
    Automatically discover and load command classes from the commands directory.
    
    Returns:
        Dictionary mapping command names to command classes
    """
    commands = {}
    
    # Get the commands directory path
    commands_dir = Path(__file__).parent
    
    # Find all Python files that don't start with underscore
    for file_path in commands_dir.glob("*.py"):
        if file_path.name.startswith("_"):
            continue  # Skip files starting with underscore
        
        # Get module name (filename without .py extension)
        module_name = file_path.stem
        
        try:
            # Import the module
            module = importlib.import_module(f".{module_name}", package=__package__)
            
            # Find all classes in the module that inherit from BaseCommand
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseCommand) and 
                    obj is not BaseCommand and 
                    obj.__module__ == module.__name__):
                    
                    # Instantiate the command to get its name
                    command_instance = obj()
                    commands[command_instance.name] = obj
                    
        except (ImportError, AttributeError) as e:
            # Skip modules that can't be imported or don't have expected structure
            print(f"Warning: Could not load command from {module_name}: {e}")
            continue
    
    return commands


def get_command_instances() -> Dict[str, BaseCommand]:
    """
    Get instances of all discovered commands.
    
    Returns:
        Dictionary mapping command names to command instances
    """
    command_classes = discover_commands()
    return {name: cls() for name, cls in command_classes.items()}


def get_command_names() -> List[str]:
    """
    Get list of all available command names.
    
    Returns:
        List of command names
    """
    return list(discover_commands().keys())
