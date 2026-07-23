// Command-line interface for mpcli
// Equivalent to cli.py

from os import args, getenv
from os.path import Path, exists, join, stem
from string import String, format
from list import List
from option import Optional

from .entities.source import AudioSource
from .entities.result import TempoResult, TimeStretchResult, ConvertResult, NormalizeResult, TextToSpeechResult
from .entities.exceptions import CLIConfigError, AudioSourceError
from .repository.audio_file import iter_sources, save_audio_file
from .repository.toml_config import read_configurations
from .use_cases.convert import execute_format_conversion
from .use_cases.normalization import execute_normalization
from .use_cases.tempo import execute_tempo_estimation
from .use_cases.timestretch import execute_timestretch
from .use_cases.tts import execute_text_to_speech
from .cli_entities import (
    TextToSpeechConfig,
    LocalAudioSource,
    CLINormalizeConfig,
    CLITimeStretchConfig,
    CLIConvertConfig,
    CLITempoEstimationConfig,
)

// Configuration file name
let CONFIG_FILE = "cli-config.toml"

fn _timestretched_filename(config: CLITimeStretchConfig, tempo: Float64) -> String:
    """Generate the output filename for time-stretched audio."""
    let tempo_min = (tempo * config.min_rate).round(2)
    let tempo_max = (tempo * config.max_rate).round(2)
    
    if config.filename is not None:
        return config.filename
    elif tempo_min == tempo_max:
        return format("{stem}_{tempo_min}_BPM", stem=Path(config.source).stem(), tempo_min=tempo_min)
    else:
        return format("{stem}_{tempo_min}-{tempo_max}_BPM", stem=Path(config.source).stem(), tempo_min=tempo_min, tempo_max=tempo_max)

fn _print_tempo_table(results: List[tuple[String, Float64]]):
    """Print tempo detection results as a table."""
    print("Tempo Detection Results")
    print("-" * 40)
    print("Source\t\tTempo")
    print("-" * 40)
    for (source_name, tempo) in results:
        print(f"{source_name}\t\t{tempo} BPM")

fn _print_timestretch_table(results: List[tuple[String, String, Float64]]):
    """Print time-stretching results as a table."""
    print("Time Stretching Results")
    print("-" * 60)
    print("Source\t\tTarget\t\tBPM")
    print("-" * 60)
    for (source, target, bpm) in results:
        print(f"{source}\t\t{target}\t\t{bpm}")

fn _print_convert_table(results: List[tuple[String, String, String, String]]):
    """Print format conversion results as a table."""
    print("Format Conversion Results")
    print("-" * 80)
    print("Source Name\t\tSource Format\t\tTarget Name\t\tTarget Format")
    print("-" * 80)
    for (src_name, src_format, tgt_name, tgt_format) in results:
        print(f"{src_name}\t\t{src_format}\t\t{tgt_name}\t\t{tgt_format}")

fn _print_normalize_table(results: List[tuple[String, Float64, String]]):
    """Print normalization results as a table."""
    print("Normalization Results")
    print("-" * 60)
    print("Source Name\t\tLUFS\t\tTarget Name")
    print("-" * 60)
    for (src_name, lufs, tgt_name) in results:
        print(f"{src_name}\t\t{lufs}\t\t{tgt_name}")

fn _print_tts_table(results: List[tuple[String, String, String]]):
    """Print TTS results as a table."""
    print("Text-to-Speech Results")
    print("-" * 60)
    print("Voice\t\tText\t\tTarget Name")
    print("-" * 60)
    for (voice, text, tgt_name) in results:
        print(f"{voice}\t\t{text}\t\t{tgt_name}")

fn _print_info(file_path: String, file_type: String, extension: String, mime: String):
    """Print file info."""
    print(f"File: {file_path}")
    print(f"Type: {file_type}")
    print(f"Extension: {extension}")
    print(f"Mime: {mime}")
    print("-" * 20)

fn detect_tempo():
    """Estimate the tempo of audio files."""
    let results = List[tuple[String, Float64]]()
    
    try:
        let configs = read_configurations[CLITempoEstimationConfig](CONFIG_FILE, "detect_tempo", CLITempoEstimationConfig)
        
        for config in configs:
            for audio in iter_sources(config.source):
                try:
                    let result = execute_tempo_estimation(audio)
                    if result is not None:
                        results.append((result.audio_source.name, result.tempo))
                except e:
                    print(f"Error processing {audio.name}: {e}")
        
        _print_tempo_table(results)
    except e:
        print(f"Error during tempo detection: {e}")

