"""
Example of a custom Python rule for more complex validations.
"""

from validation_base import ValidationRule, ValidationResult
from lightburn_file import LightburnFile
from pathlib import Path

class ShapeCountRule(ValidationRule):
    """Validates the total number of shapes in the file."""
    
    def __init__(self):
        super().__init__(
            name="shape_count_validation",
            description="Checks if the total number of shapes is within reasonable limits",
            enabled=True
        )
    
    def validate(self, xml_root: LightburnFile, file_path: Path) -> ValidationResult:
        """Count all shapes in the file."""
        
        # Find all Shape elements
        shapes = xml_root.find_all("Shape")
        total_shapes = len(shapes)
        
        # Allow up to 1000 shapes
        if total_shapes > 1000:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                error=f"Too many shapes: {total_shapes} (max: 1000)",
                suggestion="Consider splitting the design into multiple files or reducing complexity"
            )
        
        return ValidationResult(
            rule_name=self.name,
            passed=True
        )
