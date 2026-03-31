"""
Base class for update rules.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
from lightburn_file import LightburnFile, LightburnLayer

class UpdateResult:
    """Result of an update operation."""
    
    def __init__(self, modified: bool = False, message: str = ""):
        self.message = message
        self.modified = modified
        self.details: Dict[str, Any] = {}
    
    def add_detail(self, key: str, value: Any) -> None:
        """Add a detail to the result."""
        self.details[key] = value


class UpdateRule(ABC):
    """Base class for all update rules."""
    
    def __init__(self, name: str = None, description: str = "", enabled: bool = True):
        self.name = name or self.__class__.__name__.lower().replace('updaterule', '')
        self.description = description
        self.enabled = enabled
    
    @abstractmethod
    def update(self, lightburn_file: LightburnFile, file_path: Path, dry_run: bool = False, **kwargs) -> UpdateResult:
        """
        Apply the update rule to the specified file.
        """
        pass
    
    def validate_parameters(self, **kwargs) -> List[str]:
        """
        Validate parameters for this update rule.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            List of error messages, empty if valid
        """
        return []
    
    def get_parameter_info(self) -> Dict[str, str]:
        """
        Get information about required/optional parameters.
        
        Returns:
            Dictionary mapping parameter names to descriptions
        """
        return {}


class LayersUpdateRule(UpdateRule, ABC):
    """Abstract base class for Layers update rules."""
    
    def update(self, lightburn_file: LightburnFile, file_path: Path, dry_run: bool = False, **kwargs) -> UpdateResult:
        """
        Apply the update rule to all Layer elements in the file.
        """
        # Find all Layer elements using the new method
        layers = lightburn_file.get_layers()
        
        layers_updated = 0
        layers_total = len(layers)
        results = []

        for layer in layers:
            result = self.update_layer(layer, dry_run=dry_run, **kwargs)
            if result:
                results.append(result)
                if result.modified:
                    layers_updated += 1

        if layers_updated > 0:
            message = f"Updated {layers_updated} layer(s) out of {layers_total}"
        else:
            message = f"No changes needed for {layers_total} layer(s)"
        
        update_result = UpdateResult(
            message=message,
            modified=layers_updated > 0
        )
        update_result.add_detail("layers_updated", layers_updated)
        update_result.add_detail("layers_total", layers_total)
        update_result.add_detail("individual_results", results)
        
        return update_result
    
    @abstractmethod
    def update_layer(self, layer: LightburnLayer, dry_run: bool = False, **kwargs) -> Optional['UpdateResult']:
        """
        Update a single Layer element.
        
        Args:
            layer: LightburnLayer instance to update
            dry_run: If True, show what would change without modifying
            **kwargs: Additional parameters specific to the update rule
            
        Returns:
            UpdateResult if layer was updated, None if no changes needed
        """
        pass

