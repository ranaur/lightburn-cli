# Lightburn CLI

Created: Thu, Mar 26, 2026  3:02:07 PM

A modular CLI tool to validate Lightburn .lbrn2 files against configurable rules.

## Features

- **Modular Rule System**: Add new rules by simply creating Python files in the `vrules/` or `urules/` directory
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

Create a `.py` file in the `vrules/` or `urules/` directory.

## Rule Structure

All rules must inherit from the `ValidationRule` base class and implement the `validate` method. The `validate` method receives:

- `Lightburn_file`: Parsed XML data from the .lbrn2 file as a LightburnFile object

The method should return a list of `ValidationResult` objects with:
- `rule_name`: Name of the rule
- `passed`: Boolean indicating if validation passed
- `error`: Error message (if validation failed)
- `suggestion`: Suggestion for fixing the issue (optional)

