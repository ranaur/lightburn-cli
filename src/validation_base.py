"""
Base classes for validation rules.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pathlib import Path
from lightburn_file import LightburnFile, LightburnLayer

class ValidationResult:
    """Represents the result of a rule validation."""
    
    def __init__(
        self,
        rule_name: str,
        passed: bool,
        error: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        self.rule_name = rule_name
        self.passed = passed
        self.error = error
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "rule_name": self.rule_name,
            "passed": self.passed,
            "error": self.error,
            "suggestion": self.suggestion
        }

class ValidationRule(ABC):
    """Base class for all validation rules."""
    
    def __init__(self, name: str, description: str, enabled: bool = True):
        self.name = name
        self.description = description
        self.enabled = enabled
    
    @abstractmethod
    def validate(self, lightburn_file: LightburnFile, file_path: Path) -> ValidationResult:
        """
        Validate the given XML data against this rule.
        
        Args:
            xml_root: Parsed .lbrn2 file as LightburnFile object
            file_path: Path to the original file
            
        Returns:
            ValidationResult with the validation outcome
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

class LayersValidationRule(ValidationRule, ABC):
    """Abstract base class for Layers validation rules."""
    
    def validate(self, lightburn_file: LightburnFile, file_path: Path) -> List[ValidationResult]:
        results = []
        
        # Find all Layer elements using the new method
        layers = lightburn_file.get_layers()
        
        for layer in layers:
            result = self.validate_setting(layer)
            if result:
                results.append(result)
        
        # If no issues found, return a single passed result
        if not results:
            return [ValidationResult(
                rule_name=self.name,
                passed=True
            )]
        
        return results
    
    @abstractmethod
    def validate_setting(self, setting: LightburnLayer) -> ValidationResult:
        """Validate a single Layer element."""
        pass
