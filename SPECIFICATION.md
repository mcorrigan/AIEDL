# AIEDL (AI Edit Decision List) Specification

## Overview

AIEDL is an extended Edit Decision List (EDL) format designed to support AI-powered video, audio, and caption editing operations. It builds upon traditional EDL formats by adding support for AI-specific operations like inpainting, object removal, and intelligent content modification.

## File Structure

An AIEDL file consists of:

1. **Header Section**: Metadata about the file
2. **Edit Entries**: Individual edit operations with their parameters

### Header Format

```
TITLE: <Project Title>
FPS: <Frame Rate>
AI_VERSION: <Version Number>
```

- **TITLE**: Name of the project or movie
- **FPS**: Frame rate (typically 24, 25, 29.97, or 30)
- **AI_VERSION**: Version of the AIEDL specification (currently 1.0)

## Edit Entry Format

Each edit entry follows this structure:

```
<EDIT_NUMBER>  <REEL>  <TRACK>  <OPERATION>  <SOURCE_IN>  <SOURCE_OUT>  <RECORD_IN>  <RECORD_OUT>
* <METADATA_FIELD>: <value>
* <METADATA_FIELD>: <value>
...
```

### Edit Line Components

- **EDIT_NUMBER**: 3-digit sequence number (001, 002, 003, etc.)
- **REEL**: Reel/type identifier
  - `AX`: Standard audio/video edit
  - `AI`: AI-powered edit operation
- **TRACK**: Track type identifier
  - `V`: Video track
  - `A1`, `A2`, etc.: Audio tracks (A1 = first audio track)
  - `S`: Subtitle/Caption track
- **OPERATION**: The type of edit operation (see Operations section)
- **SOURCE_IN**: Source material in point (HH:MM:SS:FF)
- **SOURCE_OUT**: Source material out point (HH:MM:SS:FF)
- **RECORD_IN**: Record timeline in point (HH:MM:SS:FF)
- **RECORD_OUT**: Record timeline out point (HH:MM:SS:FF)

### Timecode Format

Timecodes use the format: `HH:MM:SS:FF`
- **HH**: Hours (00-23)
- **MM**: Minutes (00-59)
- **SS**: Seconds (00-59)
- **FF**: Frames (00-23 for 24fps, 00-29 for 30fps)

## Track Types

### Video Track (V)

Video tracks support visual editing operations:
- Standard cuts and edits
- AI-powered inpainting
- Object manipulation
- Color correction

### Audio Track (A1, A2, ...)

Audio tracks support sound editing operations:
- Muting specific time ranges
- Replacing audio segments
- Channel-specific operations

### Caption/Subtitle Track (S)

Caption tracks support text editing operations:
- Replacing profanity or inappropriate text
- Modifying caption content
- Hiding captions during specific time ranges
- Text substitution

## Operations

### Video Operations

#### C (Cut)
Standard video cut/edit operation.

```
001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
* FROM CLIP NAME: Scene1
```

#### INPAINT
AI-powered inpainting operation for video manipulation.

```
002  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4)
* ACTION: REMOVE_OBJECT
* TARGET: Make the chair green
* STRENGTH: 0.8
* MODEL: stable-diffusion-v2
* SEED: 123456789
```

**Metadata Fields:**
- `REGION`: Tuple defining the region as percentages (x1, y1, x2, y2)
- `ACTION`: Type of inpainting action
  - `REMOVE_OBJECT`: Remove an object from the scene
  - `ADD_OBJECT`: Add an object to the scene
  - `REPLACE_OBJECT`: Replace an object with another
  - `ADD_COLOR`: Add or modify colors
  - `RESTORE`: Restore damaged/missing content
- `TARGET`: Description of what to achieve
- `STRENGTH`: Strength/intensity of the operation (0.0 to 1.0)
- `MODEL`: (Optional) AI model identifier to use for this edit (e.g., "stable-diffusion-v2", "dall-e-3", "custom-model-v1")
- `SEED`: (Optional) Integer seed for best-effort repeatability of generative AI results. Use the same `MODEL`, `TARGET`, `STRENGTH`, and `SEED` to improve reproducibility across runs.

### Audio Operations

#### MUTE
Mute audio during a specific time range.

```
004  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* DESCRIPTION: Mute profanity in dialogue ("explicit word").
* CHANNEL: 2  # Optional: specific audio channel
```

**Metadata Fields:**
- `DESCRIPTION`: Human-readable description of why the mute is applied
- `CHANNEL`: (Optional) Specific audio channel number (1, 2, etc.)

