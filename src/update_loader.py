"""
Dynamic update rule loading system.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List
from update_base import UpdateRule


class UpdateLoader:
    """Loads update rules from urules directory."""
    
    def __init__(self, urules_dir: str = "urules", custom_variables_path=None):
        self.urules_dir = Path(urules_dir)
        self.custom_variables_path = custom_variables_path
        self._update_rules_cache: List[UpdateRule] = None
    
    def load_all_update_rules(self) -> List[UpdateRule]:
        """Load all update rules from the urules directory."""
        if self._update_rules_cache is not None:
            return self._update_rules_cache
        
        update_rules = []
        
        if not self.urules_dir.exists():
            print(f"Warning: Update rules directory '{self.urules_dir}' not found", file=sys.stderr)
            return update_rules
        
        # Load Python update rule files only
        for py_file in self.urules_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                update_rules_from_file = self._load_python_update_rule(py_file)
                update_rules.extend(update_rules_from_file)
            except Exception as e:
                print(f"Warning: Failed to load update rule from {py_file}: {e}", file=sys.stderr)
        
        self._update_rules_cache = update_rules
        return update_rules
    
    def _load_python_update_rule(self, file_path: Path) -> List[UpdateRule]:
        """Load update rules from a Python file. Returns a list of update rules found."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        update_rules = []
        
        # Look for all UpdateRule classes or instances
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, UpdateRule) and attr != UpdateRule:
                # Skip abstract classes
                if getattr(attr, '__abstractmethods__', None):
                    continue
                # Check if update rule constructor accepts custom_variables_path
                try:
                    update_rule_instance = attr(custom_variables_path=self.custom_variables_path)
                except TypeError:
                    # Fallback for update rules that don't support custom path
                    update_rule_instance = attr()
                update_rules.append(update_rule_instance)
            elif isinstance(attr, UpdateRule):
                update_rules.append(attr)
        
        if not update_rules:
            raise ValueError(f"No UpdateRule class or instance found in {file_path}")
        
        return update_rules
