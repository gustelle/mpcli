// Result entities for mpcli operations
// Equivalent to result.py

from .source import AudioSource
from .exceptions import AudioSourceError

struct TempoResult:
    """
    Result of a tempo estimation operation.
    Equivalent to TempoResult in result.py.
    """
    var tempo: Float64
    var audio_source: AudioSource
    
    fn __init__(inout self, tempo: Float64, audio_source: AudioSource):
        """
        Initialize a TempoResult instance.
        
        Args:
            tempo: Estimated tempo in BPM.
            audio_source: The audio source for which the tempo was estimated.
        """
        self.tempo = tempo
        self.audio_source = audio_source

struct TimeStretchResult:
    """
    Result of a time-stretching operation.
    Equivalent to TimeStretchResult in result.py.
    """
    var audio_source: AudioSource
    var converted_audio: AudioSource
    var original_tempo: Float64
    var target_tempo: Float64
    
    fn __init__(
        inout self,
        audio_source: AudioSource,
        converted_audio: AudioSource,
        original_tempo: Float64,
        target_tempo: Float64,
    ):
        """
        Initialize a TimeStretchResult instance.
        
        Args:
            audio_source: The original audio source.
            converted_audio: The time-stretched audio.
            original_tempo: Tempo of the original audio in BPM.
            target_tempo: Target tempo in BPM.
        """
        self.audio_source = audio_source
        self.converted_audio = converted_audio
        self.original_tempo = original_tempo
        self.target_tempo = target_tempo

struct ConvertResult:
    """
    Result of a format conversion operation.
    Equivalent to ConvertResult in result.py.
    """
    var audio_source: AudioSource
    var converted_audio: AudioSource
    
    fn __init__(inout self, audio_source: AudioSource, converted_audio: AudioSource):
        """
        Initialize a ConvertResult instance.
        
        Args:
            audio_source: The original audio source.
            converted_audio: The converted audio.
        """
        self.audio_source = audio_source
        self.converted_audio = converted_audio

struct NormalizeResult:
    """
    Result of a loudness normalization operation.
    Equivalent to NormalizeResult in result.py.
    """
    var audio_source: AudioSource
    var converted_audio: AudioSource
    var lufs: Float64
    
    fn __init__(
        inout self,
        audio_source: AudioSource,
        converted_audio: AudioSource,
        lufs: Float64,
    ):
        """
        Initialize a NormalizeResult instance.
        
        Args:
            audio_source: The original audio source.
            converted_audio: The normalized audio.
            lufs: Target LUFS level.
        """
        self.audio_source = audio_source
        self.converted_audio = converted_audio
        self.lufs = lufs

struct TextToSpeechResult:
    """
    Result of a text-to-speech operation.
    Equivalent to TextToSpeechResult in result.py.
    """
    var text: String
    var ref_audio: String
    var generated_audio: AudioSource
    
    fn __init__(
        inout self,
        text: String,
        ref_audio: String,
        generated_audio: AudioSource,
    ):
        """
        Initialize a TextToSpeechResult instance.
        
        Args:
            text: The input text that was synthesized.
            ref_audio: Path to the reference audio file used for voice cloning.
            generated_audio: The generated audio.
        """
        self.text = text
        self.ref_audio = ref_audio
        self.generated_audio = generated_audio
