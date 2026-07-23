// Text-to-speech synthesis
// Equivalent to tts.py

from os.path import Path
from string import String
from option import Optional

from ..entities.source import AudioSource
from ..entities.exceptions import TextToSpeechError

// Sample rate for TTS audio (24 kHz)
let TTS_SAMPLE_RATE = 24000

// OmniVoice model name
let _MODEL_NAME = "k2-fsa/OmniVoice"

fn synthesize_speech(
    text: String,
    ref_audio: String,
    device: String = "cpu",
    name: Optional[String] = None,
) raises -> AudioSource:
    """
    Generate speech from text, cloning the voice of the reference audio.
    Uses OmniVoice via Python import.
    
    Args:
        text: The text to synthesize.
        ref_audio: Path to the reference audio whose voice is cloned.
        device: The device to run inference on (e.g., 'mps', 'cuda', 'cpu').
        name: Optional name for the generated audio source.
    
    Returns:
        AudioSource: The generated speech as an audio source.
    
    Raises:
        TextToSpeechError: If speech synthesis fails.
    """
    from python import Python
    from numpy import np
    
    try:
        // Import required modules
        torch = Python.import_module("torch")
        OmniVoice = Python.import_module("omnivoice").OmniVoice
        
        // Load the model
        model = OmniVoice.from_pretrained(
            _MODEL_NAME,
            device_map=device,
            dtype=torch.float16,
        )
        
        // Generate audio
        audio = model.generate(text=text, ref_audio=ref_audio)
        
        // audio is a list of numpy arrays with shape (T,) at 24 kHz
        let audio_array = audio[0]  // Get the first (and only) array
        
        // Reshape the mono signal to (frames, channels) expected by AudioSource
        let samples = audio_array.reshape(-1, 1)
        
        // Convert to Mojo tensor
        let samples_tensor = Tensor[Float32](samples)
        
        // Create AudioSource from the tensor
        return AudioSource.from_array(
            data=samples_tensor,
            audio_format=.wav,
            sample_rate=TTS_SAMPLE_RATE,
            name=name or "tts_output",
        )
    except e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}")
