"""
Lightburn file class that wraps XML parsing with helper methods for easy access in rules.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Union, Any


class LightburnLayer:
    """Represents a Layer element with helper methods for accessing child values."""
    
    def __init__(self, element: ET.Element):
        """Initialize Layer wrapper from XML element."""
        self.element = element
    
    def _get_value(self, child_name: str) -> Optional[str]:
        """Get Value attribute from a child element."""
        child = self.element.find(child_name)
        if child is not None:
            return child.get("Value")
        return None

    def _get_bool(self, child_name: str, truevalue: Optional[str], falsevalue: Optional[str]) -> bool:
        """Get Value attribute from a child element."""
        #print(f"_get_bool({child_name}, {truevalue}, {falsevalue})")

        child = self.element.find(child_name)
        #print(f"{child}")
        if child is None:
            if truevalue is None:
                return True
            elif falsevalue is None:
                return False
            else:
                return False
        else:
            if child.get("Value") == truevalue:
                return True
            elif child.get("Value") == falsevalue:
                return False
            else:
                return False

    def _set_bool(self, child_name: str, value: bool, truevalue: Optional[str], falsevalue: Optional[str]) -> None:
        """Set Value attribute on a child element."""
        #print(f"_set_bool({child_name}, {value})")
        #print(f"Before setting {child_name} to {value}: {ET.tostring(self.element, encoding='utf-8').decode('utf-8')}")

        newvalue = truevalue if value else falsevalue
        child = self.element.find(child_name)

        if newvalue is None:
            if child is None:
                pass
            else:
                self.element.remove(child)
        else:
            if child is None:
                child = ET.Element(child_name, {"Value": newvalue})
                self.element.append(child)
            else:
                child.set("Value", newvalue)

        #print(f"After setting {child_name} to {value}: {ET.tostring(self.element, encoding='utf-8').decode('utf-8')}")
        
    def _set_value(self, child_name: str, value: str) -> None:
        """Set Value attribute on a child element."""
        child = self.element.find(child_name)
        if child is not None:
            child.set("Value", value)
        else:
            # Create the child element if it doesn't exist
            child = ET.Element(child_name, {"Value": value})
            self.element.append(child)
    
    def _get_path(self) -> str:
        """Get XPath-like path to this Layer."""
        # For Layer, we could include name or type in path
        name = self.element.get("name", "unnamed")
        return f"Layer[{name}]"

    def get_type(self) -> str:
        return self.element.get("type", "unknown")

    def get_speed(self) -> str:
        return self._get_value("speed")
    def set_speed(self, value: str) -> str:
        return self._set_value("speed", value)

    def get_max_power(self) -> str:
        return self._get_value("maxPower")
    def set_max_power(self, value: str) -> str:
        self._set_value("maxPower2", value)
        return self._set_value("maxPower", value)

    def get_min_power(self) -> str:
        return self._get_value("minPower")
    def set_min_power(self, value: str) -> str:
        return self._set_value("minPower", value)

    def set_power(self, value: str) -> str:
        self.set_min_power(value)
        return self.set_max_power(value)

    def get_name(self) -> str:
        return self._get_value("name")
    def set_name(self, value: str) -> None:
        return self._set_value("name", value)

    def get_subname(self) -> str:
        return self._get_value("subname")
    def set_subname(self, value: str) -> None:
        return self._set_value("subname", value)
    def get_tags(self):
        tags = []
        for part in self.get_subname().split(" "):
            if part.startswith("#"):
                tags.append(part)
        return tags

    def get_priority(self) -> str:
        return self._get_value("priority")
    def set_priority(self, value: str) -> None:
        return self._set_value("priority", value)

    def get_index(self) -> str:
        return self._get_value("index")
    def set_index(self, value: str) -> None:
        return self._set_value("index", value)

    def _get_run_blower(self) -> bool:
        return not self._get_bool("runBlower", "0", None)
    def _set_run_blower(self, value: bool) -> bool:
        return self._set_bool("runBlower", not value, "0")
    def blower_on(self) -> None:
        self._set_run_blower(True)
    def blower_off(self) -> None:
        self._set_run_blower(False)
    def blower(self) -> bool:
        return self.get_run_blower()

    def _get_hide(self) -> bool:
        return self._get_bool("hide", None, "1")
    def _set_hide(self, value: bool) -> bool:
        return self._set_bool("hide", value, None, "1")
    def hide(self) -> None:
        self._set_hide(True)
    def show(self) -> None:
        self._set_hide(False)
    def is_hidden(self) -> bool:
        return self._get_hide()

    def _get_do_output(self) -> bool:
        return not self._get_bool("doOutput", "0", None)
    def _set_do_output(self, value: bool) -> None:
        self._set_bool("doOutput", False, "0", None)
    def enable(self) -> None:
        self._set_do_output(True)
    def disable(self) -> None:
        self._set_do_output(False)
    def is_enabled(self) -> bool:
        return self._get_do_output()

class LightburnFile:
    """
    Wrapper class for Lightburn .lbrn2 files with helper methods for easier access in validation rules.
    Stores the original file path and parsed XML root element separately.
    """
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize wrapper from a Lightburn .lbrn2 file path.
        
        Args:
            file_path: Path to the .lbrn2 file
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Lightburn file not found: {self.file_path}")
        
        if not self.file_path.suffix.lower() == ".lbrn2":
            raise ValueError(f"Expected .lbrn2 file, got {self.file_path.suffix}")
        
        try:
            # Parse the XML file and store the root element
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
                
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format in Lightburn file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse Lightburn file: {e}")
    
    def get_layers(self, 
                     cut_type: Optional[str] = None,
                     index: Optional[int] = None,
                     name: Optional[str] = None,
                     subname: Optional[str] = None) -> List[LightburnLayer]:
        """
        Get Layer elements from the file with optional filtering parameters.
        
        Args:
            cut_type: Filter by Layer type (e.g., 'Cut', 'Fill')
            index: Filter by Layer index (0-based)
            name: Filter by Layer name attribute
            subname: Filter by subname content (partial match)
            
        Returns:
            List of LightburnLayer objects matching the criteria
        """
        # Find all CutSetting elements from LightBurnProject
        cut_setting_elements = self.root.findall(".//CutSetting")
        cut_settings = []
        
        for element in cut_setting_elements:
            cut_setting = LightburnLayer(element)
            
            # Apply filters
            if cut_type is not None:
                if element.get("type") != cut_type:
                    continue
            
            if index is not None:
                # Find index in parent (assuming sequential order)
                parent = element.parent
                siblings = [child for child in parent.findall("CutSetting")]
                try:
                    current_index = siblings.index(element)
                    if current_index != index:
                        continue
                except ValueError:
                    continue
            
            if name is not None:
                if element.get("name") != name:
                    continue
            
            if subname is not None:
                subname_value = cut_setting.get_value("subname")
                if subname_value is None or subname not in subname_value:
                    continue
            
            cut_settings.append(cut_setting)
        
        return cut_settings
    
    def write(self, file_path, encoding='utf-8', xml_declaration=True):
        print(f"Writting: {file_path}")
        self.tree.write(file_path, encoding=encoding, xml_declaration=xml_declaration)
