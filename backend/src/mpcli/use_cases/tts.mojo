// Text-to-speech use case
// Equivalent to tts.py

from os.path import Path
from string import String

from ..entities.result import TextToSpeechResult
from ..repository.tts import synthesize_speech

fn execute_text_to_speech(
    text: String,
    ref_audio: String,
) -> Optional[TextToSpeechResult]:
    """
    Execute text-to-speech synthesis using the voice of a reference audio.
    
    Args:
        text: The text to synthesize.
        ref_audio: Path to the reference audio file for voice cloning.
    
    Returns:
        Optional[TextToSpeechResult]: The result of the TTS, or None if it fails.
    """
    try:
        let generated_audio = synthesize_speech(
            text=text,
            ref_audio=ref_audio,
            name=Path(ref_audio).stem() + "-gen",
        )
        
        return TextToSpeechResult(
            text=text,
            ref_audio=ref_audio,
            generated_audio=generated_audio,
        )
    except e:
        print(f"Error during text-to-speech: {e}")
        return None
