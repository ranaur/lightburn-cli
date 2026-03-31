"""
Rules command for Lightburn CLI.
"""

import argparse
from pathlib import Path
from typing import List

from ._base import BaseCommand
from validation_loader import ValidationLoader
from update_loader import UpdateLoader


class RulesCommand(BaseCommand):
    """Command to list and manage validation and update rules."""
    
    def add_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Add the rules command parser."""
        parser = subparsers.add_parser(
            "rules",
            help="List available rules"
        )
        parser.add_argument(
            "--rules",
            help="Path to rules directory (default: vrules for validation rules)"
        )
        parser.add_argument(
            "--urules",
            help="Path to update rules directory (default: urules for update rules)"
        )
        parser.add_argument(
            "--format",
            choices=["list", "detailed"],
            default="list",
            help="Output format (default: list)"
        )
        return parser
    
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the rules command."""
        # Initialize rule loaders
        rules_dir = args.rules or "vrules"  # Default vrules directory
        urules_dir = args.urules or "urules"  # Default urules directory
        
        # Load validation rules
        rule_loader = ValidationLoader(rules_dir)
        validation_rules = rule_loader.load_all_rules()
        
        # Load update rules
        update_loader = UpdateLoader(urules_dir)
        update_rules = update_loader.load_all_update_rules()
        
        if args.format == "detailed":
            self._print_detailed_rules(validation_rules, update_rules)
        else:
            self._print_rules_list(validation_rules, update_rules)
    
    def _print_rules_list(self, validation_rules: List, update_rules: List) -> None:
        """Print a simple list of validation and update rules."""
        print("Validation Rules (vrules):")
        if validation_rules:
            for rule in validation_rules:
                status = "✅" if rule.enabled else "❌"
                print(f"  {status} {rule.name} # {rule.description}")
        else:
            print("  No validation rules found")
        
        print()
        print("Update Rules (urules):")
        if update_rules:
            for rule in update_rules:
                status = "✅" if rule.enabled else "❌"
                print(f"  {status} {rule.name} # {rule.description}")
        else:
            print("  No update rules found")
    
    def _print_detailed_rules(self, validation_rules: List, update_rules: List) -> None:
        """Print detailed information about validation and update rules."""
        print("Validation Rules (vrules):")
        print("=" * 50)
        
        if validation_rules:
            for i, rule in enumerate(validation_rules, 1):
                status = "ENABLED" if rule.enabled else "DISABLED"
                print(f"{i}. {rule.name}")
                print(f"   Status: {status}")
                print(f"   Description: {rule.description}")
                print()
        else:
            print("No validation rules found")
        
        print()
        print("Update Rules (urules):")
        print("=" * 50)
        
        if update_rules:
            for i, rule in enumerate(update_rules, 1):
                status = "ENABLED" if rule.enabled else "DISABLED"
                print(f"{i}. {rule.name}")
                print(f"   Status: {status}")
                print(f"   Description: {rule.description}")
                # Show parameter info for update rules
                if hasattr(rule, 'get_parameter_info'):
                    param_info = rule.get_parameter_info()
                    if param_info:
                        print("   Parameters:")
                        for param, desc in param_info.items():
                            print(f"     {param}: {desc}")
                print()
        else:
            print("No update rules found")