fn timestretch():
    """Apply time stretching to audio files."""
    let results = List[tuple[String, String, Float64]]()
    
    try:
        let configs = read_configurations[CLITimeStretchConfig](CONFIG_FILE, "timestretch", CLITimeStretchConfig)
        
        for mut config in configs:
            config.validate_config()
            
            for source in iter_sources(config.source):
                try:
                    let result = execute_timestretch(
                        source=source,
                        target_tempo=config.target_tempo,
                        min_rate=config.min_rate,
                        max_rate=config.max_rate,
                    )
                    
                    if result is not None:
                        // Save the time-stretched audio
                        let filename = _timestretched_filename(config, result.original_tempo)
                        let sound_file = save_audio_file(
                            output_dir=config.output,
                            filename=filename,
                            data=result.converted_audio.to_array(),
                            sample_rate=result.converted_audio.sample_rate,
                            format=result.converted_audio.audio_format,
                        )
                        results.append((config.source, sound_file.name, result.target_tempo))
                except e:
                    print(f"Error processing {source.name}: {e}")
        
        _print_timestretch_table(results)
    except e:
        print(f"Configuration error: {e}")

fn convert():
    """Convert audio files to another format."""
    let results = List[tuple[String, String, String, String]]()
    
    try:
        let configs = read_configurations[CLIConvertConfig](CONFIG_FILE, "convert", CLIConvertConfig)
        
        for config in configs:
            for source in iter_sources(config.source):
                let result = execute_format_conversion(source, config.target_format)
                
                if result is not None:
                    // Save the converted audio
                    let converted_array = result.converted_audio.to_array()
                    let saved_source = save_audio_file(
                        output_dir=config.output,
                        filename=result.converted_audio.name,
                        data=converted_array,
                        sample_rate=result.converted_audio.sample_rate,
                        format=result.converted_audio.audio_format,
                    )
                    results.append((
                        result.audio_source.name,
                        result.audio_source.get_format_string(),
                        saved_source.name,
                        saved_source.get_format_string(),
                    ))
        
        _print_convert_table(results)
    except e:
        print(f"Error during conversion: {e}")

fn normalize():
    """Normalize the loudness of audio files."""
    let results = List[tuple[String, Float64, String]]()
    
    try:
        let configs = read_configurations[CLINormalizeConfig](CONFIG_FILE, "normalize", CLINormalizeConfig)
        
        for config in configs:
            for source in iter_sources(config.source):
                let result = execute_normalization(source, config.lufs)
                
                if result is not None:
                    // Save the normalized audio
                    let saved_source = save_audio_file(
                        output_dir=config.output,
                        filename=result.converted_audio.name,
                        data=result.converted_audio.to_array(),
                        sample_rate=result.converted_audio.sample_rate,
                        format=result.converted_audio.audio_format,
                    )
                    results.append((
                        result.audio_source.name,
                        result.lufs,
                        saved_source.name,
                    ))
        
        _print_normalize_table(results)
    except e:
        print(f"Error during normalization: {e}")

fn info():
    """Display information about audio files."""
    try:
        let configs = read_configurations[LocalAudioSource](CONFIG_FILE, "info", LocalAudioSource)
        
        for config in configs:
            from python import Python
            fleep = Python.import_module("fleep")
            
            with open(config.source, "rb") as file:
                let info = fleep.get(file.read(128))
                _print_info(
                    config.source,
                    info.type,
                    info.extension,
                    info.mime,
                )
    except e:
        print(f"Error during info: {e}")

fn tts():
    """Generate speech from text, cloning the voice of a reference audio."""
    let results = List[tuple[String, String, String]]()
    
    try:
        let configs = read_configurations[TextToSpeechConfig](CONFIG_FILE, "tts", TextToSpeechConfig)
        
        for config in configs:
            let result = execute_text_to_speech(text=config.text, ref_audio=config.voice)
            
            if result is not None:
                // Save the generated audio
                let sound_file = save_audio_file(
                    output_dir=config.output,
                    filename=result.generated_audio.name,
                    data=result.generated_audio.to_array(),
                    sample_rate=result.generated_audio.sample_rate,
                    format=result.generated_audio.audio_format,
                )
                results.append((
                    config.voice,
                    result.text,
                    sound_file.name,
                ))
        
        _print_tts_table(results)
    except e:
        print(f"Error during TTS: {e}")

fn print_usage():
    """Print CLI usage information."""
    print("mpcli - Audio processing CLI")
    print("-" * 40)
    print("Usage: mojo cli.mojo <command> [options]")
    print("\nCommands:")
    print("  detect_tempo   Estimate the tempo of audio files")
    print("  timestretch    Apply time stretching to audio files")
    print("  convert        Convert audio files to another format")
    print("  normalize      Normalize the loudness of audio files")
    print("  info           Display information about audio files")
    print("  tts            Generate speech from text")
    print("  help           Show this help message")
    print("\nNote: Configuration is read from 'cli-config.toml'")

fn main():
    """Main entry point for the CLI."""
    if args.size() < 2:
        print_usage()
        return
    
    let command = args[1]
    
    match command:
        case "detect_tempo":
            detect_tempo()
        case "timestretch":
            timestretch()
        case "convert":
            convert()
        case "normalize":
            normalize()
        case "info":
            info()
        case "tts":
            tts()
        case "help":
            print_usage()
        case _:
            print(f"Unknown command: {command}")
            print_usage()

if __name__ == "__main__":
    main()
