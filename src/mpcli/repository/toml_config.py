import tomllib
from typing import TypeVar

T = TypeVar("T")


def read_configurations(config_path: str, section_name: str, entity_type: T) -> list[T]:
    """Read a TOML configuration file and returns a list of entities of type T
    contained in the section `section_name`.

    The section can be either a single entity or a list of entities.

    Example:
    ```toml
    [timestretch]
    source = "/path/to/audio/file/or/directory"
    output = "/path/to/output/directory"
    target_tempo = 120.0
    min_rate = 0.8
    max_rate = 1.2
    filename = "{{ source.stem }}_{{ tempo_min }}-{{ tempo_max }}_BPM"
    ```
    or
    ```toml
    [[timestretch]]
    source = "/path/to/audio/file/or/directory"
    output = "/path/to/output/directory"
    target_tempo = 120.0

    [[timestretch]]
    source = "/path/to/another/audio/file/or/directory"
    output = "/path/to/output/directory"
    min_rate = 0.8
    max_rate = 1.2
    filename = "{{ source.stem }}_{{ tempo_min }}-{{ tempo_max }}_BPM"
    ```
    """
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)

            if isinstance(config[section_name], list):
                configs = [entity_type(**item) for item in config[section_name]]
            else:
                configs = [entity_type(**config[section_name])]

        return configs
    except Exception as e:
        raise ValueError(f"Error reading config file '{config_path}': {e}")
