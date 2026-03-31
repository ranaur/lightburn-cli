"""
Example update rule for setting layer power using LayersUpdateRule.
"""
from update_base import LayersUpdateRule, UpdateResult

class SetPowerRule(LayersUpdateRule):
    """Update rule to set power for all layers or specific layers."""
    
    def __init__(self, name="set_power", description="Set power for layers", enabled=True):
        super().__init__(name, description, enabled)
    
    def validate_parameters(self, **kwargs) -> list:
        """Validate parameters for this update rule."""
        errors = []
        
        if "power" not in kwargs:
            errors.append("Required parameter 'power' is missing")
        else:
            try:
                power_value = int(kwargs["power"])
                if power_value < 0 or power_value > 100:
                    errors.append("Power must be between 0 and 100")
            except ValueError:
                errors.append("Power must be a numeric value")
        
        if "layer_name" in kwargs and not kwargs["layer_name"].strip():
            errors.append("Layer name cannot be empty")
        
        return errors
    
    def get_parameter_info(self) -> dict:
        """Get information about required/optional parameters."""
        return {
            "power": "Required: Power value (0-100)",
            "layer_name": "Optional: Name of specific layer to update (updates all layers if not specified)"
        }
    
    def update_layer(self, layer, dry_run: bool = False, **kwargs) -> UpdateResult:
        """Update power for a single layer."""
        power = kwargs.get("power")
        layer_name = kwargs.get("layer_name")
        
        if power is None:
            return UpdateResult(False, "Power parameter is required")
        
        try:
            power_value = int(power)
        except ValueError:
            return UpdateResult(False, "Invalid power value")
        
        if power_value < 0 or power_value > 100:
            return UpdateResult(False, "Power value must be between 0 and 100")
        
        # Get layer information
        current_name = layer.get_name()
        current_power = layer.get_max_power()
        
        # Check if this layer should be updated
        if layer_name is not None and current_name != layer_name:
            return None
        
        # Check if layer has power attribute
        if current_power is None:
            return None
        
        # Check if power needs to be changed
        if float(current_power) == power_value:
            return None
        
        # Create update result
        result = UpdateResult(
            modified=True,
            message=f"Power changed from {current_power} to {power_value}"
        )
        result.add_detail("power", power_value)
        
        # Apply the change if not in dry run mode
        if not dry_run:
            layer.set_power(power_value)
        
        # Print what happened
        action = "Would update" if dry_run else "Updated"
        print(f"{action} layer '{current_name}': power {current_power} -> {power_value}")
        
        return result
