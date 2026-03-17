# AIEDL JavaScript Implementation

JavaScript/TypeScript library for parsing, validating, and building AIEDL files.

## Installation

### Node.js

```bash
npm install aiedl
# or
yarn add aiedl
```

### Browser

Include the script directly:

```html
<script src="aiedl.js"></script>
```

## Usage

### Node.js / CommonJS

```javascript
const AIEDL = require('./aiedl.js');
const { Parser, Builder, Validator, Timecode, Region } = AIEDL;
```

### ES6 Modules

```javascript
import { Parser, Builder, Validator, Timecode, Region } from './aiedl.js';
```

### Browser

```javascript
// Available as window.AIEDL
const { Parser, Builder, Validator, Timecode, Region } = window.AIEDL;
```

## Examples

### Parsing

```javascript
const fs = require('fs');
const content = fs.readFileSync('movie.ai.edl', 'utf8');
const file = Parser.parse(content);

for (const edit of file.edits) {
    console.log(`Edit ${edit.edit_number}: ${edit.track} ${edit.operation}`);
}
```

### Building

```javascript
const builder = new Builder('output.ai.edl', 'My Movie', 24.0);

const sourceIn = new Timecode(0, 0, 0, 0);
const sourceOut = new Timecode(0, 0, 5, 0);
const recordIn = new Timecode(0, 0, 10, 0);
const recordOut = new Timecode(0, 0, 15, 0);

builder.addVideoCut(sourceIn, sourceOut, recordIn, recordOut, 'Scene1');

const region = new Region(0.1, 0.2, 0.3, 0.4);
builder.addVideoInpaint(sourceIn, sourceOut, region, 'REMOVE_OBJECT', 'Remove object', 0.8);

// For reproducible generative output in AIEDL files, include:
// * SEED: 123456789

// Save to file (Node.js)
builder.save((err) => {
    if (err) throw err;
    console.log('File saved!');
});

// Or get as string
const content = builder.toString();
```

### Validation

```javascript
const validator = new Validator(true);
const result = validator.validate(file);

if (result.isValid) {
    console.log('File is valid!');
} else {
    for (const error of result.errors) {
        console.log(`Error: ${error.message}`);
    }
}
```

## API

### Classes

- **Parser**: Parse AIEDL files from strings
- **Builder**: Build AIEDL files programmatically
- **Validator**: Validate AIEDL files
- **Timecode**: Represent timecodes (HH:MM:SS:FF)
- **Region**: Represent region coordinates (0.0-1.0)
- **EditMetadata**: Edit metadata container
- **Edit**: Single edit entry
- **AIEDLFile**: Complete AIEDL file structure

## Requirements

- Node.js 12+ (for file operations)
- Modern browser with ES6 support (for browser usage)

