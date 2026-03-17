# AIEDL - AI Edit Decision List

AIEDL is an extended Edit Decision List format that supports AI-powered video, audio, and caption editing operations.

## Structure

- **`sample.ai.edl`**: Example AIEDL file demonstrating all supported operations
- **`SPECIFICATION.md`**: Complete specification and documentation
- **`python/`**: Python implementation (parser, builder, validator)
- **`cpp/`**: C++ implementation (header-only library)
- **`javascript/`**: JavaScript/TypeScript implementation (Node.js and browser)

## Implementations

### Python

```python
from aiedl.python import parse_edl_with_ai, AIEDLBuilder

# Parse
edits = parse_edl_with_ai('sample.ai.edl')

# Build
builder = AIEDLBuilder('output.ai.edl', 'My Movie', fps=24)
builder.add_audio_mute('00:01:00:00', '00:01:05:00', 
                       '00:01:00:00', '00:01:05:00',
                       description='Mute profanity')
```

See [python/README.md](python/README.md) for details.

### C++

```cpp
#include "aiedl.h"
using namespace aiedl;

// Parse
AIEDLFile file = Parser::parse("movie.ai.edl");

// Build
Builder builder("output.ai.edl", "My Movie", 24.0);
Timecode source_in(0, 0, 0, 0);
Timecode source_out(0, 0, 5, 0);
builder.addVideoCut(source_in, source_out, source_in, source_out, "Scene1");
```

See [cpp/README.md](cpp/README.md) for details.

### JavaScript

```javascript
const { Parser, Builder, Timecode } = require('./javascript/aiedl.js');

// Parse
const file = Parser.parse(content);

// Build
const builder = new Builder('output.ai.edl', 'My Movie', 24.0);
const sourceIn = new Timecode(0, 0, 0, 0);
const sourceOut = new Timecode(0, 0, 5, 0);
builder.addVideoCut(sourceIn, sourceOut, sourceIn, sourceOut, 'Scene1');
```

See [javascript/README.md](javascript/README.md) for details.

## Supported Operations

### Video
- **C**: Standard cuts and edits
- **INPAINT**: AI-powered inpainting (object removal, addition, replacement)
  - Optional metadata includes `MODEL` and `SEED` for model selection and best-effort repeatability

### Audio
- **MUTE**: Mute audio during specific time ranges
- **REPLACE**: Replace audio segments

### Captions
- **REPLACE**: Replace caption text
- **MUTE**: Hide captions during specific time ranges
- **MODIFY**: Modify caption text

## Quick Start Examples

### Python

```python
from aiedl.python import parse_edl_with_ai, AIEDLBuilder, validate_file

# Parse
edits = parse_edl_with_ai('sample.ai.edl')

# Validate
is_valid, errors, warnings = validate_file('sample.ai.edl')

# Build
builder = AIEDLBuilder('output.ai.edl', 'My Movie', fps=24)
builder.add_audio_mute('00:01:00:00', '00:01:05:00', 
                       '00:01:00:00', '00:01:05:00',
                       description='Mute profanity')
```

### C++

```cpp
#include "aiedl.h"
using namespace aiedl;

AIEDLFile file = Parser::parse("movie.ai.edl");
Validator validator(true);
ValidationResult result = validator.validate(file);
```

### JavaScript

```javascript
const { Parser, Validator } = require('./javascript/aiedl.js');

const file = Parser.parse(content);
const validator = new Validator(true);
const result = validator.validate(file);
```

## Documentation

See [SPECIFICATION.md](SPECIFICATION.md) for complete documentation including:
- File format specification
- All supported operations
- Metadata fields
- Validation rules
- Error handling
- Examples
- Best practices

