// Tempo estimation
// Equivalent to tempo.py

from io import BytesIO
from python import Python

from ..entities.source import AudioSource
from ..entities.result import TempoResult
from ..entities.exceptions import AudioTransformError

fn estimate_tempo(source: AudioSource) raises -> TempoResult:
    """
    Estimate the tempo of an audio signal in beats per minute (BPM).
    Uses tempocnn via Python import.
    
    Args:
        source: The audio source.
    
    Returns:
        TempoResult: The estimated tempo result.
    
    Raises:
        AudioTransformError: If tempo estimation fails.
    """
    try:
        // Import tempocnn modules
        classifier_module = Python.import_module("tempocnn.classifier")
        feature_module = Python.import_module("tempocnn.feature")
        
        TempoClassifier = classifier_module.TempoClassifier
        read_features = feature_module.read_features
        
        // Initialize the model
        classifier = TempoClassifier("cnn")
        
        // Read features from audio bytes
        features = read_features(BytesIO(source.audio_bytes.numpy()), zero_pad=True)
        
        // Estimate the global tempo
        tempo = classifier.estimate_tempo(features, interpolate=True)
        
        return TempoResult(
            audio_source=source,
            tempo=Float64(tempo),
        )
    except e:
        raise AudioTransformError(f"Error estimating tempo for {source.name}: {e}")
