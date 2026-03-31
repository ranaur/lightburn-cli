"""
Update command for Lightburn CLI.
"""

import argparse
from pathlib import Path
from typing import List
from update_loader import UpdateLoader
from lightburn_file import LightburnFile
from ._base import BaseCommand

class UpdateCommand(BaseCommand):
    """Command to update Lightburn files based on update rules."""
    
    def add_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Add the update command parser."""
        parser = subparsers.add_parser(
            "update",
            help="Update Lightburn files using specified update rules"
        )
        parser.add_argument(
            "file",
            help="Path to the Lightburn file to update"
        )
        parser.add_argument(
            "update_rule",
            help="Name of the update rule to apply"
        )
        parser.add_argument(
            "parameters",
            nargs="*",
            help="Parameters for the update rule (format: key=value)"
        )
        parser.add_argument(
            "--urules",
            help="Path to urules directory (default: urules)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without modifying the file"
        )
        return parser
    
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the update command."""
        # Parse parameters
        params = {}
        for param in args.parameters:
            if "=" not in param:
                print(f"Error: Parameter '{param}' must be in format key=value")
                return
            key, value = param.split("=", 1)
            params[key] = value
        
        # Initialize update loader
        urules_dir = "urules"
        update_loader = UpdateLoader(urules_dir)
        
        # Load update rules
        try:
            update_rules = update_loader.load_all_update_rules()
        except Exception as e:
            print(f"Error loading update rules: {e}")
            return
        
        # Find the specified update rule
        update_rule = None
        for rule in update_rules:
            if rule.name == args.update_rule:
                update_rule = rule
                break
        
        if not update_rule:
            print(f"Error: Update rule '{args.update_rule}' not found")
            print(f"Available update rules: {[rule.name for rule in update_rules]}")
            return
        
        # Validate parameters
        errors = update_rule.validate_parameters(**params)
        if errors:
            print("Parameter validation errors:")
            for error in errors:
                print(f"  - {error}")
            return
        
        # Check if file exists
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found")
            return

        lightburn_file = LightburnFile(file_path)

        # Apply the update rule
        try:
            result = update_rule.update(lightburn_file, file_path, dry_run=args.dry_run, **params)
            
            # Save the file if changes were made and not in dry run mode
            if result.modified and not args.dry_run:
                lightburn_file.write(file_path, encoding='utf-8', xml_declaration=True)
            
            if result.modified:
                action = "Would be updated" if args.dry_run else "Updated"
                print(f"✅ {action}: {args.file}")
                if result.message:
                    print(f"   {result.message}")
            else:
                print(f"ℹ️  No changes needed: {args.file}")
                if result.message:
                    print(f"   {result.message}")
            
            # Show details if any
            if result.details:
                print("   Details:")
                for key, value in result.details.items():
                    if key == "individual_results" and isinstance(value, list):
                        print(f"     {key}:")
                        for i, individual_result in enumerate(value, 1):
                            if individual_result and hasattr(individual_result, 'message'):
                                print(f"       {i}. {individual_result.message}")
                    else:
                        print(f"     {key}: {value}")
                
        except Exception as e:
            print(f"Error applying update rule: {e}")
            return
        
        return
