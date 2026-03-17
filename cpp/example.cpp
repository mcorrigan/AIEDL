/**
 * Example usage of AIEDL C++ library
 */

#include "aiedl.h"
#include <iostream>

using namespace aiedl;

int main() {
    try {
        // Create a new AIEDL file
        Builder builder("example.ai.edl", "Example Movie", 24.0);
        
        // Add a video cut
        Timecode source_in(0, 0, 0, 0);
        Timecode source_out(0, 0, 5, 0);
        Timecode record_in(0, 0, 10, 0);
        Timecode record_out(0, 0, 15, 0);
        
        builder.addVideoCut(source_in, source_out, record_in, record_out, "Scene1");
        
        // Add a video inpaint
        Timecode inpaint_in(0, 0, 12, 0);
        Timecode inpaint_out(0, 0, 14, 0);
        Region region(0.1, 0.2, 0.3, 0.4);
        
        builder.addVideoInpaint(inpaint_in, inpaint_out, region, "REMOVE_OBJECT", "Remove chair", 0.8);
        // For reproducible generative output, add "* SEED: <integer>" to the INPAINT metadata.
        
        // Add an audio mute
        Timecode mute_in(0, 1, 10, 12);
        Timecode mute_out(0, 1, 12, 5);
        
        builder.addAudioMute(mute_in, mute_out, mute_in, mute_out, "Mute profanity");
        
        // Add a caption replace
        Timecode caption_in(0, 3, 0, 0);
        Timecode caption_out(0, 3, 5, 0);
        
        builder.addCaptionReplace(caption_in, caption_out, caption_in, caption_out,
                                  "\"What the hell?\"", "\"What?\"", "Remove profanity");
        
        builder.close();
        
        std::cout << "Created example.ai.edl\n";
        
        // Parse and validate
        AIEDLFile file = Parser::parse("example.ai.edl");
        Validator validator(true);
        ValidationResult result = validator.validate(file);
        
        if (result.is_valid) {
            std::cout << "File is valid!\n";
            std::cout << "Found " << file.edits.size() << " edits\n";
        } else {
            std::cout << "Validation failed:\n";
            for (const auto& error : result.errors) {
                std::cout << "  Error: " << error.what() << "\n";
            }
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}

