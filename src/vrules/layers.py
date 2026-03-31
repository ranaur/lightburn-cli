"""
Validation rules for Layers elements.
"""

from validation_base import ValidationResult, LayersValidationRule
from lightburn_file import LightburnLayer
from material_manager import get_variable

class LayersSubnameRule(LayersValidationRule):
    """Validates that all Layers elements have subnames."""
    
    def __init__(self, name="layers_subname",
            description="Ensures every Layers element have a subname",
            enabled=True, custom_variables_path=None):
        super().__init__(name, description, enabled)
        self.custom_variables_path = custom_variables_path
    
    def validate_setting(self, setting: LightburnLayer) -> ValidationResult:
        """Check a single Layers element for subname tag."""
        # Get name element for identification
        name = setting.get_name()
        if name is None:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                error="Layers missing required 'name' element with 'Value' attribute",
                suggestion="Recreate the file in Lightburn software. It is probably corrupted."
            )

        subname = setting.get_subname()
        # If no subname found, return a ValidationResult for this specific Layers
        if subname is None:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                error=f"Layers {name} has no Subname",
                suggestion=f"Add subname with a valid #tag to Layers '{name}'"
            )
        
        # Get all #tags in the subname
        tags = setting.get_tags()

        # Ensure that there is a #TAG in the subname
        if len(tags) == 0:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                error=f"Layers {name} with subname {subname} must have a #TAG",
                suggestion=f"Add a valid #tag to Layers '{name}'"
            )

        # Validate that all #tags are valid
        valid_tags = {"#CUT", "#ENGRAVE", "#COMMENT"}

        for tag in tags:
            if tag.upper() not in valid_tags:
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"Layers {name} has an invalid #TAG '{tag}'",
                    suggestion=f"Adjust the #tag in Layers '{name}' to one of: {', '.join(valid_tags)}"
                )

        # All Right, no issue
        return None

class LayersPowerRule(LayersValidationRule):
    """Validates power settings for Layers elements."""
    
    def __init__(self, name="layers_power",
            description="Ensures Layers power matches material variables",
            enabled=True, custom_variables_path=None):
        super().__init__(name, description, enabled)
        self.custom_variables_path = custom_variables_path
    
    def validate_setting(self, setting: LightburnLayer) -> ValidationResult:
        """Validate power settings for a single Layers element."""
        name = setting.get_name()
        if name is None:
            return None  # Skip if no name
        
        cut_type = setting.get_type()
        if cut_type == "Cut":
            return self._validate_cut_power(setting, name)
        elif cut_type == "Engrave":
            return self._validate_engrave_power(setting, name)
        
        return None
    
    def _validate_cut_power(self, setting: LightburnLayer, name: str) -> ValidationResult:
        """Validate Cut type power settings."""
        cut_power = get_variable("cut.power", self.custom_variables_path)
        if cut_power is not None:
            if int(setting.get_min_power()) != int(engrave_power):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"minPower does not match cut.power",
                    suggestion=f"Adjusts minPower value of Layers '{name}' from {setting.get_min_power()} to {cut_power}"
                )
            if int(setting.get_max_power()) != int(engrave_power):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"maxPower does not match cut.power",
                    suggestion=f"Adjusts maxPower values of Layers '{name}' from {setting.get_max_power()}  to {cut_power}"
                )
        
        # Validate speed
        speed = get_variable("cut.speed", self.custom_variables_path)
        if speed is not None:
            if int(setting.get_speed()) != int(speed):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"Layers {name} must have speed equal to variable speed",
                    suggestion=f"Adjusts speed value of Layers '{name}' from {setting.get_speed()}  to {cut_power}"
                )
        
        return None
    
    def _validate_engrave_power(self, setting: LightburnLayer, name: str) -> ValidationResult:
        """Validate Engrave type power settings."""
        engrave_power = get_variable("engrave.power", self.custom_variables_path)
        if engrave_power is not None:
            if int(setting.get_min_power()) != int(engrave_power):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"minPower does not match engrave.power",
                    suggestion=f"Adjusts minPower value of Layers '{name}' from {setting.get_min_power()} to {engrave_power}"
                )
            if int(setting.get_max_power()) != int(engrave_power):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"maxPower does not match engrave.power",
                    suggestion=f"Adjusts maxPower values of Layers '{name}' from {setting.get_max_power()}  to {engrave_power}"
                )
        
        # Validate speed
        speed = get_variable("engrave.speed", self.custom_variables_path)
        if speed is not None:
            if int(setting.get_speed()) != int(speed):
                return ValidationResult(
                    rule_name=self.name,
                    passed=False,
                    error=f"Layers {name} must have speed equal to variable engrave.speed",
                    suggestion=f"Adjusts speed value of Layers '{name}' to {engrave_power}"
                )
        
        return None
