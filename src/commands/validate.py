"""
Validate command for Lightburn CLI.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from ._base import BaseCommand
from lightburn_file import LightburnFile
from validation_loader import ValidationLoader


class ValidateCommand(BaseCommand):
    """Command to validate .lbrn2 files against rules."""
    
    def add_parser(self, subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Add the validate command parser."""
        parser = subparsers.add_parser(
            "validate",
            help="Validate a .lbrn2 file"
        )
        parser.add_argument(
            "file",
            help="Path to .lbrn2 file to validate"
        )
        parser.add_argument(
            "--rules",
            help="Path to rules file (default: ~/.lightburn_cli/rules or all rules if not found)"
        )
        parser.add_argument(
            "--config",
            help="Path to custom variables file (default: ~/.lightburn_cli/variables.json)"
        )
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)"
        )
        return parser
    
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the validate command."""
        # Check if file exists
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        
        if not file_path.suffix.lower() == ".lbrn2":
            print(f"Error: Expected .lbrn2 file, got '{file_path.suffix}'", file=sys.stderr)
            sys.exit(1)
        
        # Initialize rule loader
        rules_dir = "vrules"  # Default rules directory
        custom_variables_path = None
        
        if args.rules:
            # If custom rules file specified, use its directory
            rules_dir = Path(args.rules).parent
        
        if args.config:
            custom_variables_path = args.config
        
        rule_loader = ValidationLoader(rules_dir, custom_variables_path)
        
        # Load Lightburn file and validate
        try:
            lightburn_file = LightburnFile(file_path)
            results = self.validate_file(lightburn_file, rule_loader, file_path)
        except Exception as e:
            results = [{
                "rule_name": "file_parsing",
                "passed": False,
                "error": f"Failed to parse file: {e}",
                "suggestion": "Ensure the file is a valid .lbrn2 file"
            }]
        
        # Format and output results
        if args.format == "json":
            print(self._format_results_json(results))
        else:
            print(self._format_results_text(results))
        
        # Exit with error code if any validation failed
        failed_count = sum(1 for r in results if not r["passed"])
        if failed_count > 0:
            sys.exit(1)
    
    def validate_file(self, lightburn_file: LightburnFile, rule_loader: ValidationLoader, file_path: Path) -> List[Dict[str, Any]]:
        """
        Validate a LightburnFile against all loaded rules.
        
        Args:
            lightburn_file: Parsed LightburnFile object
            rule_loader: Rule loader instance
            file_path: Path to the original file
            
        Returns:
            List of validation results as dictionaries
        """
        rules = rule_loader.load_all_rules()
        results = []
        
        for rule in rules:
            if not rule.enabled:
                continue
                
            try:
                result = rule.validate(lightburn_file, file_path)
                # Handle rules that return multiple ValidationResult objects
                if isinstance(result, list):
                    for r in result:
                        results.append(r.to_dict())
                else:
                    results.append(result.to_dict())
            except Exception as e:
                results.append({
                    "rule_name": rule.name,
                    "passed": False,
                    "error": f"Rule execution failed: {e}",
                    "suggestion": "Check rule implementation for errors"
                })
        
        return results
    
    def _format_results_text(self, results: List[Dict[str, Any]]) -> str:
        """Format validation results as plain text."""
        output = []
        
        if not results:
            output.append("✅ All validations passed!")
            return "\n".join(output)
        
        failed_count = sum(1 for r in results if not r["passed"])
        passed_count = len(results) - failed_count
        
        output.append(f"Validation Results: {passed_count} passed, {failed_count} failed\n")
        
        for result in results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            output.append(f"{status}: {result['rule_name']}")
            
            if not result["passed"]:
                output.append(f"   Error: {result['error']}")
                if result.get("suggestion"):
                    output.append(f"   Suggestion: {result['suggestion']}")
            output.append("")
        
        return "\n".join(output)
    
    def _format_results_json(self, results: List[Dict[str, Any]]) -> str:
        """Format validation results as JSON."""
        return json.dumps({
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r["passed"]),
                "failed": sum(1 for r in results if not r["passed"])
            },
            "results": results
        }, indent=2)