#### REPLACE
Replace audio with alternative content.

```
005  AX       A1    REPLACE  00:02:15:08 00:02:16:20 00:02:15:08 00:02:16:20
* REPLACEMENT: "[CENSORED]"
* DESCRIPTION: Replace explicit word with "CENSORED".
```

**Metadata Fields:**
- `REPLACEMENT`: The replacement audio content or description
- `DESCRIPTION`: Explanation of the replacement

### Caption Operations

#### REPLACE
Replace caption text with alternative text.

```
007  AX       S     REPLACE  00:03:00:00 00:03:05:00 00:03:00:00 00:03:05:00
* ORIGINAL_TEXT: "What the hell are you doing?"
* REPLACEMENT: "What are you doing?"
* DESCRIPTION: Replace profanity in captions with clean text.
```

**Metadata Fields:**
- `ORIGINAL_TEXT`: The original caption text to be replaced
- `REPLACEMENT`: The replacement text
- `DESCRIPTION`: Explanation of the change

#### MUTE
Hide captions during a specific time range (no subtitles displayed).

```
009  AX       S     MUTE     00:05:20:00 00:05:22:00 00:05:20:00 00:05:22:00
* DESCRIPTION: Hide captions during this time period.
```

**Metadata Fields:**
- `DESCRIPTION`: Explanation of why captions are hidden

#### MODIFY
Modify caption text to be more appropriate or accurate.

```
010  AX       S     MODIFY   00:06:15:00 00:06:18:00 00:06:15:00 00:06:18:00
* ORIGINAL_TEXT: "He said a bad word"
* REPLACEMENT: "He said something inappropriate"
* DESCRIPTION: Modify caption text to be more appropriate.
```

**Metadata Fields:**
- `ORIGINAL_TEXT`: The original caption text
- `REPLACEMENT`: The modified text
- `DESCRIPTION`: Explanation of the modification

## Complete Example

```edl
TITLE: AI Edited Movie
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
* FROM CLIP NAME: Scene1

002  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4)
* ACTION: REMOVE_OBJECT
* TARGET: Make the chair green
* STRENGTH: 0.8
* MODEL: stable-diffusion-v2
* SEED: 123456789

003  AI       V     INPAINT  00:00:20:00 00:00:22:00
* REGION: (x1:.5, y1:.6, x2:.7, y2:.8)
* ACTION: ADD_OBJECT
* TARGET: Maple tree with fall colored leaves
* STRENGTH: 0.5
* MODEL: dall-e-3
* SEED: 424242

004  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* DESCRIPTION: Mute profanity in dialogue ("explicit word").

005  AX       A1    REPLACE  00:02:15:08 00:02:16:20 00:02:15:08 00:02:16:20
* REPLACEMENT: "[CENSORED]"
* DESCRIPTION: Replace explicit word with "CENSORED".

006  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* CHANNEL: 2
* DESCRIPTION: Mute explicit dialogue in channel 2 only.

007  AX       S     REPLACE  00:03:00:00 00:03:05:00 00:03:00:00 00:03:05:00
* ORIGINAL_TEXT: "What the hell are you doing?"
* REPLACEMENT: "What are you doing?"
* DESCRIPTION: Replace profanity in captions with clean text.

008  AX       S     REPLACE  00:04:10:12 00:04:12:05 00:04:10:12 00:04:12:05
* ORIGINAL_TEXT: "explicit word"
* REPLACEMENT: "[CENSORED]"
* DESCRIPTION: Replace explicit word in captions with "[CENSORED]".

009  AX       S     MUTE     00:05:20:00 00:05:22:00 00:05:20:00 00:05:22:00
* DESCRIPTION: Hide captions during this time period.

010  AX       S     MODIFY   00:06:15:00 00:06:18:00 00:06:15:00 00:06:18:00
* ORIGINAL_TEXT: "He said a bad word"
* REPLACEMENT: "He said something inappropriate"
* DESCRIPTION: Modify caption text to be more appropriate.
```

## Parser Usage

The AIEDL parser (`parser.py`) can be used to parse AIEDL files:

```python
from aiedl.parser import parse_edl_with_ai

# Parse an AIEDL file
edits = parse_edl_with_ai('sample.ai.edl')

# Each edit is a dictionary containing:
# - edit_number: String (e.g., "001")
# - reel: String (e.g., "AX", "AI")
# - track: String (e.g., "V", "A1", "S")
# - operation: String (e.g., "MUTE", "REPLACE", "INPAINT")
# - timecodes: List of timecode strings
# - metadata: Dictionary of metadata fields

for edit in edits:
    print(f"Edit {edit['edit_number']}: {edit['track']} {edit['operation']}")
    if 'description' in edit['metadata']:
        print(f"  Description: {edit['metadata']['description']}")
```

