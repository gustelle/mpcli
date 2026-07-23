// CLI configuration entities
// Equivalent to cli_entities.py

from os.path import Path
from string import String
from option import Optional
from list import List

from .entities.source import AudioSource
from .entities.exceptions import CLIConfigError

// Supported audio formats for CLI
enum CLIAudioFormat:
    case wav
    case mp3

struct TextToSpeechConfig:
    """Configuration for TTS command."""
    var output: String  // Output directory
    var voice: String   // Path to reference audio
    var text: String    // Text to synthesize

struct LocalAudioSource:
    """Base configuration for audio source."""
    var source: String  // Path to audio file or directory

struct CLINormalizeConfig(LocalAudioSource):
    """Configuration for normalize command."""
    var output: String  // Output directory
    var lufs: Float64 = -14.0  // Target LUFS level

struct CLITimeStretchConfig(LocalAudioSource):
    """
    Configuration for timestretch command.
    
    Controls:
    - If min_rate is provided but not max_rate, max_rate is set to 1.0.
    - If max_rate is provided but not min_rate, min_rate is set to 1.0.
    """
    var output: String  // Output directory
    var target_tempo: Optional[Float64] = None
    var min_rate: Optional[Float64] = None
    var max_rate: Optional[Float64] = None
    var filename: Optional[String] = None
    
    fn validate_config(inout self) raises:
        """Validate the configuration and set defaults."""
        if self.target_tempo is None and self.min_rate is None and self.max_rate is None:
            raise CLIConfigError(
                "Either target_tempo or min_rate/max_rate must be provided"
            )
        
        if self.target_tempo is not None and (self.min_rate is not None or self.max_rate is not None):
            raise CLIConfigError(
                "Only one of target_tempo or min_rate/max_rate can be provided"
            )
        
        if self.min_rate is not None and self.max_rate is not None and self.min_rate > self.max_rate:
            raise CLIConfigError("min_rate cannot be greater than max_rate")
        
        // Set defaults
        if self.min_rate is not None and self.max_rate is None:
            self.max_rate = 1.0
        if self.max_rate is not None and self.min_rate is None:
            self.min_rate = 1.0

struct CLIConvertConfig(LocalAudioSource):
    """Configuration for convert command."""
    var output: String  // Output directory
    var target_format: String = "wav"  // Target format (wav or mp3)

struct CLITempoEstimationConfig(LocalAudioSource):
    """Configuration for detect_tempo command."""
    pass
