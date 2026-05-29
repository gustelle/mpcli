from pathlib import Path
from typing import Optional

import torch
from loguru import logger
from omnivoice import OmniVoice

from src.mpcli.entities.source import AudioSource
from src.mpcli.repository.exceptions import TextToSpeechError

# the OmniVoice model generates audio as a list of np.ndarray with shape (T,) at 24 kHz
TTS_SAMPLE_RATE = 24000

_MODEL_NAME = "k2-fsa/OmniVoice"


def synthesize_speech(
    text: str,
    ref_audio: Path,
    device: str = "mps",
    name: Optional[str] = None,
) -> AudioSource:
    """Generate speech from text, cloning the voice of the reference audio.

    Args:
        text (str): The text to synthesize.
        ref_audio (Path): Path to the reference audio whose voice is cloned.
        device (str): The device to run inference on (e.g. 'mps', 'cuda', 'cpu').
        name (Optional[str]): Optional name for the generated audio source.

    Returns:
        AudioSource: The generated speech as an audio source.
    """
    try:
        model = OmniVoice.from_pretrained(
            _MODEL_NAME, device_map=device, dtype=torch.float16
        )

        # audio is a list of `np.ndarray` with shape (T,) at 24 kHz
        audio = model.generate(text=text, ref_audio=str(ref_audio))

        # reshape the mono signal to (frames, channels) expected by AudioSource
        samples = audio[0].reshape(-1, 1)

        logger.info(f"Generated {samples.shape[0]} samples from reference '{ref_audio}'")

        return AudioSource.from_array(
            data=samples,
            audio_format="wav",
            sample_rate=TTS_SAMPLE_RATE,
            name=name,
        )
    except Exception as e:
        raise TextToSpeechError(f"Error during text-to-speech generation: {e}") from e