## Builder Usage

The AIEDL builder (`builder.py`) provides a programmatic interface for creating AIEDL files:

```python
from aiedl.builder import AIEDLBuilder

# Create a new AIEDL file
builder = AIEDLBuilder('output.ai.edl', 'My Movie', fps=24)

# Add a video cut
builder.add_video_cut(
    '00:00:00:00', '00:00:05:00',
    '00:00:10:00', '00:00:15:00',
    clip_name='Scene1'
)

# Add a video inpaint operation
builder.add_video_inpaint(
    '00:00:12:00', '00:00:14:00',
    region={'x1': 0.1, 'y1': 0.2, 'x2': 0.3, 'y2': 0.4},
    action='REMOVE_OBJECT',
    target='Remove unwanted object',
    strength=0.8,
    model='stable-diffusion-v2'  # Optional: specify AI model
)

# Add an audio mute
builder.add_audio_mute(
    '00:01:10:12', '00:01:12:05',
    '00:01:10:12', '00:01:12:05',
    description='Mute profanity',
    channel=2  # Optional: specific channel
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

## Validator Usage

The AIEDL validator (`validator.py`) checks files for compliance:

```bash
# Command line usage
python aiedl/validator.py <file.ai.edl>
```

```python
# Programmatic usage
from aiedl.validator import validate_file

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

## Use Cases

### Content Moderation
- Automatically mute or replace profanity in audio
- Replace inappropriate text in captions
- Hide captions during sensitive scenes

### Content Enhancement
- Remove unwanted objects from video
- Add visual elements to scenes
- Restore damaged video content

### Accessibility
- Improve caption accuracy
- Modify captions for clarity
- Ensure captions match edited audio

## Character Encoding and File Format

### Encoding
AIEDL files **MUST** be encoded in **UTF-8**. All parsers and validators should assume UTF-8 encoding.

### Line Endings
AIEDL files may use either:
- **Unix-style** (LF, `\n`) - Recommended
- **Windows-style** (CRLF, `\r\n`)

Parsers should accept both formats. Writers may choose either format, but Unix-style (LF) is recommended for cross-platform compatibility.

### File Extension
The recommended file extension is **`.ai.edl`** (e.g., `movie.ai.edl`). Alternative extensions like `.aiedl` are also acceptable.

### MIME Type
The suggested MIME type is `application/x-aiedl` (not yet registered with IANA).

### Case Sensitivity
All keywords in AIEDL files are **case-sensitive**:
- Header fields: `TITLE`, `FPS`, `AI_VERSION` (must be uppercase)
- Reel types: `AX`, `AI` (must be uppercase)
- Track types: `V`, `A1`, `S` (track letter must be uppercase)
- Operations: `C`, `INPAINT`, `MUTE`, `REPLACE`, `MODIFY` (must be uppercase)
- Metadata fields: `* FROM CLIP NAME`, `* REGION`, etc. (case-sensitive as shown)

### Whitespace
- Fields in edit lines are separated by **one or more spaces or tabs**
- Leading and trailing whitespace on lines is ignored
- Empty lines are allowed and ignored
- Comments start with `#` and continue to end of line

## Validation Rules

### Required Header Fields
In strict mode, the following header fields are **required**:
- `TITLE`: Project title (non-empty)
- `FPS`: Frame rate (must be a positive number, typically 0-120)
- `AI_VERSION`: Specification version (currently "1.0")

### Edit Number Format
- **MUST** be exactly 3 digits (001, 002, 003, etc.)
- **SHOULD** be sequential starting from 001 (non-sequential numbers generate warnings)
- **MUST** be unique within a file (duplicate numbers are invalid)

### Reel Types
Valid reel types:
- `AX`: Standard audio/video edit
- `AI`: AI-powered edit operation

### Track Types
Valid track types:
- `V`: Video track
- `A1` through `A32`: Audio tracks (A1 = first audio track)
- `S`: Subtitle/Caption track

### Operation Compatibility
Operations are only valid for specific track types:

| Operation | Valid Tracks |
|-----------|-------------|
| `C` | `V` |
| `INPAINT` | `V` |
| `MUTE` | `A1`-`A32`, `S` |
| `REPLACE` | `A1`-`A32`, `S` |
| `MODIFY` | `S` |

