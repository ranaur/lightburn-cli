"""
Material command for Lightburn CLI.
"""

# Construct config path from material name
from pathlib import Path
import argparse
import json
import sys

from ._base import BaseCommand
from material_manager import MaterialManager


class MaterialCommand(BaseCommand):
    """Command to manage material variables."""
    
    def add_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Add the material command parser."""
        parser = subparsers.add_parser(
            "material",
            help="Manage material variables"
        )
        parser.add_argument(
            "material_name",
            help="Name of the material (used as filename in ~/.lightburn_cli directory)"
        )
        
        # Add subparsers for material actions
        material_subparsers = parser.add_subparsers(
            dest="material_action",
            help="Material actions"
        )
        
        # Material list command
        material_subparsers.add_parser("list", help="List all material variables")
        
        # Material get command
        get_parser = material_subparsers.add_parser("get", help="Get a specific material variable")
        get_parser.add_argument("key", help="Variable key to retrieve")
        
        # Material set command
        set_parser = material_subparsers.add_parser("set", help="Set a material variable value")
        set_parser.add_argument("key", help="Variable key to set")
        set_parser.add_argument("value", help="Variable value to set")
        
        # Material delete command
        delete_parser = material_subparsers.add_parser("delete", help="Delete a material variable")
        delete_parser.add_argument("key", help="Variable key to delete")
        
        # Material clear command
        material_subparsers.add_parser("clear", help="Clear all material variables")
        
        # Material export command
        material_subparsers.add_parser("export", help="Export material variables as JSON")
        
        # Material import command
        import_parser = material_subparsers.add_parser("import", help="Import material variables from JSON")
        import_parser.add_argument("file", help="JSON file to import variables from")
        
        return parser
    
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the material command."""
        # Get user home directory
        home_dir = Path.home()
        config_dir = home_dir / ".lightburn_cli"
        
        # Ensure config directory exists
        config_dir.mkdir(exist_ok=True)
        
        # Construct file path for this material
        config_path = config_dir / f"{args.material_name}.json"
        
        # Initialize material manager with the material-specific config path
        vars_manager = MaterialManager(custom_path=str(config_path))
        
        if not args.material_action:
            print("Error: No material action specified. Use 'list', 'get', 'set', 'delete', 'clear', 'export', or 'import'", file=sys.stderr)
            sys.exit(1)
        
        # Route to appropriate action handler
        action_method = getattr(self, f"_handle_{args.material_action}", None)
        if action_method:
            action_method(args, vars_manager, args.material_name)
        else:
            print(f"Error: Unknown material action '{args.material_action}'", file=sys.stderr)
            sys.exit(1)
    
    def _handle_list(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material list action."""
        variables = vars_manager.list_variables()
        if not variables:
            print(f"No material variables set for '{material_name}'.")
        else:
            print(f"Material Variables for '{material_name}':")
            for key, value in variables.items():
                print(f"  {key}: {value}")
    
    def _handle_get(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material get action."""
        value = vars_manager.get_variable(args.key)
        if value is None:
            print(f"Material variable '{args.key}' not found in '{material_name}'.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"{args.key}: {value}")
    
    def _handle_set(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material set action."""
        # Try to parse as JSON, fallback to string if fails
        try:
            parsed_value = json.loads(args.value)
        except json.JSONDecodeError:
            parsed_value = args.value
        
        vars_manager.set_variable(args.key, parsed_value)
        print(f"Material variable '{args.key}' set to: {parsed_value} for '{material_name}'")
    
    def _handle_delete(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material delete action."""
        if vars_manager.delete_variable(args.key):
            print(f"Material variable '{args.key}' deleted from '{material_name}'.")
        else:
            print(f"Material variable '{args.key}' not found in '{material_name}'.", file=sys.stderr)
            sys.exit(1)
    
    def _handle_clear(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material clear action."""
        vars_manager.clear_variables()
        print(f"All material variables cleared for '{material_name}'.")
    
    def _handle_export(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material export action."""
        variables = vars_manager.list_variables()
        print(json.dumps(variables, indent=2))
    
    def _handle_import(self, args: argparse.Namespace, vars_manager: MaterialManager, material_name: str) -> None:
        """Handle material import action."""
        try:
            with open(args.file, 'r') as f:
                variables = json.load(f)
            
            if not isinstance(variables, dict):
                print("Error: JSON file must contain a dictionary of material variables", file=sys.stderr)
                sys.exit(1)
            
            for key, value in variables.items():
                vars_manager.set_variable(key, value)
            
            print(f"Imported {len(variables)} material variables from {args.file} to '{material_name}'")
            
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error importing material variables: {e}", file=sys.stderr)
            sys.exit(1)
