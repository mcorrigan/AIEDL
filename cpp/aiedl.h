/**
 * AIEDL (AI Edit Decision List) C++ Parser and Builder
 * 
 * Header file for AIEDL C++ implementation
 */

#ifndef AIEDL_H
#define AIEDL_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <stdexcept>

namespace aiedl {

// Forward declarations
struct Timecode;
struct Region;
struct EditMetadata;
struct Edit;
struct AIEDLFile;

/**
 * Timecode structure (HH:MM:SS:FF)
 */
struct Timecode {
    int hours;
    int minutes;
    int seconds;
    int frames;
    
    Timecode() : hours(0), minutes(0), seconds(0), frames(0) {}
    Timecode(int h, int m, int s, int f) : hours(h), minutes(m), seconds(s), frames(f) {}
    
    std::string toString() const;
    static Timecode fromString(const std::string& str);
    bool isValid() const;
};

/**
 * Region coordinates (0.0-1.0)
 */
struct Region {
    double x1, y1, x2, y2;
    
    Region() : x1(0), y1(0), x2(0), y2(0) {}
    Region(double x1, double y1, double x2, double y2) : x1(x1), y1(y1), x2(x2), y2(y2) {}
    
    bool isValid() const;
};

/**
 * Edit metadata
 */
struct EditMetadata {
    std::string from_clip_name;
    Region region;
    std::string action;
    std::string target;
    double strength;
    std::string replacement;
    std::string original_text;
    std::string description;
    int channel;
    std::string model;
    
    EditMetadata() : strength(0.0), channel(0) {}
    
    bool hasRegion() const { return region.isValid(); }
    bool hasStrength() const { return strength > 0.0; }
    bool hasChannel() const { return channel > 0; }
    bool hasModel() const { return !model.empty(); }
};

/**
 * Edit entry
 */
struct Edit {
    std::string edit_number;  // 3-digit string
    std::string reel;          // "AX" or "AI"
    std::string track;         // "V", "A1", "S", etc.
    std::string operation;     // "C", "INPAINT", "MUTE", etc.
    std::vector<Timecode> timecodes;
    EditMetadata metadata;
    
    Edit() {}
};

/**
 * AIEDL file structure
 */
struct AIEDLFile {
    std::string title;
    double fps;
    std::string ai_version;
    std::vector<Edit> edits;
    
    AIEDLFile() : fps(24.0), ai_version("1.0") {}
};

/**
 * Parser class
 */
class Parser {
public:
    static AIEDLFile parse(const std::string& filename);
    static AIEDLFile parseFromString(const std::string& content);
    
private:
    static void parseHeader(const std::vector<std::string>& lines, AIEDLFile& file);
    static Edit parseEditLine(const std::string& line);
    static void parseMetadata(const std::vector<std::string>& lines, size_t& index, EditMetadata& metadata);
    static Region parseRegion(const std::string& str);
};

/**
 * Builder class
 */
class Builder {
public:
    Builder(const std::string& filename, const std::string& title, double fps = 24.0, const std::string& ai_version = "1.0");
    ~Builder();
    
    int addVideoCut(const Timecode& source_in, const Timecode& source_out,
                   const Timecode& record_in, const Timecode& record_out,
                   const std::string& clip_name = "");
    
    int addVideoInpaint(const Timecode& source_in, const Timecode& source_out,
                       const Region& region, const std::string& action,
                       const std::string& target = "", double strength = 0.0,
                       const std::string& model = "");
    
    int addAudioMute(const Timecode& source_in, const Timecode& source_out,
                    const Timecode& record_in, const Timecode& record_out,
                    const std::string& description, int channel = 0, const std::string& track = "A1");
    
    int addAudioReplace(const Timecode& source_in, const Timecode& source_out,
                       const Timecode& record_in, const Timecode& record_out,
                       const std::string& replacement, const std::string& description,
                       const std::string& track = "A1");
    
    int addCaptionReplace(const Timecode& source_in, const Timecode& source_out,
                         const Timecode& record_in, const Timecode& record_out,
                         const std::string& original_text, const std::string& replacement,
                         const std::string& description);
    
    int addCaptionMute(const Timecode& source_in, const Timecode& source_out,
                      const Timecode& record_in, const Timecode& record_out,
                      const std::string& description);
    
    int addCaptionModify(const Timecode& source_in, const Timecode& source_out,
                        const Timecode& record_in, const Timecode& record_out,
                        const std::string& original_text, const std::string& replacement,
                        const std::string& description);
    
    void close();
    
private:
    std::string filename_;
    std::string title_;
    double fps_;
    std::string ai_version_;
    int edit_counter_;
    std::vector<Edit> edits_;
    
    void writeHeader();
    void writeEdit(const Edit& edit);
    int getNextEditNumber();
};

/**
 * Validator class
 */
class ValidationError : public std::runtime_error {
public:
    ValidationError(const std::string& message, int line_number = -1)
        : std::runtime_error(message), line_number_(line_number) {}
    
    int lineNumber() const { return line_number_; }
    
private:
    int line_number_;
};

struct ValidationResult {
    bool is_valid;
    std::vector<ValidationError> errors;
    std::vector<std::string> warnings;
    
    ValidationResult() : is_valid(true) {}
};

class Validator {
public:
    Validator(bool strict = true) : strict_(strict) {}
    
    ValidationResult validate(const std::string& filename);
    ValidationResult validate(const AIEDLFile& file);
    
private:
    bool strict_;
    ValidationResult result_;
    
    void validateHeader(const AIEDLFile& file);
    void validateEdit(const Edit& edit, size_t index);
    void validateTimecode(const Timecode& tc);
    void validateMetadata(const Edit& edit);
    bool isValidReel(const std::string& reel) const;
    bool isValidTrack(const std::string& track) const;
    bool isValidOperation(const std::string& operation, const std::string& track) const;
};

} // namespace aiedl

#endif // AIEDL_H

