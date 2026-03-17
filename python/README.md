# AIEDL Python Implementation

Python library for parsing, validating, and building AIEDL files.

## Installation

```bash
# From the aiedl directory
pip install -e python/
```

Or add to your Python path:

```python
import sys
sys.path.append('path/to/aiedl/python')
```

## Usage

### Parsing

```python
from aiedl.python import parse_edl_with_ai

edits = parse_edl_with_ai('sample.ai.edl')

for edit in edits:
    print(f"Edit {edit['edit_number']}: {edit['track']} {edit['operation']}")
    if 'description' in edit['metadata']:
        print(f"  Description: {edit['metadata']['description']}")
```

### Building

```python
from aiedl.python import AIEDLBuilder

builder = AIEDLBuilder('output.ai.edl', 'My Movie', fps=24)

# Add a video cut
builder.add_video_cut(
    '00:00:00:00', '00:00:05:00',
    '00:00:10:00', '00:00:15:00',
    clip_name='Scene1'
)

# Add a video inpaint
builder.add_video_inpaint(
    '00:00:12:00', '00:00:14:00',
    region={'x1': 0.1, 'y1': 0.2, 'x2': 0.3, 'y2': 0.4},
    action='REMOVE_OBJECT',
    target='Remove unwanted object',
    strength=0.8
)

# For reproducible generative output in AIEDL files, include:
# * SEED: 123456789

# Add an audio mute
builder.add_audio_mute(
    '00:01:10:12', '00:01:12:05',
    '00:01:10:12', '00:01:12:05',
    description='Mute profanity',
    channel=2  # Optional
)

# Add a caption replace
builder.add_caption_replace(
    '00:03:00:00', '00:03:05:00',
    '00:03:00:00', '00:03:05:00',
    original_text='"What the hell?"',
    replacement='"What?"',
    description='Remove profanity from captions'
)
```

### Validation

```python
from aiedl.python import validate_file

is_valid, errors, warnings = validate_file('sample.ai.edl', strict=True)

if not is_valid:
    for error in errors:
        print(f"Error: {error}")
else:
    print("File is valid!")
    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")
```

### Command Line Tools

#### Validator

```bash
python -m aiedl.python.validator sample.ai.edl
```

## Testing

Run the test suite:

```bash
python -m pytest python/test_parser.py -v
```

## API Reference

### `parse_edl_with_ai(filename: str) -> List[Dict]`

Parse an AIEDL file and return a list of edit dictionaries.

### `AIEDLBuilder(output_file: str, title: str, fps: float = 24, ai_version: str = "1.0")`

Builder class for creating AIEDL files programmatically.

### `validate_file(filename: str, strict: bool = True) -> Tuple[bool, List[ValidationError], List[str]]`

Validate an AIEDL file. Returns (is_valid, errors, warnings).

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