### Timecode Validation
Timecodes **MUST** follow the format `HH:MM:SS:FF`:
- **HH**: Hours (00-23)
- **MM**: Minutes (00-59)
- **SS**: Seconds (00-59)
- **FF**: Frames (00-29, frame limit depends on FPS)

Timecode logic constraints:
- `SOURCE_IN` **MUST** be before `SOURCE_OUT`
- `RECORD_IN` **MUST** be before `RECORD_OUT`

### INPAINT Operation Requirements
INPAINT operations **REQUIRE**:
- `REGION`: Dictionary with `x1`, `y1`, `x2`, `y2` (all values between 0.0 and 1.0)
- `ACTION`: One of `REMOVE_OBJECT`, `ADD_OBJECT`, `REPLACE_OBJECT`, `ADD_COLOR`, `RESTORE`

INPAINT operations **MAY** include:
- `TARGET`: Description of the operation goal
- `STRENGTH`: Float value between 0.0 and 1.0
- `MODEL`: AI model identifier (string) specifying which model to use for this edit
- `SEED`: Integer random seed for best-effort repeatability of generated output

### Caption Operation Requirements
- **REPLACE**: Requires `REPLACEMENT` metadata; `ORIGINAL_TEXT` is recommended
- **MODIFY**: Requires both `ORIGINAL_TEXT` and `REPLACEMENT` metadata
- **MUTE**: Requires `DESCRIPTION` metadata

### Channel Metadata
- `CHANNEL` **MUST** be a positive integer (1, 2, 3, etc.)
- Only valid for audio operations

### Region Coordinates
Region coordinates (`x1`, `y1`, `x2`, `y2`) **MUST** be:
- Float values between 0.0 and 1.0 (inclusive)
- Representing percentages of frame dimensions
- `x1` < `x2` and `y1` < `y2` (logically, though not strictly enforced)

## Error Handling

### Parser Behavior
When encountering invalid input, parsers should:
1. **Continue parsing** when possible (skip invalid lines, log warnings)
2. **Raise exceptions** for critical errors (file not found, encoding errors)
3. **Return partial results** with error information when non-critical errors occur

### Validation Errors
The validator distinguishes between:
- **Errors**: Invalid format that prevents proper parsing or violates constraints
- **Warnings**: Non-critical issues (e.g., non-sequential edit numbers, missing optional metadata)

### Common Error Scenarios

#### Invalid Timecode Format
```
Error: Invalid timecode format: 00:00:5:00. Expected HH:MM:SS:FF
```
**Resolution**: Ensure all timecodes use exactly 2 digits per component.

#### Missing Required Metadata
```
Error: INPAINT operation requires REGION metadata
```
**Resolution**: Add the required metadata field for the operation.

#### Invalid Operation for Track
```
Error: Invalid operation 'INPAINT' for track 'A1'. Valid operations: {'MUTE', 'REPLACE'}
```
**Resolution**: Use a valid operation for the specified track type.

#### Out of Range Values
```
Error: STRENGTH must be between 0.0 and 1.0, got: 1.5
```
**Resolution**: Ensure values are within valid ranges.

#### Duplicate Edit Numbers
```
Error: Duplicate edit number: 001
```
**Resolution**: Ensure each edit has a unique edit number.

### Error Recovery
Parsers should attempt to recover from errors when possible:
- Skip invalid lines and continue parsing
- Use default values for missing optional fields
- Log warnings for non-critical issues
- Return partial results with error list

### Validation Tool
Use the provided `validator.py` tool to validate AIEDL files:
```bash
python aiedl/validator.py <file.ai.edl>
```

## Best Practices

1. **Timecode Accuracy**: Ensure timecodes are frame-accurate and match the project's frame rate
2. **Descriptive Metadata**: Always include DESCRIPTION fields to explain why edits were made
3. **Consistent Numbering**: Use sequential edit numbers (001, 002, 003, etc.)
4. **Comment Clarity**: Use clear, descriptive text in metadata fields
5. **Version Control**: Track AI_VERSION to ensure compatibility with processing tools
6. **Validation**: Always validate AIEDL files before processing
7. **Encoding**: Always use UTF-8 encoding when creating or editing files

## Future Extensions

Potential future additions to the AIEDL format:
- Multi-language caption support
- Style transfer operations
- Color grading operations
- Audio enhancement operations
- Batch operation support
- Conditional edit logic

## Version History

- **1.0**: Initial specification with video, audio, and caption support

