# Music Production Client Backend

The backend can be called through 2 APIs:
1. through the `cli`
2. through REST endpoints


## Use the REST endpoints

You have to start the server:

```sh
fastapi dev src/mpcli/api.py
```

The best way to use the REST endpoints is to use a REST Client. The directory [bruno-api](../bruno-api/) provides a pre-packaged configuration.

## Use the CLI

You don't need to run the frontend to run the CLI, but the drawback is that you have to configure things in the file `config.toml`

A configuration template is provided [here](./cli-config-template.toml)

* `poetry run timestretch` will timestrech the given files to the target tempo (`target_tempo`)
* `poetry run detect_tempo` will just give the tempos of the files located in the source directory 
* `poetry run convert` 
* `poetry run normalize` 
* `poetry run tts` will synthesize speech from text, cloning the voice of a reference audio file

### Text-to-Speech (`tts`)

`poetry run tts` generates speech from text using the [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) model. It clones the timbre of a reference audio file (`voice`) and reads the provided `text` with that voice.

The generated audio is written to the `output` directory as a `.wav` file (24 kHz), named after the reference voice file with a `-gen` suffix (e.g. a reference `moonlight.wav` produces `moonlight-gen.wav`).

> **Note:** the model runs on Apple Silicon GPU (`mps`) with `float16` precision. The weights are downloaded from Hugging Face on first run.

Configuration section in `config.toml`:

```toml
[tts]

# the reference audio file whose voice will be cloned
voice = "/my/path/to/reference/voice.wav"

# the text to synthesize with the cloned voice
text = "The text that will be spoken."

# directory where the generated <voice-stem>-gen.wav file will be saved
output = "/my/path/to/output/directory"
```

| Field    | Type   | Required | Description                                                        |
| -------- | ------ | -------- | ------------------------------------------------------------------ |
| `voice`  | path   | yes      | Reference audio file whose voice is cloned                         |
| `text`   | string | yes      | Text to synthesize                                                 |
| `output` | path   | yes      | Output directory for the generated `<voice-stem>-gen.wav` file     |
