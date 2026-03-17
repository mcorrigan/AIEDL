# AIEDL C++ Implementation

C++ library for parsing, validating, and building AIEDL files.

## Building

### Using CMake

```bash
mkdir build
cd build
cmake ..
make
```

### Manual Compilation

```bash
g++ -std=c++17 -o aiedl_example example.cpp aiedl.cpp
```

## Usage

### Parsing

```cpp
#include "aiedl.h"
using namespace aiedl;

AIEDLFile file = Parser::parse("movie.ai.edl");
for (const auto& edit : file.edits) {
    std::cout << "Edit " << edit.edit_number << ": " 
              << edit.track << " " << edit.operation << "\n";
}
```

### Building

```cpp
Builder builder("output.ai.edl", "My Movie", 24.0);

Timecode source_in(0, 0, 0, 0);
Timecode source_out(0, 0, 5, 0);
Timecode record_in(0, 0, 10, 0);
Timecode record_out(0, 0, 15, 0);

builder.addVideoCut(source_in, source_out, record_in, record_out, "Scene1");

Region region(0.1, 0.2, 0.3, 0.4);
builder.addVideoInpaint(source_in, source_out, region, "REMOVE_OBJECT", "Remove object", 0.8);

// For reproducible generative output in AIEDL files, include:
// * SEED: 123456789

builder.close();
```

### Validation

```cpp
Validator validator(true);
ValidationResult result = validator.validate("movie.ai.edl");

if (result.is_valid) {
    std::cout << "File is valid!\n";
} else {
    for (const auto& error : result.errors) {
        std::cout << "Error: " << error.what() << "\n";
    }
}
```

## Requirements

- C++17 or later
- Standard library (no external dependencies)

