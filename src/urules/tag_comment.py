"""
Update rule for enabling/disabling layers based on #COMMENT tag using LayersUpdateRule.
"""

from update_base import LayersUpdateRule, UpdateResult
import xml.etree.ElementTree as ET

class TagCommentRule(LayersUpdateRule):
    """Update rule to disable layers with #COMMENT tag and enable layers without it."""
    
    def __init__(self, name="tag_comment", description="Disable #COMMENT layers and enable others", enabled=True):
        super().__init__(name, description, enabled)
    
    def validate_parameters(self, **kwargs) -> list:
        """Validate parameters for this update rule."""
        # This rule doesn't require any parameters
        return []
    
    def get_parameter_info(self) -> dict:
        """Get information about required/optional parameters."""
        return {}
    
    def _get_tags_from_subname(self, subname: str) -> list:
        """Extract all #tags from a subname string."""
        tags = []
        for part in subname.split(" "):
            if part.startswith("#"):
                tags.append(part)
        return tags
    
    def update_layer(self, layer, dry_run: bool = False, **kwargs) -> UpdateResult:
        """Update a single layer based on #COMMENT tag."""

        # Get tags from subname
        tags = layer.get_tags()
        has_comment_tag = "#COMMENT" in tags
        
        # Check current enabled/disabled state
        current_disabled = not layer.is_enabled()
        #print(f"Layer: {layer.get_name()} / {layer.get_subname()} {"disabled" if current_disabled else "enabled"}")
        
        if has_comment_tag:
            # Disable layers with #COMMENT tag
            if not current_disabled:
                result = UpdateResult(
                    modified=True,
                    message=f"Disabled layer {layer.get_name()} (has #COMMENT tag)"
                )

                # Apply change if not in dry run mode
                if not dry_run:
                    layer.disable()
                
                # Print what happened
                action = "Would disable" if dry_run else "Disabled"
                print(f"{action} layer '{layer.get_name()}' (has #COMMENT tag)")
                
                return result
        else:
            # Enable layers without #COMMENT tag
            if current_disabled:
                result = UpdateResult(
                    modified=True,
                    message=f"Enabled layer {layer.get_name()} (no #COMMENT tag)"
                )
                
                # Apply change if not in dry run mode
                if not dry_run:
                    layer.enable()
                
                # Print what happened
                action = "Would enable" if dry_run else "Enabled"
                print(f"{action} layer '{layer.get_name()}' (no #COMMENT tag)")
                
                return result
        
        # No changes needed
        return None
