"""
Dynamic rule loading system.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List
from validation_base import ValidationRule

class ValidationLoader:
    """Loads validation rules from vrules directory."""
    
    def __init__(self, rules_dir: str = "vrules", custom_variables_path=None):
        rules_dir = Path(rules_dir)
        if rules_dir.is_absolute():
            self.rules_dir = rules_dir
        else:
            self.rules_dir = Path(__file__).parent / rules_dir
        self.custom_variables_path = custom_variables_path
        self._rules_cache: Optional[List[ValidationRule]] = None
    
    def load_all_rules(self) -> List[ValidationRule]:
        """Load all rules from the rules directory."""
        if self._rules_cache is not None:
            return self._rules_cache
        
        rules = []
        
        if not self.rules_dir.exists():
            print(f"Warning: Rules directory '{self.rules_dir}' not found", file=sys.stderr)
            return rules
        
        # Load Python rule files only
        for py_file in self.rules_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                #print(f"Loading rule from: {py_file.name}")
                rules_from_file = self._load_python_rule(py_file)
                rules.extend(rules_from_file)
            except Exception as e:
                print(f"Warning: Failed to load rule from {py_file}: {e}", file=sys.stderr)
        
        self._rules_cache = rules
        return rules
    
    def _load_python_rule(self, file_path: Path) -> List[ValidationRule]:
        """Load rules from a Python file. Returns a list of rules found."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        rules = []
        
        # Look for all ValidationRule classes or instances
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, ValidationRule) and attr != ValidationRule:
                # Skip abstract classes
                if getattr(attr, '__abstractmethods__', None):
                    continue
                # Check if rule constructor accepts custom_variables_path
                try:
                    rule_instance = attr(custom_variables_path=self.custom_variables_path)
                except TypeError:
                    # Fallback for rules that don't support custom path
                    rule_instance = attr()
                rules.append(rule_instance)
            elif isinstance(attr, ValidationRule):
                rules.append(attr)
        
        if not rules:
            raise ValueError(f"No ValidationRule class or instance found in {file_path}")
        
        return rules
