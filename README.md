# Lightburn CLI

Created: Thu, Mar 26, 2026  3:02:07 PM

A modular CLI tool to validate Lightburn .lbrn2 files against configurable rules.

## Features

- **Modular Rule System**: Add new rules by simply creating Python files in the `rules/` directory
- **Python Rules**: Support complex custom validation logic with full programming flexibility
- **CLI Interface**: Command-line tool with simple syntax
- **Extensible**: Easy to add custom validation logic

## Installation

```bash
pip install -e .
```

## Usage

### Validate a file
```bash
python main.py validate file.lbrn2
```

### Validate with custom rules file
```bash
python main.py validate file.lbrn2 --rules /path/to/rules
```

### List available rules
```bash
python main.py rules
```

## Syntax

```
lightburn-cli command [parameters]

Where command is:

validate file.lbrn2 [--rules rules-file]
    Validates file.lbrn2 against all rules in the rules file, or only in the rules specified in the rules file.

    The rule file defines which rules to be applied to the file. (default is to read from ~/.lightburn_cli/rules or all rules if it does not exist)

    The rule file is a text file that defines the rules to be applied to the file. One for each line (ignore blank lines and lines starting with #).

rules
    Lists available rules names and a short description. Show as:

    rule_name # Rule description ...
```

## Adding New Rules

### Python Rules

Create a `.py` file in the `rules/` directory:

```python
from rule_base import Rule, ValidationResult
from lightburn_file import LightburnFile
from pathlib import Path

class MyCustomRule(Rule):
    def __init__(self):
        super().__init__(
            name="my_custom_rule",
            description="Custom validation logic",
            enabled=True
        )
    
    def validate(self, xml_root: LightburnFile, file_path: Path) -> ValidationResult:
        # Your validation logic here using xml_root methods
        # Example: Find all Shapes elements
        cut_settings = xml_root.find_all("Shapes")
        
        return ValidationResult(
            rule_name=self.name,
            passed=True  # or False with error/suggestion
        )
```

## Rule Structure

All rules must inherit from the `Rule` base class and implement the `validate` method. The `validate` method receives:

- `xml_root`: Parsed XML data from the .lbrn2 file as a LightburnFile object
- `file_path`: Path to the original file

The method should return a `ValidationResult` with:
- `rule_name`: Name of the rule
- `passed`: Boolean indicating if validation passed
- `error`: Error message (if validation failed)
- `suggestion`: Suggestion for fixing the issue (optional)

## Project Structure

```
lightburn-cli/
├── main.py              # CLI entry point
├── lightburn_file.py      # Lightburn file wrapper with helper methods
├── rule_base.py          # Base classes for rules
├── rule_loader.py        # Dynamic rule loading
├── material_manager.py  # Material variables management
├── commands/             # Command modules
│   ├── __init__.py
│   ├── _base.py          # Base command class
│   ├── _discovery.py     # Command discovery utility
│   ├── validate.py       # Validate command
│   ├── rules.py          # Rules command
│   └── material.py       # Material command
├── requirements.txt      # Dependencies
├── pyproject.toml        # Project configuration
├── rules/                # Rules directory
│   └── custom_example.py # Python rule example
└── README.md
```

