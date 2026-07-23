// HTTP API for mpcli
// Equivalent to api.py

from mojo.http import Server, Request, Response, Status
from string import String
from option import Optional
from list import List

from .entities.source import AudioSource, string_to_audio_format
from .entities.result import TempoResponse, AudioResponse
from .entities.exceptions import AudioSourceError
from .use_cases.convert import execute_format_conversion
from .use_cases.normalization import execute_normalization
from .use_cases.tempo import execute_tempo_estimation
from .use_cases.timestretch import execute_timestretch

// Create the HTTP server
let app = Server()

// Helper function to create error responses
fn create_error_response(status: Status, detail: String) -> Response:
    return Response(
        body=detail,
        status=status,
        headers={"Content-Type": "text/plain"},
    )

// Helper function to create JSON responses
fn create_json_response(body: String, status: Status = Status.OK) -> Response:
    return Response(
        body=body,
        status=status,
        headers={"Content-Type": "application/json"},
    )

// Helper function to parse form data
fn parse_form_data(request: Request) -> dict[String, String]:
    let form_data = dict[String, String]()
    if request.body:
        // Simple form data parsing (for multipart/form-data, use a proper parser)
        let body_str = String(request.body)
        for part in body_str.split("&"):
            let key_value = part.split("=")
            if key_value.size() == 2:
                form_data[key_value[0]] = key_value[1]
    return form_data

// POST /convert
fn handle_convert(request: Request) -> Response:
    """Convert an audio file to another format."""
    try:
        // Parse form data and file
        let form_data = parse_form_data(request)
        let target_format = form_data.get("target_format", "wav")
        let sample_rate = Int(form_data.get("sample_rate", "44100"))
        
        // For simplicity, assume the file is sent as raw bytes in the body
        // In a real implementation, use a proper multipart parser
        let file_content = request.body
        let file_filename = form_data.get("filename", "unknown")
        let file_format = form_data.get("format", "wav")
        
        if file_content.size() == 0:
            return create_error_response(Status.BAD_REQUEST, "No file provided")
        
        // Create AudioSource
        let audio_source = AudioSource(
            audio_format=string_to_audio_format(file_format),
            audio_bytes=file_content,
            name=file_filename,
            sample_rate=sample_rate,
        )
        
        // Execute conversion
        let result = execute_format_conversion(audio_source, target_format)
        
        if result is None:
            return create_error_response(Status.INTERNAL_SERVER_ERROR, "Conversion failed")
        
        // Return the converted audio bytes
        return Response(
            body=result.converted_audio.audio_bytes.numpy().tobytes(),
            status=Status.OK,
            headers={"Content-Type": "application/octet-stream"},
        )
    except e:
        return create_error_response(Status.INTERNAL_SERVER_ERROR, f"Error: {e}")

// POST /normalize
fn handle_normalize(request: Request) -> Response:
    """Normalize the loudness of an audio file."""
    try:
        let form_data = parse_form_data(request)
        let lufs = Float64(form_data.get("lufs", "-14.0"))
        
        // Parse file
        let file_content = request.body
        let file_filename = form_data.get("filename", "unknown")
        let file_format = form_data.get("format", "wav")
        
        if file_content.size() == 0:
            return create_error_response(Status.BAD_REQUEST, "No file provided")
        
        // Create AudioSource
        let audio_source = AudioSource(
            audio_format=string_to_audio_format(file_format),
            audio_bytes=file_content,
            name=file_filename,
            sample_rate=44100,  // Default sample rate
        )
        
        // Execute normalization
        let result = execute_normalization(audio_source, lufs)
        
        if result is None:
            return create_error_response(Status.INTERNAL_SERVER_ERROR, "Normalization failed")
        
        // Return the normalized audio bytes
        return Response(
            body=result.converted_audio.audio_bytes.numpy().tobytes(),
            status=Status.OK,
            headers={"Content-Type": "application/octet-stream"},
        )
    except e:
        return create_error_response(Status.INTERNAL_SERVER_ERROR, f"Error: {e}")

// POST /timestretch
fn handle_timestretch(request: Request) -> Response:
    """Apply time stretching to an audio file."""
    try:
        let form_data = parse_form_data(request)
        let target_tempo = Optional[Float64](None)
        let min_rate = Float64(form_data.get("min_rate", "1.0"))
        let max_rate = Float64(form_data.get("max_rate", "1.0"))
        
        if form_data.contains("target_tempo"):
            target_tempo = Float64(form_data["target_tempo"])
        
        // Parse file
        let file_content = request.body
        let file_filename = form_data.get("filename", "unknown")
        let file_format = form_data.get("format", "wav")
        
        if file_content.size() == 0:
            return create_error_response(Status.BAD_REQUEST, "No file provided")
        
        // Create AudioSource
        let audio_source = AudioSource(
            audio_format=string_to_audio_format(file_format),
            audio_bytes=file_content,
            name=file_filename,
            sample_rate=44100,  // Default sample rate
        )
        
        // Execute time stretching
        let result = execute_timestretch(
            audio_source,
            target_tempo=target_tempo,
            min_rate=min_rate,
            max_rate=max_rate,
        )
        
        if result is None:
            return create_error_response(Status.INTERNAL_SERVER_ERROR, "Time stretching failed")
        
        // Return the time-stretched audio bytes
        return Response(
            body=result.converted_audio.audio_bytes.numpy().tobytes(),
            status=Status.OK,
            headers={"Content-Type": "application/octet-stream"},
        )
    except e:
        return create_error_response(Status.INTERNAL_SERVER_ERROR, f"Error: {e}")

// POST /tempo
fn handle_tempo(request: Request) -> Response:
    """Estimate the tempo of an audio file."""
    try:
        // Parse file
        let file_content = request.body
        let file_filename = request.headers.get("filename", "unknown")
        let file_format = request.headers.get("format", "wav")
        
        if file_content.size() == 0:
            return create_error_response(Status.BAD_REQUEST, "No file provided")
        
        // Create AudioSource
        let audio_source = AudioSource(
            audio_format=string_to_audio_format(file_format),
            audio_bytes=file_content,
            name=file_filename,
            sample_rate=44100,  // Default sample rate
        )
        
        // Execute tempo estimation
        let result = execute_tempo_estimation(audio_source)
        
        if result is None:
            return create_error_response(Status.INTERNAL_SERVER_ERROR, "Tempo estimation failed")
        
        // Create JSON response
        let response_body = f'{{' +
            f'"source_name": "{result.audio_source.name}", ' +
            f'"source_format": "{result.audio_source.get_format_string()}", ' +
            f'"tempo": {result.tempo}' +
            f'}}'
        
        return create_json_response(response_body)
    except e:
        return create_error_response(Status.INTERNAL_SERVER_ERROR, f"Error: {e}")

// Register routes
app.route("POST", "/convert", handle_convert)
app.route("POST", "/normalize", handle_normalize)
app.route("POST", "/timestretch", handle_timestretch)
app.route("POST", "/tempo", handle_tempo)

fn main():
    """Start the HTTP server."""
    let port = 8000
    print(f"Starting mpcli API server on port {port}...")
    app.serve(port=port)

if __name__ == "__main__":
    main()
