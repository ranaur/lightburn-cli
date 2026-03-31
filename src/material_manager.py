import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

def get_variable(key: str, custom_path=None) -> Optional[Any]:
    """Get a specific variable by key."""
    vars_manager = MaterialManager(custom_path)
    return vars_manager.get_variable(key)

class MaterialManager:
    """Manages material variables stored in a JSON file."""
    
    def __init__(self, custom_path=None):
        if custom_path:
            self.config_dir = Path(custom_path).parent
            self.variables_file = Path(custom_path)
        else:
            # Check for LIGHTBURN_VARIABLES environment variable
            env_path = os.environ.get("LIGHTBURN_VARIABLES")
            if env_path:
                self.config_dir = Path(env_path).parent
                self.variables_file = Path(env_path)
            else:
                # Use default path
                self.config_dir = Path.home() / ".lightburn_cli"
                self.variables_file = self.config_dir / "variables.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_variables(self) -> Dict[str, Any]:
        """Load variables from the JSON file."""
        if not self.variables_file.exists():
            return {}
        
        try:
            with open(self.variables_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_variables(self, variables: Dict[str, Any]):
        """Save variables to the JSON file."""
        try:
            with open(self.variables_file, 'w', encoding='utf-8') as f:
                json.dump(variables, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save variables: {e}")
    
    def list_variables(self) -> Dict[str, Any]:
        """List all variables."""
        return self._load_variables()
    
    def get_variable(self, key: str) -> Optional[Any]:
        """Get a specific variable by key."""
        variables = self._load_variables()
        return variables.get(key)
    
    def set_variable(self, key: str, value: Any):
        """Set a variable value."""
        variables = self._load_variables()
        variables[key] = value
        self._save_variables(variables)
    
    def delete_variable(self, key: str) -> bool:
        """Delete a variable by key. Returns True if deleted, False if not found."""
        variables = self._load_variables()
        if key in variables:
            del variables[key]
            self._save_variables(variables)
            return True
        return False
    
    def clear_variables(self):
        """Clear all variables."""
        if self.variables_file.exists():
            self.variables_file.unlink()
